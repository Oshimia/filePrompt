import os
import json

LLM_INTERPRETATION_GUIDE_TEXT = """This document is a token-efficient representation of a codebase. Interpret it as follows:

- HIERARCHY: Indentation represents the directory structure.
- DIRECTORIES: A line ending with a forward slash `/` is a directory.
- FILES: A line not ending in a slash is a file within the directory defined by its indentation level.
- FILE CONTENT:
  - Textual content for a file is preceded by a `---[FILE_CONTENT]---` marker on the line immediately following the filename. The content begins on the next line.
  - The content has been processed to remove comments and reduce whitespace.
- SPECIAL FILE TAGS: Some files are represented by a single-line tag on the line after the filename:
  - `[SUMMARY_JSON] {"key":"value",...}`: A compact, single-line JSON summary of a configuration file (e.g., package.json).
  - `[BINARY]`: A binary file whose content is not included.
  - `[IGNORED]`: File was ignored due to filtering rules (e.g., minified file, lock file, SVG).
  - `[ERROR] message...`: An error occurred while reading or processing the file."""

DEFAULT_CONFIG = {
    "output_dir": "scan_results",
    "output_filename": "scan_output.txt",
    "text_extensions": [
        ".txt", ".py", ".js", ".json", ".html", ".css", ".md", ".xml",
        ".csv", ".ini", ".cfg", ".log", ".rst", ".yml", ".yaml", ".tex",
        ".java", ".c", ".cpp", ".h", ".hpp", ".sh", ".bat", ".rb", ".php", ".jsx",
        ".pl", ".sql", ".cs", ".go", ".rs", ".swift", ".kt", ".scala", ".jsw", ".vb", ".example", ".ts"
    ],
    "included_hidden_filenames": [".env.example"],
    "ignored_folders": ["node_modules", "venv", "__pycache__", ".git", ".vscode", ".idea", "playwright-report"],
    "ignored_filenames": ["package-lock.json", "yarn.lock", "pnpm-lock.yaml", "composer.lock"],
    "ignored_extensions": [".svg", ".lock"],
    "llm_interpretation_guide": LLM_INTERPRETATION_GUIDE_TEXT,
    "summarization_rules": {
        "by_filename": {
            "package.json": "summarize_json",
            "jsconfig.json": "summarize_json",
            "tsconfig.json": "summarize_json"
        },
        "by_extension": {},
        "default_strategy": "full_content"
    }
}

def load_config(config_path="config.json"):
    """Loads configuration from a JSON file, creating it with defaults if it doesn't exist."""
    if not os.path.exists(config_path):
        print(f"Configuration file '{config_path}' not found. Creating it with default values.")
        try:
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(DEFAULT_CONFIG, f, indent=2)
            config_data = DEFAULT_CONFIG
        except Exception as e:
            print(f"Error creating default config file: {e}. Using internal defaults.")
            config_data = DEFAULT_CONFIG
    else:
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config_data = json.load(f)
        except (json.JSONDecodeError, Exception) as e:
            print(f"Error reading or parsing '{config_path}': {e}. Using internal defaults.")
            config_data = DEFAULT_CONFIG

    # NEW: Check for the "default" trigger for the LLM guide
    if config_data.get("llm_interpretation_guide") == "default":
        config_data["llm_interpretation_guide"] = LLM_INTERPRETATION_GUIDE_TEXT

    # Convert lists from JSON to sets for efficient lookups
    for key in ['text_extensions', 'included_hidden_filenames', 'ignored_folders', 'ignored_filenames', 'ignored_extensions']:
        config_data[key] = set(config_data.get(key, []))
    return config_data