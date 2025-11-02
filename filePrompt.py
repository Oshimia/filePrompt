import os
import sys
from scanner import scan_folder_token_efficient
from config_loader import load_config

# --- Main Execution ---

if __name__ == "__main__":
    
    config = load_config()
    folders_to_scan = []

    if len(sys.argv) > 1:
        for arg in sys.argv[1:]:
            folder = arg.strip('"')
            if os.path.isdir(folder):
                folders_to_scan.append(folder)
            else:
                print(f"Warning: '{folder}' is not a valid directory. Skipping.")
    else:
        print("Enter folder paths to scan. Press Enter on an empty line when you are done.")
        while True:
            raw_folder_path = input("Path: ").strip()
            if not raw_folder_path:
                break
            folder = raw_folder_path.strip('"')
            if os.path.isdir(folder):
                folders_to_scan.append(folder)
                print(f"  -> Added '{folder}'")
            else:
                print(f"  -> Error: '{folder}' is not a valid directory. Please try again.")

    if not folders_to_scan:
        print("No valid directories to scan. Exiting.")
        sys.exit(1)

    all_file_structure_lines = []
    for i, folder in enumerate(folders_to_scan):
        print(f"Scanning root folder: {folder}...")
        if i > 0:
            all_file_structure_lines.append("") # Add a blank line for separation
        all_file_structure_lines.append(f"---[ROOT_DIRECTORY: {folder}]---")
        all_file_structure_lines.extend(scan_folder_token_efficient(folder, config, is_root=True))
    
    llm_guide = config.get('llm_interpretation_guide', '')
    final_output_content = f"{llm_guide}\n---\n\n" + "\n".join(all_file_structure_lines)
    
    # Create output directory if it doesn't exist
    output_dir = config['output_dir']
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    output_file_path = os.path.join(output_dir, config['output_filename'])

    try:
        with open(output_file_path, "w", encoding="utf-8") as out:
            out.write(final_output_content)
        print(f"Scan completed. Filtered output saved to {output_file_path}")
        print(f"Output size: {os.path.getsize(output_file_path)} bytes")

    except Exception as e:
        print(f"Error writing output file {output_file_path}: {e}")