from pathlib import Path
from shutil import rmtree


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
