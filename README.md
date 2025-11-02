# filePrompt: A Modular Codebase Scanner for LLMs

A modular Python script that scans one or more project directories and creates a single, token-efficient text file representing the entire codebase. This output is specifically formatted to be easily parsed and understood by Large Language Models (LLMs) like GPT-4, Gemini, Claude, and others.

The primary goal is to provide a clean, context-rich representation of a project that can be easily pasted into an LLM prompt, overcoming token limits and removing irrelevant "noise" like comments, `node_modules`, and lock files.

## The Problem It Solves

When working with LLMs, you often need to provide them with the context of your codebase. However, you face several challenges:
*   **Token Limits:** Pasting entire files can quickly exceed the model's context window.
*   **Noise:** Comments, excessive whitespace, build artifacts, and dependency folders (`node_modules`) consume valuable tokens without adding useful context.
*   **Structure:** It's difficult to convey the directory structure and file relationships in a plain text format.

This script addresses these issues by creating a compact, hierarchical representation of your codebase, intelligently filtering out noise and summarizing key configuration files.

## Features

*   **Recursive Directory Scanning:** Traverses the entire folder structure of your project.
*   **Fully Configurable via JSON:** All filtering rules, output settings, and even the LLM guide text are managed in a `config.json` file.
*   **Intelligent Filtering:** Ignores common boilerplate folders, specific filenames, and file extensions by default.
*   **Content Processing:**
    *   Removes comments from a wide range of languages (Python, JavaScript, Java, C-style, HTML, etc.).
    *   Normalizes whitespace to reduce token count.
*   **Configurable Summarization Engine:** Summarizes key files like `package.json` into a compact format. This is extensible, allowing you to define new summarization strategies for different file types.
*   **Multi-Directory Scanning:** Scan multiple project folders in a single command, with the output clearly delineated by root directory headers.
*   **Cross-Platform:** Built with standard Python libraries to run on Windows, macOS, and Linux.
*   **Modular Architecture:** The codebase is broken into logical modules for configuration, scanning, and content processing, making it easy to understand and extend.

## The Output Format

The script generates an output file (e.g., `scan_output.txt`) with a custom format designed for LLM interpretation. The file begins with a guide explaining the structure.

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

### Running the Script
1.  Open your terminal or command prompt.
2.  Run the script in one of two ways:

    *   **Interactive Mode:**
        ```bash
        python filePrompt.py
        ```
        The script will prompt you to enter one or more folder paths. Press Enter on an empty line when you are finished.

    *   **Command-Line Argument:**
        ```bash
        python filePrompt.py "path/to/project1" "path/to/project2"
        ```
        Replace the paths with the actual folder paths you want to scan.

The output will be saved to a directory and filename specified in your `config.json` (by default, `scan_results/scan_output.txt`).

### Creating an Executable

To create a standalone executable from the source code, you will need `pyinstaller`.

1.  **Install PyInstaller:**
    ```bash
    pip install pyinstaller
    ```

2.  **Run the Build Script:**
    ```bash
    python build.py
    ```

This will create a single executable file inside a `dist` directory.

## Configuration

The script's behavior is controlled by a `config.json` file. When you run the script for the first time, it will automatically create a `config.json` file in the same directory with default settings if one doesn't already exist.

You can customize the scanning process by editing this file.

### Example `config.json`

```json
{
  "output_dir": "scan_results",
  "output_filename": "scan_output.txt",
  "text_extensions": [
    ".txt",
    ".py",
    ".js",
    ".json"
  ],
  "included_hidden_filenames": [
    ".env.example"
  ],
  "ignored_folders": [
    "node_modules",
    "venv",
    "__pycache__",
    ".git"
  ],
  "ignored_filenames": [
    "package-lock.json"
  ],
  "ignored_extensions": [
    ".svg",
    ".lock"
  ],
  "summarization_rules": {
    "by_filename": {
      "package.json": "summarize_json"
    }
  }
}
```

**Key Configuration Options:**
*   `output_dir` & `output_filename`: Where to save the final scan result.
*   `text_extensions`: A list of file extensions to be treated as text and have their content included.
*   `included_hidden_filenames`: A list of specific hidden files (e.g., `.env.example`) to always include, even if they would normally be ignored.
*   `ignored_folders`, `ignored_filenames`, `ignored_extensions`: Rules to filter out specific items.
*   `summarization_rules`: Defines strategies for handling specific files (e.g., summarizing `package.json` instead of including its full content).

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