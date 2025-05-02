import sys
import shutil
import os

def main():
    if len(sys.argv) != 2:
        print("Usage: create_archive.py <version>")
        sys.exit(1)
    version = sys.argv[1]
    source_dir = os.path.join('dist', 'app')
    if not os.path.exists(source_dir):
        print(f"Error: Source directory '{source_dir}' does not exist.")
        sys.exit(1)
    archive_path = os.path.join('dist', f"pintura_{version}")
    shutil.make_archive(archive_path, 'zip', source_dir)
    print(f"Successfully created archive: {archive_path}.zip")

if __name__ == "__main__":
    main()