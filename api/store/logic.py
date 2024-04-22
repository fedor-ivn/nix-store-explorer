from pathlib import Path
from shutil import rmtree
from subprocess import run
import json


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
    return set(
        f"/nix/store/{path.name}"
        for path in (store / "nix/store").iterdir()
        if path.name != ".links"
    )


def install_package(store: Path, package_name: str):
    process = run(
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
    process.check_returncode()

    output = json.loads(process.stdout)
    path = output[0]["outputs"]["out"]
    return path


def remove_package(store: Path, package_name: str):
    process = run(
        ["nix", "store", "delete", "--store", str(store), f"nixpkgs#{package_name}"],
        capture_output=True,
        text=True,
    )
    if process.stderr:
        raise Exception(process.stderr)
    process.check_returncode()


def _check_paths_are_valid(output, package_name: str):
    if any(not path["valid"] for path in output):
        raise Exception(f"Package nixpkgs#{package_name} is not installed")


def get_closure_size(store: Path, package_name: str):
    process = run(
        [
            "nix",
            "path-info",
            "--json",
            "--store",
            str(store),
            "--closure-size",
            f"nixpkgs#{package_name}",
        ],
        capture_output=True,
        text=True,
    )
    process.check_returncode()

    output = json.loads(process.stdout)
    _check_paths_are_valid(output, package_name)

    closure_size = sum(path["closureSize"] for path in output)
    return closure_size


def get_closure(store: Path, package_name: str):
    process = run(
        [
            "nix",
            "path-info",
            "--json",
            "--store",
            str(store),
            "--recursive",
            f"nixpkgs#{package_name}",
        ],
        capture_output=True,
        text=True,
    )
    process.check_returncode()

    output = json.loads(process.stdout)
    _check_paths_are_valid(output, package_name)

    return set(path["path"] for path in output)