from platformdirs import user_documents_dir
from pathlib import Path
import os

class Constant:
    """
    A container for application-wide constants such as default paths, 
    configuration filenames, supported file extensions, and style resources.

    These constants are designed to centralize shared values that remain fixed 
    across the application, ensuring consistency and easier maintainability.
    """ 
    DOCUMENTS_DIRPATH = user_documents_dir()

    APP_DIRNAME = ".app"
    CONFIG_FILENAME = "config.json"
    AVAILABLE_EXTENSIONS = ["exr", "jpeg", "jpg", "png", "mov"]
    DEFAULT_ENABLED_EXTS = {"jpeg", "jpg"}
    CONFIG_FILEPATH = Path(DOCUMENTS_DIRPATH) / APP_DIRNAME / CONFIG_FILENAME
    STYLE_QSSPATH =   Path(os.path.dirname(__file__)) / "style.qss" 



