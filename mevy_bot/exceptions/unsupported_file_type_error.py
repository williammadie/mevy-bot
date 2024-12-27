import logging


l = logging.getLogger(__name__)

class UnsupportedFileTypeError(Exception):
    """
    This file type cannot be used currently for this operation. 
    """

    def __init__(self, filepath: str, *args):
        l.error("The following file type is unsupported: %s", filepath)
        super().__init__(*args)
