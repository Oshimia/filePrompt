import os
import json
import re

# --- Configuration ---

# Define which extensions should be treated as text files.
TEXT_EXTENSIONS = {
    '.txt', '.py', '.js', '.json', '.html', '.css', '.md', '.xml',
    '.csv', '.ini', '.cfg', '.log', '.rst', '.yml', '.yaml', '.tex',
    '.java', '.c', '.cpp', '.h', '.hpp', '.sh', '.bat', '.rb', '.php',
    '.pl', '.sql', '.cs', '.go', '.rs', '.swift', '.kt', '.scala', '.jsw', '.vb', '.example'
}

# --- ADVANCED IGNORE/FILTER RULES ---
# Folders to completely ignore
IGNORED_FOLDERS = {'node_modules', 'venv', '__pycache__', '.git', '.vscode', '.idea'}

# Specific hidden files to ALWAYS include
INCLUDED_HIDDEN_FILENAMES = {'.env.example'}

# Specific filenames to ignore entirely
IGNORED_FILENAMES = {
    'package-lock.json', 'yarn.lock', 'pnpm-lock.yaml', 'composer.lock'
}

# Extensions to ignore, even if they are text-based (high token, low value)
IGNORED_EXTENSIONS = {
    '.svg', '.lock'  # Treat SVG as a non-content file, and ignore any other .lock files
}

# --- LLM Interpretation Guide (Token-Efficient Format) ---
LLM_INTERPRETATION_GUIDE = """
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
"""

# --- Helper Functions for Content Processing (Unchanged) ---

def remove_comments_from_line(line, comment_marker):
    """Removes comments from a single line given a single-line comment marker."""
    try:
        return line.split(comment_marker, 1)[0].rstrip()
    except:
        return line.rstrip()

def remove_c_style_multiline_comments(code):
    """Removes /* ... */ comments."""
    return re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)

def remove_html_xml_comments(code):
    """Removes <!-- ... --> comments."""
    return re.sub(r'<!--.*?-->', '', code, flags=re.DOTALL)

def process_code_content(content_str, file_ext):
    """Removes comments and normalizes whitespace for known code types."""
    lines = content_str.splitlines()
    processed_lines = []
    
    if file_ext in ['.js', '.jsw', '.css', '.c', '.cpp', '.java', '.cs', '.go', '.rs', '.swift', '.kt', '.scala', '.h', '.hpp']:
        content_str = remove_c_style_multiline_comments(content_str)
        lines = content_str.splitlines()

    if file_ext in ['.xml', '.html']:
        content_str = remove_html_xml_comments(content_str)
        lines = content_str.splitlines()

    in_python_multiline_string = False
    
    for i, line in enumerate(lines):
        original_line_for_shebang = line
        
        if file_ext in ['.py', '.sh', '.rb', '.pl', '.yml', '.yaml', '.ini', '.cfg', '.bat']:
            if file_ext == '.py':
                if '"""' in line:
                    if line.count('"""') % 2 != 0: 
                        in_python_multiline_string = not in_python_multiline_string
                elif "'''" in line:
                    if line.count("'''") % 2 != 0:
                        in_python_multiline_string = not in_python_multiline_string
            
            if not in_python_multiline_string and '#' in line:
                if i == 0 and (original_line_for_shebang.startswith("#!") or original_line_for_shebang.startswith("::#")):
                     line = original_line_for_shebang.rstrip()
                else:
                    stripped_line_for_hash = line.strip()
                    if stripped_line_for_hash.startswith('#'):
                        if not processed_lines or processed_lines[-1].strip() != "":
                            processed_lines.append("") 
                        continue
                    else:
                        line = remove_comments_from_line(line, '#')
            elif in_python_multiline_string and file_ext == '.py':
                pass

        elif file_ext in ['.js', '.jsw', '.c', '.cpp', '.java', '.cs', '.go', '.rs', '.swift', '.kt', '.scala', '.h', '.hpp']:
            if '//' in line:
                idx = line.find('//')
                single_quotes_before = line[:idx].count("'")
                double_quotes_before = line[:idx].count('"')
                if (single_quotes_before % 2 == 0) and (double_quotes_before % 2 == 0):
                    line = remove_comments_from_line(line, '//')
        
        if line.strip() or (processed_lines and processed_lines[-1].strip()):
            processed_lines.append(line.rstrip())

    final_lines = []
    for i, line_item in enumerate(processed_lines):
        if line_item.strip() == "" and (i > 0 and not final_lines[-1].strip()):
            continue 
        final_lines.append(line_item)
        
    return "\n".join(final_lines)

