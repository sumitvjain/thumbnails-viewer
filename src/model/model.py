import os
import json
import re
import random
from config import constant
from qt_lib.qt_compact import *
from view import thumbnil_container


con = constant.Constant()


class Model():
    """
    Model class responsible for handling core data operations such as:
    - Fetching folder and file tree structures
    - Extracting project configuration and supported extensions
    - Building thumbnail metadata for supported files
    - Basic file operations (open, save, undo, redo, etc.)
    """


    def __init__(self):
        """
        Initialize the Model object with default values.
        """
        self.thumbnil_widget = None
        self.drive = None

    def get_invoked_action_path(self, invoked_action):
        """
        Get the path text from the parent QLabel of an invoked QAction.

        Args:
            invoked_action: QAction object that triggered the event.

        Returns:
            tuple: (True, path) if path found, else None.
        """
        child_widgets = invoked_action.parentWidget().parentWidget().findChildren(QWidget)
        
        for child in child_widgets:
            if isinstance(child, QLabel):
                if child.text().startswith("Path"):
                    path = child.text().split("Path-")[-1]
                    
                    ####################################################
                    # return True, path
                    normalized = path.replace("\\", "/")
                    return True, normalized
                    ####################################################

    def fetch_folder_tree_data(self, path):
        """
        Recursively build a folder tree structure for the given directory.

        Args:
            path (str): Directory path.

        Returns:
            dict: Dictionary with folder structure containing subdirectories and files.
        """
        folder_tree_data = {
            "dir_name" : os.path.basename(path),
            "path" : path
            }

        if os.path.isdir(path):
            files = []
            folders = []

            for entry in sorted(os.listdir(path)):
                full_path = os.path.join(path, entry)
                if os.path.isdir(full_path):
                    folders.append(self.fetch_folder_tree_data(full_path))
                else:
                    files.append(full_path.replace("\\", "/"))

            if files:
                folder_tree_data["files"] = files
            if folders:
                folder_tree_data["sub_dir"] = folders

        return folder_tree_data

    def get_urls_data(self, drop_urls):
        """
        Process dropped URLs and generate folder tree data for directories.

        Args:
            drop_urls (list): List of QUrls dropped into the application.

        Returns:
            list: List of folder tree data dictionaries.
        """
        folder_tree_data_lst = []
        for url in drop_urls:
            url_path = url.toLocalFile() 
            if self.drive == None:
                self.drive = re.split(r"[\\/]", url_path)[0]
            tree_name = re.split(r"[\\/]", url_path)[-1]

            if os.path.isdir(url_path):
                if len(os.listdir(url_path)) > 0:

                    folder_tree_data_dict = self.fetch_folder_tree_data(url_path)
                    folder_tree_data_lst.append({tree_name:folder_tree_data_dict})

            #         # ----------------------------------------------------------
            #         # This is working code without thread
            #         self.addTopLevelItem(tree_item)
            #         self.build_tree_view(path, tree_item)
            #         # event.accept()  
            #         # ----------------------------------------------------------   

                else:
                    print("Directory check complete: no content found.")
            else:
                print("This is not directory path")

        return folder_tree_data_lst

    def get_project_extension(self, proj_code):
        """
        Fetch all extensions configured for a given project.

        Args:
            proj_code (str): Project code.

        Returns:
            list: List of supported extensions for the project.
        """
        try:
            with open(con.CONFIG_FILEPATH, "r") as f:
                data = json.load(f)

            project = data.get(proj_code)
            if project:
                return project.get("extension", [])
            else:
                print(f"Project '{proj_code}' not found.")
                return []
        except Exception as e:
            print(f"Error reading JSON: {e}")
            return []

    def fetch_project_extensions(self, selected_proj):
        """
        Fetch only enabled extensions for a given project.

        Args:
            selected_proj (str): Project code.

        Returns:
            list: List of enabled extension strings.
        """
        with open(con.CONFIG_FILEPATH, "r") as rd:
            config_data = json.load(rd)

        raw_ext_dict = config_data[selected_proj]['extension']
        supported_ext_lst = []
        
        for ext_key in raw_ext_dict.keys():
            if raw_ext_dict[ext_key] == True:
                supported_ext_lst.append(ext_key)

        return supported_ext_lst


    def get_thumbnil_wid_lst(self, item: QTreeWidgetItem, column: int):
        """
        Build a list of thumbnail widgets for files in the selected directory.

        Args:
            item (QTreeWidgetItem): The tree item selected.
            column (int): Column index (unused but required by Qt signal/slot).

        Returns:
            tuple: (list of thumbnail widgets, directory path, status message)
        """
        parts = []
        it = item
  
        while it is not None:
            parts.append(it.text(0))
            it = it.parent()
 
        parts.reverse()
        self.thumbnil_dir_path = os.path.join(self.drive + os.sep, *parts)
        proj_code = parts[1]

        if len(parts) >= 2:
            ext_list = self.fetch_project_extensions(proj_code)
            ext_tuple = tuple(ext_list)
        
            thumbnil_data_dict_lst = []
            thumb_dir_name = ''
            is_available_in_dir = False

            if os.path.isdir(self.thumbnil_dir_path):
                thumb_dir_name = self.thumbnil_dir_path
                    
                if not is_available_in_dir:
                    is_available_in_dir = True                

                for file_name in os.listdir(self.thumbnil_dir_path):
                    if file_name.lower().endswith(ext_tuple):
                        thumbnil_data_dict = self.get_thumb_data_dict(file_name, is_thumb_dir=True)
                        thumbnil_data_dict_lst.append(thumbnil_data_dict)
                        
            elif os.path.isfile(self.thumbnil_dir_path):
                thumb_dir_name = os.path.dirname(self.thumbnil_dir_path)
                file_name = re.split(r"[\\/]", self.thumbnil_dir_path)[-1]
                if file_name.lower().endswith(ext_tuple):
                    thumbnil_data_dict = self.get_thumb_data_dict(file_name, is_thumb_dir=False)
                    thumbnil_data_dict_lst.append(thumbnil_data_dict)

            if thumbnil_data_dict_lst:
                thumb_wid_lst = []

                for img_data_dict in thumbnil_data_dict_lst:
                    self.thumbnil_widget = thumbnil_container.ThumbnilWidget(img_data_dict)
                    thumb_wid_lst.append(self.thumbnil_widget)
                        
                if thumb_wid_lst:
                    msg = "Images found."
                    return thumb_wid_lst, thumb_dir_name, msg
            else:
                if is_available_in_dir:
                    msg = "No images found in the directory." 
                    return [], self.thumbnil_dir_path, msg
                else:
                    msg = f"Invalid or unsupported image format - [{file_name.split('.')[-1]}]"
                    return [], self.thumbnil_dir_path, msg        
        else: 
            msg = "Please select a project or a post-prefix directory."
            return [], self.thumbnil_dir_path, msg
         
    def get_thumb_data_dict(self, file_name, is_thumb_dir=None):
        """
        Generate metadata dictionary for a thumbnail image.

        Args:
            file_name (str): Name of the file.
            is_thumb_dir (bool): Whether file is inside a directory.

        Returns:
            dict: Metadata including title, full path, frame range, project and shot code.
        """
        thumbnil_data_dict = {}
        
        if is_thumb_dir:
            image_full_path = os.path.join(self.thumbnil_dir_path, file_name)
        else:
            image_full_path = self.thumbnil_dir_path

        thumbnil_data_dict['lbl_title'] = file_name.split('.')[0]
        thumbnil_data_dict['image_full_path'] = image_full_path
        thumbnil_data_dict['first_frame'] = random.randint(1001, 1009)
        thumbnil_data_dict['last_frame'] = random.randint(1100, 1200)
        
        thumbnil_data_dict['prj_code'] = re.split(r"[\\/]", image_full_path)[2]
        thumbnil_data_dict['shot_code'] =re.split(r"[\\/]", image_full_path)[5]

        return thumbnil_data_dict
            

    def get_current_preferences(self):
        try:
            with open(con.CONFIG_FILEPATH, "r") as f:
                data = json.load(f)
                print(f"Successful read JSON file")
                return data

        except Exception as e:
            print(f"Error reading JSON: {e}")
            return []        

    def overwrite_config(self, new_extensions, selected_proj):
        """
        Overwrite project extension configuration.

        Args:
            new_extensions (list): List of enabled extensions.
            selected_proj (str): Project code to update.

        Returns:
            None
        """
        with open(con.CONFIG_FILEPATH, 'r') as f:
            data = json.load(f)

        for ext_item in data[selected_proj]["extension"].keys():
            if ext_item in new_extensions:
                data[selected_proj]["extension"][ext_item] = True
            else:
                data[selected_proj]["extension"][ext_item] = False

        with open(con.CONFIG_FILEPATH, 'w') as f:
            json.dump(data, f, indent=4)
        print(f"Updated extensions for {selected_proj}: {new_extensions}")


    

   

   