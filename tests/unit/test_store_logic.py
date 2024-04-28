import shutil
from pathlib import Path
from subprocess import CalledProcessError
from unittest.mock import patch

import pytest

import src.logic.core as logic
from src.logic.exceptions import (
    AttributeNotProvidedException,
    BrokenPackageException,
    InsecurePackageException,
    NotAvailableOnHostPlatformException,
    PackageNotInstalledException,
    StillAliveException,
    UnfreeLicenceException,
)


@pytest.fixture
def store():
    store = Path("stores")
    store.mkdir()
    yield store
    shutil.rmtree("stores", ignore_errors=True)


def test_create_store(store):
    path = store / "store"
    logic.create_store(path)
    assert path.exists()


def test_remove_store(store):
    logic.remove_store(store)
    assert not store.exists()


def test_remove_store_permission_error(store):
    path = store / "store"
    path.mkdir()

    path.chmod(0o444)
    logic.remove_store(path)
    assert not path.exists()


def test_remove_store_no_store(store):
    path = store / "store"
    with pytest.raises(FileNotFoundError):
        logic.remove_store(path)


def test_get_paths(store):
    Path("stores/nix/store").mkdir(parents=True)
    Path("stores/nix/store/file1").touch(exist_ok=True)
    Path("stores/nix/store/file2").touch(exist_ok=True)

    paths = logic.get_paths(store)
    assert paths == {"/nix/store/file1", "/nix/store/file2"}


def test_install_package(store):
    package_name = "package_name"

    with patch("src.logic.core.run") as mock_run:
        mock_run.return_value.stdout = '[{"outputs": {"out": "path"}}]'
        path = logic.install_package(store, package_name)
        assert path == "path"
        mock_run.assert_called_with(
            [
                "nix",
                "build",
                "--json",
                "--no-link",
                "--store",
                str(store),
                f"nixpkgs#{package_name}",
            ],
            capture_output=True,
            text=True,
        )


def test_install_package_called_process_error(store):
    package_name = "package_name"

    with patch("src.logic.core.run") as mock_run:
        mock_error = CalledProcessError(1, "cmd")
        mock_run.return_value.check_returncode.side_effect = mock_error

        with pytest.raises(CalledProcessError):
            logic.install_package(store, package_name)


def test_install_package_unfree_licence(store):
    package_name = "package_name"

    with patch("src.logic.core.run") as mock_run:
        mock_error = CalledProcessError(1, "cmd")
        mock_run.return_value.check_returncode.side_effect = mock_error
        mock_run.return_value.stderr = (
            "has an unfree license (‘unfree’), refusing to evaluate."
        )

        with pytest.raises(UnfreeLicenceException):
            logic.install_package(store, package_name)


def test_install_package_not_available_on_host_platform(store):
    package_name = "package_name"

    with patch("src.logic.core.run") as mock_run:
        mock_error = CalledProcessError(1, "cmd")
        mock_run.return_value.check_returncode.side_effect = mock_error
        mock_run.return_value.stderr = "is not available on the requested hostPlatform"

        with pytest.raises(NotAvailableOnHostPlatformException):
            logic.install_package(store, package_name)


def test_install_package_attribute_not_provided(store):
    package_name = "package_name"

    with patch("src.logic.core.run") as mock_run:
        mock_error = CalledProcessError(1, "cmd")
        mock_run.return_value.check_returncode.side_effect = mock_error
        mock_run.return_value.stderr = "does not provide attribute"

        with pytest.raises(AttributeNotProvidedException):
            logic.install_package(store, package_name)


def test_install_package_broken_package(store):
    package_name = "package_name"

    with patch("src.logic.core.run") as mock_run:
        mock_error = CalledProcessError(1, "cmd")
        mock_run.return_value.check_returncode.side_effect = mock_error
        mock_run.return_value.stderr = "is marked as broken, refusing to evaluate."

        with pytest.raises(BrokenPackageException):
            logic.install_package(store, package_name)


def test_install_package_insecure_package(store):
    package_name = "package_name"

    with patch("src.logic.core.run") as mock_run:
        mock_error = CalledProcessError(1, "cmd")
        mock_run.return_value.check_returncode.side_effect = mock_error
        mock_run.return_value.stderr = "is marked as insecure, refusing to evaluate."

        with pytest.raises(InsecurePackageException):
            logic.install_package(store, package_name)


def test_remove_package(store):
    package_name = "package_name"

    with patch("src.logic.core.run") as mock_run:
        mock_run.return_value.stderr = False
        logic.remove_package(store, package_name)
        mock_run.assert_called_with(
            [
                "nix",
                "store",
                "delete",
                "--store",
                str(store),
                f"nixpkgs#{package_name}",
            ],
            capture_output=True,
            text=True,
        )


def test_remove_package_still_alive(store):
    package_name = "package_name"

    with patch("src.logic.core._run_nix") as mock_run:
        mock_error = CalledProcessError(1, "cmd")
        mock_run.return_value.check_returncode.side_effect = mock_error
        mock_run.return_value.stderr = "since it is still alive."

        with pytest.raises(StillAliveException):
            logic.remove_package(store, package_name)

        mock_run.assert_called_with(
            "store",
            "delete",
            "--store",
            str(store),
            f"nixpkgs#{package_name}",
        )


def test_remove_package_exception(store):
    package_name = "package_name"

    with patch("src.logic.core._run_nix") as mock_run:
        mock_error = CalledProcessError(1, "cmd")
        mock_run.return_value.check_returncode.side_effect = mock_error
        mock_run.return_value.stderr = "error"

        with pytest.raises(Exception):
            logic.remove_package(store, package_name)

        mock_run.assert_called_with(
            "store",
            "delete",
            "--store",
            str(store),
            f"nixpkgs#{package_name}",
        )


def test_check_paths_are_not_valid(store):
    with pytest.raises(PackageNotInstalledException):
        logic._check_paths_are_valid([{"valid": False}])


def test_check_paths_are_valid(store):
    logic._check_paths_are_valid([{"valid": True}])


def test_get_closure_size(store):
    with patch("src.logic.core.run") as mock_run:
        mock_run.return_value.stdout = (
            '[{"closureSize": 1, "valid": true}, {"closureSize": 1, "valid": true}]'
        )
        output = logic.get_closure_size(store, "package_name")
        mock_run.assert_called_with(
            [
                "nix",
                "path-info",
                "--json",
                "--store",
                str(store),
                "--closure-size",
                "nixpkgs#package_name",
            ],
            capture_output=True,
            text=True,
        )

        assert output == 2


def test_get_closure(store):
    with patch("src.logic.core.run") as mock_run:
        mock_run.return_value.stdout = (
            '[{"path": "path1", "valid": true}, {"path": "path2", "valid": true}]'
        )
        output = logic.get_closure(store, "package_name")
        mock_run.assert_called_with(
            [
                "nix",
                "path-info",
                "--json",
                "--store",
                str(store),
                "--recursive",
                "nixpkgs#package_name",
            ],
            capture_output=True,
            text=True,
        )

        assert set(output) == {"path1", "path2"}
