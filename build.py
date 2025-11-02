import os
import subprocess
import platform
import shutil
import time

# --- Configuration ---
SCRIPT_NAME = "filePrompt.py"
EXE_NAME = "filePrompt"
OUTPUT_DIR = "dist"
BUILD_DIR = "build"

def main():
    """Runs the PyInstaller build command and cleans up."""
    print("Starting build process...")

    # Construct the PyInstaller command
    command = [
        "pyinstaller",
        "--onefile",
        f"--name={EXE_NAME}",
        f"--distpath={OUTPUT_DIR}",
        f"--workpath={BUILD_DIR}",
        "--clean",
        SCRIPT_NAME,
    ]

    print(f"Running command: {' '.join(command)}")

    try:
        subprocess.run(command, check=True, shell=(platform.system() == 'Windows'))
        print(f"\nBuild successful! Executable is in the '{OUTPUT_DIR}' directory.")
    except FileNotFoundError:
        print("\nError: 'pyinstaller' command not found.")
        print("Please install PyInstaller: pip install pyinstaller")
    except subprocess.CalledProcessError as e:
        print(f"\nAn error occurred during the build process: {e}")
    finally:
        print("Build process finished. Cleaning up temporary files...")
        time.sleep(1) # Add a 1-second delay to allow file handles to be released.

        try:
            if os.path.exists(BUILD_DIR):
                shutil.rmtree(BUILD_DIR)
            spec_file = f"{EXE_NAME}.spec"
            if os.path.exists(spec_file):
                os.remove(spec_file)
            print("Cleanup successful.")
        except PermissionError as e:
            print(f"\nWarning: Could not clean up temporary build files due to a permission error.")
            print(f"Details: {e}")
            print(f"You may need to manually delete the '{BUILD_DIR}' directory and '{EXE_NAME}.spec' file.")

if __name__ == "__main__":
    main()