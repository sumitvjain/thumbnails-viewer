
try:
    from PySide2.QtWidgets import *
    from PySide2.QtCore import *
    from PySide2.QtGui import *
    from PySide2.QtMultimedia import *
    
    QT_API = "PySide2"
    
except ImportError:
    from PySide6.QtWidgets import *
    from PySide6.QtCore import *
    from PySide6.QtGui import *
    from PySide6.QtMultimedia import *
    
    QT_API = "PySide6"
    
print("QT_API --- ", QT_API)