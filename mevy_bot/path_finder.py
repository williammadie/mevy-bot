import os


class PathFinder:

    @classmethod
    def package_path(cls) -> str:
        return os.path.dirname(__file__)

    @classmethod
    def project_path(cls) -> str:
        return os.path.dirname(cls.package_path())
    
    @classmethod
    def secrets(cls) -> str:
        return os.path.join(cls.project_path(), "secrets")

    @classmethod
    def data_definition(cls) -> str:
        return os.path.join(cls.project_path(), "data_definition")

    @classmethod
    def data_storage(cls) -> str:
        return os.path.join(cls.project_path(), "data_storage")

    @classmethod
    def data_storage_auto(cls) -> str:
        return os.path.join(cls.data_storage(), "auto")

    @classmethod
    def data_storage_manual(cls) -> str:
        return os.path.join(cls.data_storage(), "manual")

    @classmethod
    def log_dirpath(cls) -> str:
        log_dirpath = os.getenv('LOGS_DIRPATH')
        if log_dirpath is None:
            return os.path.join(cls.project_path(), 'logs')
        return log_dirpath
