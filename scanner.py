import os
from summarizer import summarize_file

def is_text_file(file_path, config):
    """Checks if a file is considered a text file based on its extension."""
    return os.path.splitext(file_path)[1].lower() in config['text_extensions']

def scan_folder_token_efficient(folder_path, config, indent_level=0, is_root=False):
    """
    Recursively scans a folder and returns a list of strings
    in the token-efficient "Compact Tree" format.
    """
    output_lines = []

    # If this is the root folder of a scan, add its name to the output.
    if is_root:
        pass # The root directory name is now handled by the header in filePrompt.py

    indent_str = "  " * indent_level
    child_indent_str = "  " * (indent_level + 1)

    try:
        # Sort items to have directories first, then files, all alphabetically.
        dir_items = sorted(os.listdir(folder_path), key=lambda x: (not os.path.isdir(os.path.join(folder_path, x)), x.lower()))
    except OSError as e:
        return [f"{indent_str}[ERROR] Could not read directory {folder_path}: {e}"]

    for item_name in dir_items:
        if item_name.startswith('.') and item_name not in config['included_hidden_filenames']:
            continue
        
        item_path = os.path.join(folder_path, item_name)

        if os.path.isdir(item_path):
            if item_name in config['ignored_folders']:
                continue
            output_lines.append(f"{indent_str}{item_name}/")
            child_lines = scan_folder_token_efficient(item_path, config, indent_level + 1, is_root=False)
            output_lines.extend(child_lines)

        elif os.path.isfile(item_path):
            file_ext = os.path.splitext(item_name)[1].lower()
            
            if (item_name in config['ignored_filenames'] or
                file_ext in config['ignored_extensions'] or
                ".min." in item_name):
                output_lines.append(f"{indent_str}{item_name}")
                output_lines.append(f"{child_indent_str}[IGNORED]")
                continue
            
            output_lines.append(f"{indent_str}{item_name}")
            
            if is_text_file(item_path, config):
                try:
                    with open(item_path, "r", encoding="utf-8", errors='ignore') as file:
                        content_str = file.read()
                    output_lines.extend(summarize_file(content_str, item_name, config))
                except Exception as e:
                    print(f"Error reading or processing {item_path}: {e}")
                    output_lines.append(f"{child_indent_str}[ERROR] {e}")
            else: 
                output_lines.append(f"{child_indent_str}[BINARY]")
                
    return output_lines