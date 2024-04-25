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
    pass
