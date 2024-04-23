class InsecurePackageException(Exception):
    pass


class BrokenPackageException(Exception):
    pass


class NotAvailableOnHostPlatformException(Exception):
    pass


class AttributeNotProvidedException(Exception):
    pass


class UnfreeLicenceException(Exception):
    pass


class StillAliveException(Exception):
    pass


class PackageNotInstalledException(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message

    def __str__(self):
        return self.message
