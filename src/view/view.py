from qt_lib.qt_compact import *
import qdarkstyle
from config import constant
from pathlib import Path
from typing import List
# from qt_material import apply_stylesheet

import os

con = constant.Constant()


class PreferencesDialog(QDialog):
    """
    A preferences dialog allowing the user to configure project-specific
    file extensions and settings.

    Attributes:
        existing_prefs_data (dict): Dictionary containing existing preferences.
        config_file_path (Path): Path to the configuration file.
        proj_combo (QComboBox): Dropdown for selecting a project.
        lst_wid (QListWidget): List of extensions with checkboxes.
        info_lbl (QLabel): Label for displaying info messages.
        close_btn (QPushButton): Button to close the dialog.
        update_btn (QPushButton): Button to save/update preferences.
    """
    def __init__(self, existing_prefs_data, parent=None, ):
        super().__init__(parent)
        self.existing_prefs_data = existing_prefs_data
        self.config_file_path = con.CONFIG_FILEPATH
        self.setWindowTitle("Application Preferences")
        icon_path = Path.cwd() / "icon" / "gear_cog_wheel.jpg"
        self.setWindowIcon(QIcon(str(icon_path)))
        self.dialog_vlay = QVBoxLayout()
        self.add_widgets()
        self.setLayout(self.dialog_vlay)

    def add_widgets(self):
        """Create and add all widgets (labels, combobox, buttons) to the dialog."""

        lbl_info = QLabel("Manage project-specific extensions settings")
        self.dialog_vlay.addWidget(lbl_info)
        
        divider = QFrame()
        divider.setFrameShape(QFrame.HLine)
        divider.setFrameShadow(QFrame.Sunken)
        self.dialog_vlay.addWidget(divider)

        hbox_lay_01 = QHBoxLayout()     
        proj_lbl = QLabel("Project:")
        self.proj_combo = QComboBox()      
        existing_prefs_proj_lst = list(self.existing_prefs_data.keys())
        self.proj_combo.addItems(['-- Select Project --'] + existing_prefs_proj_lst)
        
        hbox_lay_01.addWidget(proj_lbl)
        hbox_lay_01.addWidget(self.proj_combo)
        
        self.dialog_vlay.addLayout(hbox_lay_01)

        self.lst_wid = QListWidget()
        self.dialog_vlay.addWidget(self.lst_wid)

        self.info_lbl = QLabel()
        self.dialog_vlay.addWidget(self.info_lbl)

        btn_hlay = QHBoxLayout()
        self.close_btn = QPushButton("Close")
        icon = QApplication.style().standardIcon(QStyle.SP_DialogCloseButton)
        self.close_btn.setIcon(icon)

        self.update_btn = QPushButton("Update")
        icon = QApplication.style().standardIcon(QStyle.SP_DialogOkButton)
        self.update_btn.setIcon(icon)
        self.toggle_button_state()

        btn_hlay.addWidget(self.close_btn)
        btn_hlay.addWidget(self.update_btn)
        self.dialog_vlay.addLayout(btn_hlay)

    def set_extension_lst(self, supported_ext_lst):
        """
        Populate the extension list for the currently selected project.

        Args:
            supported_ext_lst (list[str]): List of supported file extensions.
        """
        selected_proj = self.get_current_project_code()
        if selected_proj != '-- Select Project --':
            self.lst_wid.clear()

            print("AVAILABLE_EXTENSIONS ---- ", con.AVAILABLE_EXTENSIONS)
            for ext in con.AVAILABLE_EXTENSIONS:
                item = QListWidgetItem(ext)
                item.setFlags(item.flags() | Qt.ItemIsUserCheckable)

                if ext in supported_ext_lst:
                    item.setCheckState(Qt.Checked)
                else:
                    item.setCheckState(Qt.Unchecked)

                self.lst_wid.addItem(item)
 
        elif selected_proj == '-- Select Project --':
            self.lst_wid.clear()

        self.toggle_button_state()

    def get_checked_extension(self):
        """Return a list of all extensions"""
        self.checked_item_nm_lst = []
        for item_index in range(self.lst_wid.count()):
            lst_item = self.lst_wid.item(item_index)
            if lst_item.checkState() == Qt.Checked:
                self.checked_item_nm_lst.append(lst_item.text())

        return self.checked_item_nm_lst

    def toggle_button_state(self):
        """Return a list of all extensions."""
        if self.proj_combo.currentText()  == '-- Select Project --':
            self.update_btn.setEnabled(False)
        else:
            self.update_btn.setEnabled(True)

    def get_current_project_code(self):
        return self.proj_combo.currentText()


