# Environment Setup

This project requires **Python 3.12**. We recommend using a virtual environment so that Python packages used for the exercises do not interfere with other projects.

## Prerequisites

1. **Python 3.12**: Download from https://www.python.org/downloads/release/python-31210/
2. **Git**: Required for cloning the repository
   - Windows users: Install Git for Windows from https://git-scm.com/download/win

## Creating a Virtual Environment

1. Clone the repository from GitLab:
   ```bash
   git clone https://gitlab.ethz.ch/{your_repo_url}
   cd {project_directory}
   ```

2. Create and activate a virtual environment:
   ```bash
   # On Windows
   py -3.12 -m venv venv
   .\venv\Scripts\activate

   # On Linux/macOS
   python3.12 -m venv venv
   source venv/bin/activate
   ```

## Installing Dependencies

Install the project and all required dependencies:

```bash
pip install -e .
```

To use the optional HiGHS solver backend (recommended for better performance):

```bash
pip install highspy
```

## Verifying Your Setup

Run the tests in `test_cmap.py` to ensure that your environment is ready:

```bash
pytest test/test_cmap.py -v
```

All tests should pass. If you encounter issues, verify that:
- You are using Python 3.12
- Your virtual environment is activated
- All dependencies installed successfully

---

## VSCode Setup (Optional)

If you choose to use Visual Studio Code, follow these steps to configure it for this project.

### Installing VSCode

1. Download and install VSCode from https://code.visualstudio.com/
2. Open VSCode and install the following extensions:

**Required Extensions:**
- **Python** (by Microsoft)
- **Black Formatter** (by Microsoft)

**Recommended Extensions:**
- **GitLens** - Enhanced Git integration
- **Git Graph** - Visual commit history
- **vscode-icons** - Better file icons
- **Live Share** - Real-time collaboration (optional)

### Configuring the Python Environment

1. Open the project folder in VSCode
2. Open any Python file (e.g., `line_planning.py`)
3. Check the **Python interpreter** in the lower-right corner of VSCode
   - It should show your virtual environment (e.g., `venv`)
   - If not, click on it and select the interpreter from your `venv` folder
4. Open a new terminal in VSCode (**Terminal → New Terminal**)
   - The virtual environment should be automatically activated
   - You should see `(venv)` at the beginning of the command prompt
   - If the old terminal doesn't show `(venv)`, close it and open a new one

### Configuring Code Quality Settings

Configure the following settings in VSCode to maintain code quality:

1. Open VSCode settings:
   - **File → Preferences → Settings** (Windows/Linux)
   - **Code → Settings → Settings** (macOS)
   - Or press `Ctrl+,` (Windows/Linux) or `Cmd+,` (macOS)

2. Search for and configure these settings:

   **Type Checking:**
   - Search: `python.analysis.typeCheckingMode`
   - Set to: `standard`

   **Code Formatting:**
   - Search: `editor.defaultFormatter`
   - For Python files, set to: `ms-python.black-formatter`
   - Search: `editor.formatOnSave`
   - Enable: `☑ Format On Save`

**Tip:** You can configure these settings at different levels:
- **User**: Applies to all projects
- **Workspace**: Applies to your current workspace (if using multiple folders)
- **Folder**: Applies only to the current project folder

For this project, we recommend setting these at the **Folder** level so they don't affect other Python projects.
