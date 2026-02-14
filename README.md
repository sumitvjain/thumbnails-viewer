# 🚀 Thumbnail Viewer Tool - (Documentation for user)

We’re excited to introduce the **Thumbnail Viewer Tool** — designed to quickly check annotations and thumbnails of each shot across sequences and projects, with smart filtering based on annotation file extensions.

🎥 *See the attached GIF for a quick walkthrough of the tool in action.*

---

## 🔎 What Problem Does It Solve?

Managing multiple shots across sequences and projects can become time-consuming when verifying:

- Shot thumbnails  
- Annotation files  
- File format consistency  
- Project-wise filtering  

The **Thumbnail Viewer Tool** simplifies this entire process in a clean, structured, and efficient way.

---

## ✨ Key Features

### 📂 1. Easy Image Loading

- Drag & drop a folder into the application  
- Automatically displays supported image formats as thumbnails  
- Smart filtering ensures only valid files are shown  

---

### 🖼️ 2. Thumbnail Preview with Metadata

Each thumbnail displays:

- Image Name  
- Project Code  
- Short Code  

This enables faster identification and validation without opening files individually.

---

### 🔍 3. Advanced Viewing Options

- Double-click a thumbnail to open it in the **Viewer Tab**  
- Zoom in/out using:
  - Mouse scroll wheel  
  - `+` key to zoom in  
  - `-` key to zoom out  
- Right-click option to load directly in Viewer  
- Centered and scalable preview for detailed inspection  

---

### 🗑️ 4. Smart Removal (Non-Destructive)

- Select one or multiple thumbnails  
- Remove them from the widget view  
- Files remain safe on disk  

---

### ⚙️ 5. Project-Based Preferences & Annotation Filter

- Configure project settings  
- Select supported annotation extensions (file formats)  
- Filter thumbnails based on required annotation types  
- Reload folder to apply updated preferences  

This allows teams to quickly verify specific annotation formats per project or sequence.

---

## 💡 Why It’s Useful

- ✔ Speeds up shot review  
- ✔ Ensures annotation format consistency  
- ✔ Reduces manual verification effort  
- ✔ Organized sequence-wise inspection  
- ✔ Lightweight and user-friendly  

---

## 🎯 Ideal For

- VFX / Post-Production Teams  
- Pipeline Developers  
- QC Artists  
- Project Coordinators  
- Shot Review Workflows  

---

## 🤝 Feedback & Contributions

We built this tool to improve visibility, speed, and accuracy in annotation checking workflows.

Your feedback and suggestions are always welcome!

---

## 🔖 Tags

`#VFX` `#PipelineDevelopment` `#Automation` `#PythonTools` `#WorkflowOptimization` `#ThumbnailViewer` `#PostProduction`


---


# 🎬 Thumbnails-Viewer - (Documentation Developer)

A Python-based **Thumbnails-Viewer** designed for VFX/Animation pipelines.  
It provides a simple interface to browse, organize, and preview assets such as images, sequences, and videos.  

The project uses **PySide2 (Qt for Python)** for the UI and supports customizable project configurations via JSON.

---

## 🚀 Features
- 📂 Drag-and-drop support for files and folders  
- 🖼️ Thumbnail previews of supported media files (`exr`, `jpg`, `jpeg`, `png`, `mov`)  
- 📑 Project-based extension filtering (customizable per project)  
- ⚡ Zoom in/out functionality on the preview tab (Using mouse-middle button and keyboard minus,plus button) 
- 🔄 Load, Remove context menu actions for thumbnil widgets in list  
- ⚙️ Preferences dialog to update project configurations  
- 📝 Config file auto-generated on first launch  

---

## 📦 Requirements
- Python **3.8+**  
- [PySide2](https://pypi.org/project/PySide2/)  
- [platformdirs](https://pypi.org/project/platformdirs/)  

Install dependencies with:

```bash
pip install -r requirements.txt
```

---

## 🛠️ Setup
When first run, the application will:
1. Create a hidden directory inside your **Documents folder** (`~/.app/`)  
2. Generate a default `config.json` file with 10 sample projects  

---

## ▶️ Run the App
```bash
python main.py
```

---

## 📝 Example: Default Config File (`config.json`)
```json
{
    "proj_01": {
        "name": "Project_01",
        "extension": {
            "exr": false,
            "jpeg": true,
            "jpg": true,
            "png": false,
            "mov": false
        }
    },
    "proj_02": {
        "name": "Project_02",
        "extension": {
            "exr": false,
            "jpeg": true,
            "jpg": true,
            "png": false,
            "mov": false
        }
    }
}
```

---

## 📂 Project Structure
```
asset-manager/
│── config/
│   ├── constant.py        # Centralized constants
│   ├── setup_config.py    # Ensures config.json exists
│
│── model/                 # Data and logic layer
│── view/                  # UI layer (PySide2 widgets)
│── controller/            # Business logic and signal-slot connections
│
│── style.qss              # UI styling
│── main.py                # Entry point
│── requirements.txt
│── README.md
```

---

## 🖥️ Example Workflow
1. Launch the app → it creates the default config at `~/Documents/.app/config.json`  
2. Drag and drop a folder with assets into the UI  
3. The **Tree widget** displays the folder structure → click an item to view thumbnails  
4. Right-click thumbnails to access options:  
   - **Load in Viewer**  
   - **Remove**  

---

## 👨‍💻 Author
**Sumit Saktepar**  
Pipeline TD / Python Developer  
