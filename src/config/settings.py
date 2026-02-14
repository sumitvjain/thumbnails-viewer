from config import constant
import os
import json


con = constant.Constant()

def create_json_file(app_dir_path):
    """
    Create a default JSON configuration file in the specified application directory.

    The configuration file contains 10 sample projects ("proj_01" to "proj_10"),
    each with:
        - A project name (e.g., "Project_01")
        - An extension dictionary where each available extension is mapped
          to a boolean indicating whether it's enabled by default.

    Args:
        app_dir_path (str): Path to the application directory where the JSON file 
                            should be created.

    Returns:
        None
    """
    jsn_fle_pth = os.path.join(app_dir_path, con.CONFIG_FILENAME)
    project = {}

    for num in range(1, 11):
        extension_dict = {ext: (ext in con.DEFAULT_ENABLED_EXTS) for ext in con.AVAILABLE_EXTENSIONS}
        project[f"proj_{num:02}"] = {
            "name" : f"Project_{num:02}",
            "extension": extension_dict
        }

        with open(jsn_fle_pth, "w") as json_file:
            json.dump(project, json_file, indent=4)
 

def setup_config():
    """
    Ensure that the application's configuration directory and config file exist.

    - Creates the configuration directory if it doesn't exist.
    - Creates the default JSON configuration file if it's missing.

    Returns:
        None
    """
    config_dir_path = os.path.dirname(con.CONFIG_FILEPATH)

    if not os.path.exists(config_dir_path):
        os.makedirs(config_dir_path)
        create_json_file(config_dir_path)

    elif not con.CONFIG_FILENAME in os.listdir(config_dir_path):
        create_json_file(config_dir_path)
 