# --- JSON Summary Helper (Unchanged) ---
def get_json_summary(data, filename):
    if filename == "package.json":
        summary = {
            "name": data.get("name"),
            "version": data.get("version"),
            "dependencies": data.get("dependencies"),
            "devDependencies": data.get("devDependencies"),
            "scripts": data.get("scripts")
        }
        return {k: v for k, v in summary.items() if v is not None}
    elif filename in ["jsconfig.json", "tsconfig.json"]:
        summary = {
            "compilerOptions_paths": data.get("compilerOptions", {}).get("paths"),
            "references": data.get("references"),
            "include": data.get("include"),
            "exclude": data.get("exclude"),
            "typeAcquisition": data.get("typeAcquisition")
        }
        return {k: v for k, v in summary.items() if v is not None}
    return data

# --- Core Scanning Logic (with Advanced Filtering) ---

def is_text_file(file_path):
    return os.path.splitext(file_path)[1].lower() in TEXT_EXTENSIONS

def scan_folder_token_efficient(folder_path, indent_level=0):
    """
    Recursively scans a folder and returns a list of strings
    in the token-efficient "Compact Tree" format.
    """
    output_lines = []
    indent_str = "  " * indent_level
    child_indent_str = "  " * (indent_level + 1)

    try:
        dir_items = sorted(os.listdir(folder_path), key=lambda x: (not os.path.isdir(os.path.join(folder_path, x)), x.lower()))
    except OSError as e:
        return [f"{indent_str}[ERROR] Could not read directory {folder_path}: {e}"]

    for item_name in dir_items:
        if item_name.startswith('.') and item_name not in INCLUDED_HIDDEN_FILENAMES:
            continue
        
        item_path = os.path.join(folder_path, item_name)

        if os.path.isdir(item_path):
            if item_name in IGNORED_FOLDERS:
                continue
            output_lines.append(f"{indent_str}{item_name}/")
            child_lines = scan_folder_token_efficient(item_path, indent_level + 1)
            output_lines.extend(child_lines)

        elif os.path.isfile(item_path):
            file_ext = os.path.splitext(item_name)[1].lower()
            
            # --- NEW: Advanced file filtering logic ---
            if (item_name in IGNORED_FILENAMES or
                file_ext in IGNORED_EXTENSIONS or
                ".min." in item_name):
                output_lines.append(f"{indent_str}{item_name}")
                output_lines.append(f"{child_indent_str}[IGNORED]")
                continue # Skip to the next file
            
            output_lines.append(f"{indent_str}{item_name}")
            
            if is_text_file(item_path):
                try:
                    with open(item_path, "r", encoding="utf-8", errors='ignore') as file:
                        content_str = file.read()

                    if file_ext == '.json':
                        try:
                            json_data = json.loads(content_str)
                            summary = get_json_summary(json_data, item_name)
                            if summary is not json_data: # A specific summary was made
                                compact_json = json.dumps(summary, separators=(',', ':'))
                                output_lines.append(f"{child_indent_str}[SUMMARY_JSON] {compact_json}")
                            else: # Not a special JSON, treat as regular text
                                processed_content = process_code_content(content_str, file_ext)
                                output_lines.extend([f"{child_indent_str}---[FILE_CONTENT]---", processed_content, f"{child_indent_str}---[FILE_CONTENT]---"])
                        except json.JSONDecodeError: # Malformed JSON, treat as text
                            processed_content = process_code_content(content_str, file_ext)
                            output_lines.extend([f"{child_indent_str}---[FILE_CONTENT]---", processed_content, f"{child_indent_str}---[FILE_CONTENT]---"])
                    else: # Regular text file
                        processed_content = process_code_content(content_str, file_ext)
                        output_lines.extend([f"{child_indent_str}---[FILE_CONTENT]---", processed_content, f"{child_indent_str}---[FILE_CONTENT]---"])
                except Exception as e:
                    print(f"Error reading or processing {item_path}: {e}")
                    output_lines.append(f"{child_indent_str}[ERROR] {e}")
            else: 
                output_lines.append(f"{child_indent_str}[BINARY]")
                
    return output_lines

# --- Main Execution ---

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        folder = sys.argv[1].strip('"')
    else:
        while True:
            raw_folder_path = input("Enter folder path to scan: ").strip()
            folder = raw_folder_path.strip('"')

            if os.path.isdir(folder):
                break
            else:
                print(f"Error: '{folder}' (derived from '{raw_folder_path}') is not a valid directory. Please try again.")

    print(f"Scanning folder: {folder}...")
    file_structure_lines = scan_folder_token_efficient(folder)
    
    final_output_content = LLM_INTERPRETATION_GUIDE + "\n---\n\n" + "\n".join(file_structure_lines)
    
    output_file = "scan_output.txt"

    try:
        with open(output_file, "w", encoding="utf-8") as out:
            out.write(final_output_content)
        print(f"Scan completed. Filtered output saved to {output_file}")
        print(f"Output size: {os.path.getsize(output_file)} bytes")

    except Exception as e:
        print(f"Error writing output file {output_file}: {e}")