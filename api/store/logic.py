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
