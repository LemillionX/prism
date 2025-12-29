# SBTW - Project Manager

A GUI-based project manager designed for creative workflows, built with PySide6 and QtPy. SBTW helps manage projects, assets, shots, tasks, and files with an intuitive interface and robust metadata handling.

## Features

- **Project Management**: Create and manage multiple projects with structured folder hierarchies
- **Asset & Shot Handling**: Organize and track assets and shots within projects
- **Task Tracking**: Manage tasks with status tracking (Waiting to Start, Retake, On Hold, Work In Progress, Approved)
- **File Management**: Browse and organize project files with metadata
- **Thumbnail Support**: Automatic thumbnail generation and display for visual assets
- **Logging**: Comprehensive logging system with rotating file handlers
- **Configuration**: User-specific configuration and project settings
- **Cross-Platform**: Built with Qt for Windows, macOS, and Linux compatibility

## Installation

### Prerequisites

- Python 3.9 or higher

### Setup

1. Clone or download the project
2. Create a virtual environment:
   ```bash
   python -m venv .venv
   ```
3. Activate the virtual environment:
   - Windows: `.venv\Scripts\activate`
   - macOS/Linux: `source .venv/bin/activate`
4. Install dependencies:
    - Using pip 
   ```bash
   pip install -e .
   ```
    - Using uv
    ```bash
    uv sync
    ```

### Dependencies

- PySide6-Essentials >= 6.10.1
- QtPy >= 2.4.3

## Usage

### Running the Application

After installation, you can run SBTW in several ways:

1. **Direct execution**:
   ```bash
   python -m sbtw.main
   ```

2. **Using the script**:
   ```bash
   sbtw
   ```

### Interface Overview

- **Header**: Displays user name and project selection
- **Browser**: Main view showing assets, tasks, and files
- **Project Structure**: Organized as Assets/Shots → Tasks → Files

### Project Workflow

1. Create a new project through the interface
2. Add assets or shots to your project
3. Create tasks for each asset/shot
4. Upload and manage files within tasks
5. Track progress with status updates

## Build

To create a standalone executable using PyInstaller:

After activating the virtual environment:
```bash
pyinstaller --onefile --windowed --clean --name SBTW --add-data "sbtw/medias;sbtw/medias" sbtw\main.py
```

This will generate a single executable file named `SBTW.exe` (Windows) or `SBTW` (macOS/Linux) in the `dist/` directory.
