from qt_lib.qt_compact import *


class Controller(QObject):
    """
    Controller class acts as a mediator between the Model and View.
    Responsibilities:
    - Connects UI actions to corresponding model/view methods.
    - Handles user interactions like clicks, drag/drop, context menus.
    - Manages zooming, keyboard shortcuts, and updating the view.
    - Controls project preferences and configuration updates.
    """

    def __init__(self, model, view):

        """
        Initialize Controller.

        Args:
            model: Instance of the Model class (data and logic).
            view: Instance of the View class (UI components).
        """

        super().__init__()
        self.model = model
        self.view = view
        self.zoom_factor = 1.0
        self.signal_slot()
        self.view.tab_wid.setFocusPolicy(Qt.StrongFocus)
        self.view.tab_wid.installEventFilter(self)
        


    def signal_slot(self):   
        """
        Connects UI signals to controller methods.
        """

        # Preference menu actions
        self.view.preferences_action.triggered.connect(self.preferences_clicked)
        self.view.about_action.triggered.connect(self.show_about)

        # # Theme Switcher menu action
        # self.view.dark_teal_action.triggered.connect(
        #     lambda: self.view.set_material_theme('dark_teal.xml'))
        # self.view.dark_blue_action.triggered.connect(
        #     lambda: self.view.set_material_theme('dark_blue.xml'))
        # self.view.light_blue_action.triggered.connect(
        #     lambda: self.view.set_material_theme('light_blue.xml'))
        # self.view.light_red_action.triggered.connect(
        #     lambda: self.view.set_material_theme('light_red.xml'))
        # self.view.dark_purple_action.triggered.connect(
        #     lambda: self.view.set_material_theme('dark_purple.xml'))

        # # Default theme (qdarkstyle)
        # self.view.qdarkstyle_action.triggered.connect(self.view.set_qdarkstyle_theme)

        # Tree widget actions
        self.view.tree_wid.itemClicked.connect(self.on_item_clicked)
        self.view.tree_wid.filesDropped.connect(self.on_files_dropped)


    def proj_combo_index_changed(self):
        """
        Triggered when project combo box index changes in preferences dialog.
        Updates extension list for selected project.
        """
        proj_code = self.prefs_window.get_current_project_code()
        ext_list = self.model.fetch_project_extensions(proj_code)
        
        self.prefs_window.set_extension_lst(ext_list)

    def update_btn_clicked(self):
        """
        Triggered when 'Update' button is clicked in preferences dialog.
        Saves updated extensions for selected project.
        """
        new_extensions = self.prefs_window.get_checked_extension()
        selected_proj = self.prefs_window.proj_combo.currentText() 
        self.model.overwrite_config(new_extensions, selected_proj)


    def on_lst_wid_double_clicked(self, img_data_dict):
        path = img_data_dict["image_full_path"]
        
        self.view.load_render_in_viewer(path)
        self.update_image_size()

    def on_item_clicked(self, item, column):
        """
        Triggered when a tree widget item is clicked.
        Fetches thumbnails and updates the UI.

        Args:
            item: QTreeWidgetItem clicked.
            column: Column index clicked.
        """
        # ==========================================================================================
        # ---- Without ThreadPool ---- #
        thumbnil_wid_items_lst, thumb_dir_name, msg = self.model.get_thumbnil_wid_lst(item, column)

        if thumbnil_wid_items_lst:
            self.view.clear_lst_wid()
            self.view.set_lbl_thumbnil_path(thumb_dir_name)
            self.view.add_thumbnil_wid(thumbnil_wid_items_lst)

            for w in thumbnil_wid_items_lst:
                w.customContextMenuRequested.connect(
                    lambda pos, widget=w: self.handle_context_menu(widget, pos)
                    )
                w.doubleClicked.connect(self.on_lst_wid_double_clicked)

        else:
            self.view.clear_lst_wid()
            self.view.set_lbl_thumbnil_path(thumb_dir_name)
            self.view.show_notification(msg)
        # ==========================================================================================

        # ---------------------------------------------------------------------------------------------     
        # ---- With ThreadPool (Causing UI crash, commented) ---- # 

        # thumbnil_wid_items_lst, thumb_dir_name, msg = self.model.get_thumbnil_wid_lst(item, column)      

        # tree_item_click_worker_pool = TreeItemClickWorkerPool(thumbnil_wid_items_lst, thumb_dir_name, msg)
        # tree_item_click_worker_pool.signal_obj.custom_context.connect(self.update_ui_frm_workerpool)

        # thread_pool = QThreadPool.globalInstance()
        # thread_pool.start(tree_item_click_worker_pool)
        # --------------------------------------------------------------------------------------------- 

    def thumbnail_context_action(self, thumbnil_wid_items_lst):
        """
        Attach context menu actions for a list of thumbnail widgets.

        Args:
            thumbnil_wid_items_lst (list): List of thumbnail widget instances.
        """
        for w in thumbnil_wid_items_lst:
            w.customContextMenuRequested.connect(lambda pos, widget=w: self.handle_context_menu(widget, pos))

    def update_ui_frm_workerpool(self, thumbnil_wid_items_lst, thumb_dir_name, msg):
        """
        Update UI after worker pool completes (ThreadPool approach).

        Args:
            thumbnil_wid_items_lst (list): Thumbnails loaded by worker.
            thumb_dir_name (str): Directory path of thumbnails.
            msg (str): Status message.
        """
        if thumbnil_wid_items_lst:
            self.view.clear_lst_wid()
            self.view.set_lbl_thumbnil_path(thumb_dir_name)
            self.view.add_thumbnil_wid(thumbnil_wid_items_lst)
            self.thumbnail_contextc_action(thumbnil_wid_items_lst)
        else:
            self.view.clear_lst_wid()
            self.view.set_lbl_thumbnil_path(thumb_dir_name)
            self.view.show_notification(msg)        

    def on_files_dropped(self, drop_urls):
        """
        Handle file/folder drop onto tree widget.

        Args:
            drop_urls (list): Dropped file/folder URLs.
        """
        folder_tree_data_lst = self.model.get_urls_data(drop_urls)
        self.view.tree_wid.load_folder_tree_into_ui(folder_tree_data_lst)

    # ---------------- Context Menu Handling ---------------- #
    def handle_context_menu(self, widget, pos):       
        """
        Display context menu for a thumbnail widget.

        Args:
            widget: Thumbnail widget.
            pos: Position where context menu was requested.
        """
        widget.populate_menu_actions(pos)
        self.action = widget.menu.exec_(widget.mapToGlobal(pos)) 

        if self.action:
            self.action_clicked(self.action, pos)

    def action_clicked(self, invoked_action, pos):
        """
        Handle action clicked from thumbnail context menu.

        Args:
            invoked_action: QAction invoked.
            pos: Position of action trigger.
        """
        if invoked_action.text() == "Load in Viewer":
            result, path = self.model.get_invoked_action_path(invoked_action)
            if result:
                self.view.load_render_in_viewer(path)
                self.update_image_size()
            else:
                self.view.show_notification(f"No [' {invoked_action.text()}' ] file was found.")

        elif self.action.text() == "Remove":
            selected_items = self.view.lst_wid.selectedItems()
            rows = sorted([self.view.lst_wid.row(it) for it in selected_items], reverse=True)

            for row in rows:
                self.view.remove_selected(row) 

        elif self.action.text() == "Compare":
            selected_items = self.view.lst_wid.selectedItems()
            if len(selected_items) == 2:
                self.view.show_notification("The selected version has been loaded into the viewer")
            else:       
                self.view.show_notification("You must select two items to proceed")

     # ---------------- Event Handling ---------------- #
    def eventFilter(self, obj, event):
        """
        Event filter to handle zooming (mouse wheel, +/- keys) and focus on tab widget.

        Args:
            obj: Object receiving the event.
            event: QEvent instance.

        Returns:
            bool: Whether event was handled or passed along.
        """
        if obj == self.view.tab_wid and event.type() == QEvent.Wheel:
            if self.view.tab_wid.underMouse():
                zoom_in = event.angleDelta().y() > 0

                if zoom_in:
                    self.zoom_factor *= 1.1
                else:
                    self.zoom_factor *= 0.9

                self.zoom_factor = max(0.1, min(self.zoom_factor, 10.0))

                self.update_image_size()
                event.accept()
            else:
                return True
            
        elif obj == self.view.tab_wid and event.type() == QEvent.KeyPress:
            key = event.key()
            if key == Qt.Key_Plus:
                self.zoom_factor *= 1.1
            elif key == Qt.Key_Minus:
                self.zoom_factor *= 0.9
                
            self.zoom_factor = max(0.1, min(self.zoom_factor, 10.0))
            self.update_image_size()
            event.accept()
            return True

        elif obj == self.view.tab_wid and event.type() == QEvent.MouseButtonPress:
            self.view.tab_wid.setFocus()

        return super().eventFilter(obj, event)
    
    def update_image_size(self):
        """
        Scale and update image preview based on current zoom factor.
        """
        if self.view.pixmap:
            scaled_pixmap = self.view.pixmap.scaled(
                self.view.tab_view_lbl.size() * self.zoom_factor,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )

            max_height = 428
            max_width = 764

            if scaled_pixmap.height() <= max_height and scaled_pixmap.width() <= max_width:
                self.view.tab_view_lbl.setPixmap(scaled_pixmap)
            else:
                # Re-scale to fit within max bounds
                fitted_pixmap = scaled_pixmap.scaled(
                    max_width - 1,
                    max_height - 1,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
                self.view.tab_view_lbl.setPixmap(fitted_pixmap)


    def preferences_clicked(self):
        """
        Handle 'Preferences' action.
        Opens preferences dialog and sets up signal connections.
        """
        existing_prefs_data = self.model.get_current_preferences()
        self.prefs_window = self.view.open_pref_dialog(existing_prefs_data)   
        self.prefs_window.proj_combo.currentIndexChanged.connect(self.proj_combo_index_changed)
        self.prefs_window.update_btn.clicked.connect(self.update_btn_clicked) 
        self.prefs_window.close_btn.clicked.connect(self.prefs_window.close)


    def show_about(self):
        self.view.show_about_info()

  