class TreeWidgetWorker(QObject):
    """
    Worker for processing folder tree data in a separate thread.

    Signals:
        tree_data_ready (str, dict): Emitted when a tree item is ready.
        finished: Emitted when processing is complete.
    """
    tree_data_ready = Signal(str, dict)
    finished = Signal()

    def __init__(self, folder_tree_data_lst):
        super().__init__()
        self.folder_tree_data_lst = folder_tree_data_lst

    def run(self):
        """Process folder tree data and emit signals for each item."""
        for dict_itm in self.folder_tree_data_lst:
            base_nm = list(dict_itm.keys())[0]
            path = dict_itm[base_nm]["path"]
            self.tree_data_ready.emit(base_nm, dict_itm[base_nm])

        self.finished.emit()


class TreeWidget(QTreeWidget):  
    """
    Custom QTreeWidget for displaying folder/file hierarchies.

    Signals:
        filesDropped (list): Emitted when files are dropped onto the widget.
    """
    filesDropped = Signal(list)
    
    def __init__(self):
        super().__init__()
        self.thread_obj_lst = []
        self.path_item_pairs = []
        self.setHeaderHidden(True)
        self.setAcceptDrops(True)


    def dragEnterEvent(self, event:QDragEnterEvent):
        """Allow drag enter if the data contains URLs."""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()
    
    def dragMoveEvent(self, e:QDragMoveEvent):
        """Allow drag move if the data contains URLs."""
        if e.mimeData().hasUrls():
            e.acceptProposedAction()
        else:
            e.ignore()

    def dropEvent(self, event):
        """Handle file drop and emit signal with dropped URLs."""
        if event.mimeData().hasUrls():
            drop_urls = event.mimeData().urls()
            self.filesDropped.emit(drop_urls)
        else:
            event.ignore()

    def enterEvent(self, event):
        super().enterEvent(event)


    def tree_wid_itm_processed(self, tree_item):
        self.addTopLevelItem(tree_item)

    def build_tree_view(self, path, tree_item):  
        """Recursively build a tree view from the filesystem path."""   
        dir_contents = os.listdir(path)

        for item in sorted(dir_contents):
            full_path = os.path.join(path, item)

            if os.path.isdir(full_path):
                folder_item = QTreeWidgetItem([item , "Folder"])
                tree_item.addChild(folder_item)
                self.build_tree_view(full_path, folder_item)
            
            elif os.path.isfile(full_path):
                file_item = QTreeWidgetItem([item, "File"])
                tree_item.addChild(file_item)


    def process_tree_data(self, base_nm, data):
        """Add tree items for a given folder structure."""
        path = data["path"]
        tree_item = QTreeWidgetItem([base_nm, "Folder"]) 
        self.addTopLevelItem(tree_item)
        self.build_tree_view(path, tree_item)



    def load_folder_tree_into_ui(self, folder_tree_data_lst):
        """
        Load folder tree data into the widget using a QThread.

        Args:
            folder_tree_data_lst (list): List of dicts with folder info.
        """
        # ---------------------------------------------------------------------
        # This code with qthread

        self.clear()
        self.thread_obj = QThread()

        self.tree_worker = TreeWidgetWorker(folder_tree_data_lst)
        self.tree_worker.moveToThread(self.thread_obj)

        self.thread_obj.started.connect(self.tree_worker.run)

        self.tree_worker.tree_data_ready.connect(self.process_tree_data)
        self.tree_worker.finished.connect(self.thread_obj.quit)
        self.tree_worker.finished.connect(self.tree_worker.deleteLater)

        self.thread_obj.finished.connect(self.thread_obj.deleteLater)
        self.thread_obj.start()
        # ---------------------------------------------------------------------


        # ********************************************************************
        # This code for without qthread

        # self.clear()
        # for dict_itm in folder_tree_data_lst:
        #     base_nm = list(dict_itm.keys())[0]
        #     path = dict_itm[base_nm]["path"]
        #     tree_item = QTreeWidgetItem([base_nm, "Folder"]) 
        #     self.addTopLevelItem(tree_item)
        #     self.build_tree_view(path, tree_item)
        # ********************************************************************


class TreeItemClickSignals(QObject):
    """Signals for TreeItemClickWorkerPool."""
    custom_context = Signal(list, str, str)
    completed = Signal()


