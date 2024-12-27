import os


class PathFinder:

    @classmethod
    def package_path(cls) -> str:
        return os.path.dirname(__file__)

    @classmethod
    def project_path(cls) -> str:
        return os.path.dirname(cls.package_path())

    @classmethod
    def data_definition(cls) -> str:
        return os.path.join(cls.project_path(), "data_definition")

    @classmethod
    def data_storage(cls) -> str:
        return os.path.join(cls.project_path(), "data_storage")
    
    @classmethod
    def vector_store(cls) -> str:
        return os.path.join(cls.project_path(), "vector_store")
