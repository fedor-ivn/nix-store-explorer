from pathlib import Path
import shutil
import pytest
from unittest.mock import patch
import store.logic as logic


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


def test_get_paths(store):
    Path("stores/nix/store").mkdir(parents=True)
    Path("stores/nix/store/file1").touch(exist_ok=True)
    Path("stores/nix/store/file2").touch(exist_ok=True)

    paths = logic.get_paths(store)
    assert paths == {"/nix/store/file1", "/nix/store/file2"}


def test_install_package(store):
    package_name = "package_name"

    with patch("store.logic.run") as mock_run:
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


def test_remove_package(store):
    package_name = "package_name"

    with patch("store.logic.run") as mock_run:
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


def test_remove_package_error(store):
    package_name = "package_name"

    with patch("store.logic.run") as mock_run:
        mock_run.return_value.stderr = "error"
        with pytest.raises(Exception):
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


def test_check_paths_are_valid(store):
    with pytest.raises(Exception):
        logic._check_paths_are_valid([{"valid": False}], "package_name")


def test_get_closure_size(store):
    with patch("store.logic.run") as mock_run:
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
    with patch("store.logic.run") as mock_run:
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

        assert output == {"path1", "path2"}