class TreeItemClickWorkerPool(QRunnable):
    """
    Worker pool task for processing thumbnail widget items.

    Attributes:
        thumbnil_wid_items_lst (list): List of thumbnail widget items.
        thumb_dir_name (str): Directory name for thumbnails.
        msg (str): Message related to the operation.
    """
    def __init__(self, thumbnil_wid_items_lst, thumb_dir_name, msg):
        super().__init__()
        self.thumbnil_wid_items_lst = thumbnil_wid_items_lst
        self.thumb_dir_name = thumb_dir_name
        self.msg = msg
        self.signal_obj = TreeItemClickSignals()


    def run(self):
        self.signal_obj.custom_context.emit(
            self.thumbnil_wid_items_lst,
            self.thumb_dir_name,
            self.msg)

        self.signal_obj.completed.emit()



class View(QMainWindow):
    """
    Main application window for Asset Manager.

    Attributes:
        tree_wid (TreeWidget): Left-side tree for file navigation.
        lst_wid (QListWidget): Center list for thumbnails.
        tab_wid (QTabWidget): Right-side tab for viewer and metadata.
    """
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.setWindowTitle("Thumbnil Viewer")
        self.set_geometry(app)
        # self._current_theme = "qdarkstyle"

        self.pixmap = None
        self.lbl_thumb_path = None
        self.tree_wid = None

        self.scroll = QScrollArea()
        widget = QWidget() 

        self.mainvlay = QVBoxLayout()
        self.mainvlay.setContentsMargins(1, 1, 1, 1)
        self.splitter = QSplitter(Qt.Horizontal)
        
        widget.setLayout(self.mainvlay)
        self.setCentralWidget(widget)

        self.add_menu()
        self.add_tree_wid()
        self.add_lst_wid()
        self.add_viewer_wid()

        self.mainvlay.addWidget(self.splitter)
        self.splitter.setSizes([200, 300, 500])


    def set_style_sheet(self):
        self.setStyleSheet("""
            background-color: #404040;
            border: none;                   
        """)

    def set_geometry(self, app):
        """Maximize window to full screen size."""
        screen = app.primaryScreen().geometry()
        width = screen.width()
        height = screen.height()
        self.setGeometry(0, 0, width, height)
        self.setMaximumWidth(width)
        self.setMaximumHeight(height)

    def add_thumbnil_wid(self, thumbnil_wid_items_lst):
        """Add a list of thumbnail widgets to the list view."""

        for widget in thumbnil_wid_items_lst:
            print("widget ==== ", widget)
            list_item = QListWidgetItem()
            list_item.setSizeHint(widget.sizeHint())

            self.lst_wid.addItem(list_item)
            self.lst_wid.setItemWidget(list_item, widget)

        self.lst_wid.setSpacing(10)

    def clear_lst_wid(self):
        self.lst_wid.clear()


    def add_menu(self):
        """Create menubar and menus (File, Edit, Preferences)."""
        menu = self.menuBar()

        # Preferences menu
        preferences_menu = menu.addMenu(" Preferences ")
        self.preferences_action = QAction("Configuration Settings", self)
        preferences_menu.addAction(self.preferences_action)


        # =========================
        # HELP MENU
        # =========================
        help_menu = menu.addMenu("Help")
        self.about_action = QAction("About", self)
        help_menu.addAction(self.about_action)


        # # Theme Switcher menu
        # theme_menu = menu.addMenu(" Theme Switcher ")
        
        # qt_material_menu = theme_menu.addMenu('Qt - Material')
        
        # self.dark_teal_action = QAction('dark_teal', self)
        # self.dark_blue_action = QAction('dark_blue', self)
        # self.light_blue_action = QAction('light_blue', self)
        # self.light_red_action = QAction('light_red', self)
        # self.dark_purple_action = QAction('dark_purple', self)

        # qt_material_menu.addAction(self.dark_teal_action)
        # qt_material_menu.addAction(self.dark_blue_action)
        # qt_material_menu.addAction(self.light_blue_action)
        # qt_material_menu.addAction(self.light_red_action)
        # qt_material_menu.addAction(self.dark_purple_action)

        # # ---------------------------------------
        # # Default theme (qdarkstyle)
        # # ---------------------------------------
        # self.qdarkstyle_action = QAction("qdarkstyle", self)
        # theme_menu.addAction(self.qdarkstyle_action)
   

    # def set_material_theme(self, theme):
    #     if getattr(self, "_current_theme", None) == theme:
    #         return
    #     self._current_theme = theme
        
    #     # CLEAR previous stylesheet
    #     self.app.setStyleSheet("")

    #     from qt_material import apply_stylesheet
    #     apply_stylesheet(self.app, theme=theme)

    # def set_qdarkstyle_theme(self):
    #     if self._current_theme == "qdarkstyle":
    #         return

    #     self._current_theme = "qdarkstyle"

    #     # CLEAR material stylesheet
    #     self.app.setStyleSheet("")

    #     # Reapply qdarkstyle
    #     self.app.setStyleSheet(qdarkstyle.load_stylesheet_pyside2())

    def add_tree_wid(self):
        """Add the tree widget to the splitter."""
        self.tree_wid = TreeWidget()
        self.splitter.addWidget(self.tree_wid)

    def add_lst_wid(self):
        """Add the thumbnail list widget to the splitter."""
        lst_widget = QWidget()
        lst_vlay = QVBoxLayout(lst_widget)
        lst_vlay.setContentsMargins(1,1,1,1)

        self.lbl_thumb_path = QLabel('')
        # self.lbl_thumb_path.setStyleSheet("""
        #     QLabel {
        #         color: white;                
        #         background-color: #333333;        
        #         padding: 5px;               
        #         border-radius: 3px;    
        #     }       
        # """)

        self.lst_wid = QListWidget()
        self.lst_wid.setSelectionMode(QListWidget.ExtendedSelection)
        
        # self.lst_wid.setStyleSheet("""
        #     QListWidget {             
                  
        #         border: 3px solid #444;          
        #     }       
        # """)

        lst_vlay.addWidget(self.lbl_thumb_path)
        lst_vlay.addWidget(self.lst_wid)

        self.splitter.addWidget(lst_widget)
        
    def set_lbl_thumbnil_path(self, text):
        """Set the label text for the current thumbnail directory path."""
        self.lbl_thumb_path.setText(f"Thumbnil Directory Path:\n{text}")
        font = QFont()
        font.setFamilies("Verdana")
        font.setBold(True) 
        self.lbl_thumb_path.setFont(font)
        

    def add_viewer_wid(self):
        """Add the viewer widget with tabs for render preview and metadata."""
        self.viewer_wid = QWidget()

        right_vlay = QVBoxLayout(self.viewer_wid)
        right_vlay.setContentsMargins(0, 0, 0, 0)
        tab_vlay = QVBoxLayout()
        self.tab_wid = QTabWidget()

        self.tab_wid.addTab(self.create_viewer_tab(), "Viewer")
   
        tab_vlay.addWidget(self.tab_wid)
        right_vlay.addLayout(tab_vlay)    
        self.splitter.addWidget(self.viewer_wid)

    def create_viewer_tab(self, meta=None):
        """Create a tab for either viewer or metadata."""
        tab_view_wid = QWidget()
        tab_view_vlay_1 = QVBoxLayout()
        if meta is None:
            self.tab_view_lbl = QLabel()
            tab_view_vlay_1.addWidget(self.tab_view_lbl)
        tab_view_wid.setLayout(tab_view_vlay_1)
        return tab_view_wid

    def load_render_in_viewer(self, path):
        """Load an image render into the viewer tab."""
        current_tab = self.tab_wid.currentWidget()
        label = current_tab.findChild(QLabel)

        self.pixmap = QPixmap(path)
        if not self.pixmap.isNull():
            self.tab_view_lbl.clear()
            self.tab_view_lbl.setAlignment(Qt.AlignCenter)
        else:
            self.tab_view_lbl.clear()
            self.tab_view_lbl.setText("Image not found!")
            self.tab_view_lbl.setAlignment(Qt.AlignCenter)       

    def open_pref_dialog(self, existing_prefs_data):

        # dialog_style = """
        #     QDialog {
        #         background-color: #2b2b2b;
        #         color: #f0f0f0;
        #         font-family: "Segoe UI", Arial, sans-serif;
        #         font-size: 12px;
        #     }

        #     /* QLabel */
        #     QLabel {
        #         color: #f0f0f0;
        #         font-size: 12px;
        #         padding: 2px;
        #     }

        #     /* QComboBox */
        #     QComboBox {
        #         background-color: #3a3a3a;
        #         color: #f0f0f0;
        #         border: 1px solid #555;
        #         padding: 4px;
        #         border-radius: 3px;
        #     }
        #     QComboBox:hover {
        #         border: 1px solid #888;
        #     }
        #     QComboBox::drop-down {
        #         subcontrol-origin: padding;
        #         subcontrol-position: top right;
        #         width: 20px;
        #         border-left: 1px solid #555;
        #         background-color: #444;
        #     }
        #     QComboBox QAbstractItemView {
        #         background-color: #2b2b2b;
        #         selection-background-color: #555;
        #         selection-color: white;
        #     }

        #     /* QListWidget */
        #     QListWidget {
        #         background-color: #333;
        #         color: #f0f0f0;
        #         border: 1px solid #555;
        #         padding: 2px;
        #     }
        #     QListWidget::item {
        #         padding: 4px;
        #     }
        #     QListWidget::item:selected {
        #         background-color: #555;
        #         color: white;
        #     }

        #     /* Checkable QListWidgetItem */
        #     QListWidget::indicator {
        #         width: 14px;
        #         height: 14px;
        #     }
        #     QListWidget::indicator:unchecked {
        #         border: 1px solid #aaa;
        #         background-color: #444;
        #     }
        #     QListWidget::indicator:checked {
        #         border: 1px solid #5a9;
        #         background-color: #2e8b57;
        #     }

        #     /* QPushButton */
        #     QPushButton {
        #         background-color: #444;
        #         color: #f0f0f0;
        #         border: 1px solid #666;
        #         padding: 6px 10px;
        #         border-radius: 4px;
        #     }
        #     QPushButton:hover {
        #         background-color: #555;
        #         border: 1px solid #888;
        #     }
        #     QPushButton:pressed {
        #         background-color: #222;
        #         border: 1px solid #888;
        #     }
        #     QPushButton:disabled {
        #         background-color: #333;
        #         color: #777;
        #         border: 1px solid #444;
        # }
        # """


        prefs_window = PreferencesDialog(existing_prefs_data, self)
        if prefs_window:
            prefs_window.show()

        return prefs_window

    def show_notification(self, msg):
        QMessageBox.information(self, "Action", msg)

    def wheelEvent(self, event: QWheelEvent):
        event.ignore()

    def remove_selected(self, widget):
        self.lst_wid.takeItem(widget)
       
    def show_about_info(self):
        # HTML version of your help text
        help_text = """
        <h2>📝 How to Thumbnails-Viewer Application</h2>

        <h3>1. Load Images</h3>
        <ul>
            <li>Drag and drop a <b>folder</b> into the <b>left-side of the window screen</b>.</li>
        </ul>
        <p><i>Tip:</i> Only directories with supported image formats will display thumbnails.</p>

        <h3>2. Preview Thumbnails</h3>
        <ul>
            <li>The <b>center widget</b> displays thumbnails-information for all images in the selected folder.</li>
            <li>Each thumbnail shows:
                <ul>
                    <li>Image Name</li>
                    <li>Project Code</li>
                    <li>Short Code</li>
                </ul>
            </li>
        </ul>
        <p><i>Tip:</i> Scroll through the list to view all images in the folder.</p>

        <h3>3. View Images</h3>
        <ul>
            <li>Double-click a thumbnail to open it in the <b>Viewer tab</b>.</li>
            <li>Zoom options:
                <ul>
                    <li>Mouse scroll wheel → Scale image up or down</li>
                    <li>Keyboard → Press <b>+</b> to zoom in, <b>-</b> to zoom out</li>
                </ul>
            </li>
            <li>Alternative: Right-click a thumbnail → Load in Viewer</li>
        </ul>
        <p><i>Tip:</i> The Viewer tab keeps your images centered and scalable for detailed inspection.</p>

        <h3>4. Remove Images</h3>
        <ul>
            <li>Select one or more thumbnails.</li>
            <li>Right click on thumbnail and click on <b>Remove</b> button to delete them from the widget.</li>
        </ul>
        <p><i>Tip:</i> Removing images from the list does not delete them from your disk.</p>

        <h3>5. Configure Project Preferences</h3>
        <ol>
            <li>Click the <b>Preferences</b> menu → Configuration Setting Action.</li>
            <li>The Application Preferences dialog opens.</li>
            <li>Select the project you want to configure.</li>
            <li>Check the boxes for the desired <b>file extensions</b>.</li>
            <li>Click <b>Update</b>, then <b>Close</b> to save your settings.</li>
            <li>After updating, reselect the folder to reload thumbnails with updated preferences.</li>
        </ol>
        <p><i>Tip:</i> This allows you to filter which file types appear for each project.</p>

        <p><b>Pro Tip:</b> Always update preferences before loading a folder. Use the Viewer tab to inspect images without changing your thumbnail list.</p>
        """

        QMessageBox.about(self, "Application Help", help_text)