# filePrompt: A Codebase Scanner for LLMs

A Python script that scans a project directory and creates a single, token-efficient text file representing the entire codebase. This output is specifically formatted to be easily parsed and understood by Large Language Models (LLMs) like GPT-4, Gemini, Claude, and others.

The primary goal is to provide a clean, context-rich representation of a project that can be easily pasted into an LLM prompt, overcoming token limits and removing irrelevant "noise" like comments, `node_modules`, and lock files. This is intended for small to medium sized projects that can fit into an LLM context window, and as such does not have a token limit, or truncation logic to cut down on the output length. 

## The Problem It Solves

When working with LLMs, you often need to provide them with the context of your codebase. However, you face several challenges:
*   **Token Limits:** Pasting entire files can quickly exceed the model's context window.
*   **Noise:** Comments, excessive whitespace, build artifacts, and dependency folders (`node_modules`) consume valuable tokens without adding useful context.
*   **Structure:** It's difficult to convey the directory structure and file relationships in a simple text format.

This script addresses these issues by creating a compact, hierarchical representation of your codebase, intelligently filtering out noise and summarizing key configuration files.

## Features

*   **Recursive Directory Scanning:** Traverses the entire folder structure of your project.
*   **Intelligent Filtering:**
    *   Ignores common boilerplate folders like `.git`, `node_modules`, `venv`, and `__pycache__`.
    *   Skips lock files (`package-lock.json`, `yarn.lock`, etc.).
    *   Excludes binary files and low-value text files like SVGs.
    *   Allows for a configurable "include list" for specific hidden files (e.g., `.env.example`).
*   **Content Processing:**
    *   Removes comments from a wide range of languages (Python, JavaScript, Java, C-style, HTML, etc.).
    *   Normalizes whitespace to reduce token count.
*   **Smart Summaries:** Condenses important files like `package.json` into a single-line JSON summary of key fields (dependencies, scripts).
*   **Configurable:** All rules—ignored folders, files, extensions, and included hidden files—are defined in simple sets at the top of the script for easy customization.
*   **Cross-Platform:** Built with standard Python libraries to run on Windows, macOS, and Linux.

## The Output Format

The script generates a `scan_output.txt` file with a custom format designed for LLM interpretation. The file begins with a guide explaining the structure.

```
This document is a token-efficient representation of a codebase. Interpret it as follows:

- HIERARCHY: Indentation represents the directory structure.
- DIRECTORIES: A line ending with a forward slash `/` is a directory.
- FILES: A line not ending in a slash is a file within the directory defined by its indentation level.
- FILE CONTENT:
  - Textual content for a file is enclosed between `---[FILE_CONTENT]---` markers that appear on the lines immediately following the filename.
  - The content has been processed to remove comments and reduce whitespace.
- SPECIAL FILE TAGS: Some files are represented by a single-line tag on the line after the filename:
  - `[SUMMARY_JSON] {"key":"value",...}`: A compact, single-line JSON summary of a configuration file (e.g., package.json).
  - `[BINARY]`: A binary file whose content is not included.
  - `[IGNORED]`: File was ignored due to filtering rules (e.g., minified file, lock file, SVG).
  - `[ERROR] message...`: An error occurred while reading or processing the file.
```

### Example Output Snippet

```
my-project/
  .env.example
    ---[FILE_CONTENT]---
    DB_HOST=localhost
    DB_USER=root
    DB_PASS=
    ---[FILE_CONTENT]---
  package.json
    [SUMMARY_JSON] {"name":"my-project","version":"1.0.0","dependencies":{"express":"^4.17.1"},"devDependencies":{"nodemon":"^2.0.15"}}
  src/
    index.js
      ---[FILE_CONTENT]---
      const express = require('express');
      const app = express();
      const port = 3000;

      app.get('/', (req, res) => {
        res.send('Hello World!');
      });

      app.listen(port, () => {
        console.log(`Example app listening at http://localhost:${port}`);
      });
      ---[FILE_CONTENT]---
```

## How to Use

### Prerequisites
*   [Python 3.6+](https://www.python.org/downloads/)

### Option 1: Run as a Python Script

1.  Save the script as `llm_scanner.py`.
2.  Open your terminal or command prompt.
3.  Run the script in one of two ways:

    *   **Interactive Mode:**
        ```bash
        python llm_scanner.py
        ```
        The script will prompt you to enter the path to the folder you want to scan.

    *   **Command-Line Argument:**
        ```bash
        python llm_scanner.py "path/to/your/project"
        ```
        Replace `"path/to/your/project"` with the actual folder path.

The output will be saved to a file named `scan_output.txt` in the same directory where you run the command.

### Option 2: Run as a Standalone Executable (Windows)

You can package the script into a single `.exe` file that runs on any Windows machine, even without Python installed.

1.  **Install PyInstaller:**
    ```bash
    pip install pyinstaller
    ```
2.  **Create the executable:**
    Navigate to the directory containing the script and run:
    ```bash
    pyinstaller --onefile llm_scanner.py
    ```
3.  **Find the executable:**
    Your `.exe` file will be in the `dist` folder.

You can now run the executable in several ways:
*   **Drag and Drop:** Drag your project folder and drop it directly onto the `.exe` file.
*   **Double-Click:** Double-click the `.exe` to run it in interactive mode.
*   **Command Line:** Use it from the command line just like the Python script:
    ```cmd
    llm_scanner.exe "path/to/your/project"
    ```

## Configuration

This script is designed to be easily configured without needing to understand all the code. Open the script file and modify the configuration sets at the top to fit your needs.

```python
# --- Configuration ---

# Define which extensions should be treated as text files.
TEXT_EXTENSIONS = {'.txt', '.py', '.js', ...}

# --- ADVANCED IGNORE/FILTER RULES ---

# NEW: Specific hidden files to ALWAYS include
INCLUDED_HIDDEN_FILENAMES = {'.env.example'}

# Folders to completely ignore
IGNORED_FOLDERS = {'node_modules', 'venv', '__pycache__', '.git', ...}

# Specific filenames to ignore entirely
IGNORED_FILENAMES = {'package-lock.json', 'yarn.lock', ...}

# Extensions to ignore, even if they are text-based (high token, low value)
IGNORED_EXTENSIONS = {'.svg', '.lock'}
```

## License

This project is licensed under the [Creative Commons Attribution-NonCommercial 4.0 International License (CC BY-NC 4.0)](http://creativecommons.org/licenses/by-nc/4.0/).

![CC BY-NC 4.0](https://i.creativecommons.org/l/by-nc/4.0/88x31.png)

You are free to:
- **Share** — copy and redistribute the material in any medium or format
- **Adapt** — remix, transform, and build upon the material

Under the following terms:
- **Attribution** — You must give appropriate credit, provide a link to the license, and indicate if changes were made.
- **NonCommercial** — You may not use the material for commercial purposes.

To be clear, this is used to stop the commercialization of this as a product. Any and all personal use is allowed, with or without attribution. 