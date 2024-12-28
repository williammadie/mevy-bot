class VectorStoreNotInitializedError(Exception):
    """
    When the vector_store attribute is None but an operation requires
    it to be initialized 
    """