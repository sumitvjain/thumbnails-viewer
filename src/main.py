# from qt_lib.qt_compact import *
import sys, os
from pathlib import Path
from qt_lib import qt_compact #module 
from PySide2.QtGui import QFontDatabase
import qdarkstyle

from view import view
from model import model
from controller import controller
from config import constant, settings



def resource_path(relative_path):
    """
    Works for:
    - python main.py
    - PyInstaller --onefile exe
    """
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)





if __name__ == "__main__":
    app = qt_compact.QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyside2())

    # #####################################################################
    # qss_file = Path("resources/styles.qss")
    # if qss_file.exists():
    #     app.setStyleSheet(app.styleSheet() + qss_file.read_text())
    # else:
    #     print('no'*10)
    # #####################################################################


    qss_path = resource_path("resources/styles.qss")

    if os.path.exists(qss_path):
        with open(qss_path, "r", encoding="utf-8") as f:
            app.setStyleSheet(app.styleSheet() + f.read())
    else:
        print("QSS file not found:", qss_path)




    view = view.View(app)
    model = model.Model()  

    settings.setup_config()

    controller = controller.Controller(model, view)
    
    view.show()
    sys.exit(app.exec_())


#######################

  # Run using --> pyinstaller --onefile main.py
