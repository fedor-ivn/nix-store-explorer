import json
import os
from pathlib import Path
from shutil import rmtree
from subprocess import CalledProcessError, run  # nosec import_subprocess

from src.logic.exceptions import (
    AttributeNotProvidedException,
    BrokenPackageException,
    InsecurePackageException,
    NotAvailableOnHostPlatformException,
    PackageNotInstalledException,
    StillAliveException,
    UnfreeLicenceException,
    StoreFolderDoesNotExistException,
)


def _run_nix(*args: str):
    return run(  # nosec subprocess_without_shell_equals_true
        ["nix"] + list(args),
        capture_output=True,
        text=True,
    )


def create_store(store: Path):
    store.mkdir(parents=True)


def remove_store(store: Path):
    def handle_permission_error(function, path, excinfo):
        exception_type, error, _ = excinfo
        if exception_type != PermissionError:
            raise error

        Path(path).parent.chmod(0o755)
        function(path)

    rmtree(store, onerror=handle_permission_error)


def get_paths(store: Path):
    try:
        return set(
            f"/nix/store/{path.name}"
            for path in (store / "nix/store").iterdir()
            if path.name != ".links"
        )
    except FileNotFoundError:
        if os.path.exists(store):
            return set()
        else:
            raise StoreFolderDoesNotExistException()


def install_package(store: Path, package_name: str):
    process = _run_nix(
        "build",
        "--json",
        "--no-link",
        "--store",
        str(store),
        f"nixpkgs#{package_name}",
    )
    try:
        process.check_returncode()
    except CalledProcessError as exception:
        if "is marked as insecure, refusing to evaluate." in process.stderr:
            raise InsecurePackageException()
        elif "is marked as broken, refusing to evaluate." in process.stderr:
            raise BrokenPackageException()
        elif "is not available on the requested hostPlatform" in process.stderr:
            raise NotAvailableOnHostPlatformException()
        elif "does not provide attribute" in process.stderr:
            raise AttributeNotProvidedException()
        elif (
            "has an unfree license (‘unfree’), refusing to evaluate." in process.stderr
        ):
            raise UnfreeLicenceException()
        else:
            raise exception

    output = json.loads(process.stdout)
    path = output[0]["outputs"]["out"]
    return path


def remove_package(store: Path, package_name: str):
    process = _run_nix(
        "store",
        "delete",
        "--store",
        str(store),
        f"nixpkgs#{package_name}",
    )

    try:
        process.check_returncode()
    except CalledProcessError:
        if "since it is still alive." in process.stderr:
            raise StillAliveException()
        raise Exception(process.stderr)


def _check_paths_are_valid(output):
    if any(not path["valid"] for path in output):
        raise PackageNotInstalledException()


def get_closure_size(store: Path, package_name: str):
    process = _run_nix(
        "path-info",
        "--json",
        "--store",
        str(store),
        "--closure-size",
        f"nixpkgs#{package_name}",
    )
    process.check_returncode()

    output = json.loads(process.stdout)
    _check_paths_are_valid(output)

    closure_size = sum(path["closureSize"] for path in output)
    return closure_size


def get_closure(store: Path, package_name: str) -> list[str]:
    process = _run_nix(
        "path-info",
        "--json",
        "--store",
        str(store),
        "--recursive",
        f"nixpkgs#{package_name}",
    )
    process.check_returncode()

    output = json.loads(process.stdout)
    _check_paths_are_valid(output)

    return list(set(path["path"] for path in output))
