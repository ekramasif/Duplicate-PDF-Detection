import os
import hashlib
from collections import defaultdict
from pathlib import Path
import datetime # For human-readable dates

def calculate_md5(filepath, chunk_size=8192):
    """Calculates the MD5 hash of a file."""
    hash_md5 = hashlib.md5()
    try:
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(chunk_size), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except IOError as e:
        print(f"Error reading file {filepath}: {e}")
        return None

def get_file_info_str(filepath: Path):
    """Gets human-readable size and last modified date for a file."""
    try:
        stat_info = filepath.stat()
        size_bytes = stat_info.st_size
        last_modified_timestamp = stat_info.st_mtime
        last_modified_date = datetime.datetime.fromtimestamp(last_modified_timestamp).strftime('%Y-%m-%d %H:%M:%S')

        if size_bytes < 1024:
            size_str = f"{size_bytes} B"
        elif size_bytes < 1024**2:
            size_str = f"{size_bytes/1024:.2f} KB"
        elif size_bytes < 1024**3:
            size_str = f"{size_bytes/(1024**2):.2f} MB"
        else:
            size_str = f"{size_bytes/(1024**3):.2f} GB"
        return f"(Size: {size_str}, Mod: {last_modified_date}, Name: '{filepath.name}')"
    except Exception as e:
        return f"(Error getting info: {e})"

def find_and_process_duplicates_auto(folder_path):
    """
    Finds duplicate PDF files, proposes one to keep per set (oldest, then shortest name),
    and deletes others after a single user confirmation.
    """
    folder = Path(folder_path)
    if not folder.is_dir():
        print(f"Error: Folder '{folder_path}' not found or is not a directory.")
        return

    pdf_files = []
    for item in folder.iterdir():
        if item.is_file() and item.suffix.lower() == '.pdf':
            pdf_files.append(item)

    if not pdf_files:
        print(f"No PDF files found in '{folder_path}'.")
        return

    print(f"Found {len(pdf_files)} PDF files. Calculating hashes...")

    hashes = defaultdict(list)
    for i, pdf_path in enumerate(pdf_files):
        print(f"Processing file {i+1}/{len(pdf_files)}: {pdf_path.name} ...", end="\r", flush=True)
        file_hash = calculate_md5(pdf_path)
        if file_hash:
            hashes[file_hash].append(pdf_path)
    print("\nHash calculation complete.                 ")

    # --- 1. Identify Duplicate Sets and Plan Deletions ---
    planned_actions = [] # List of tuples: (set_hash, file_to_keep, list_of_files_to_delete)

    duplicates_found = False
    for file_hash, file_paths_in_set in hashes.items():
        # Filter out any files that might have been deleted by another process since scanning
        current_files_in_set = [p for p in file_paths_in_set if p.exists()]

        if len(current_files_in_set) > 1:
            duplicates_found = True
            # Sort to determine which one to keep:
            # 1. Oldest modification time (ascending)
            # 2. Shortest filename (ascending)
            # 3. Alphabetical path (ascending)
            def sort_key(p: Path):
                stat_info = p.stat()
                return (stat_info.st_mtime, len(p.name), str(p))

            current_files_in_set.sort(key=sort_key)

            file_to_keep = current_files_in_set[0]
            files_to_delete_for_this_set = current_files_in_set[1:]
            planned_actions.append((file_hash, file_to_keep, files_to_delete_for_this_set))

    if not duplicates_found:
        print("\nNo duplicate PDF files found needing action.")
        return

    # --- 2. Display the Plan ---
    print("\n--- Deletion Plan ---")
    print("For each set of duplicates, one file will be kept (oldest modification, then shortest name).")
    total_to_delete = 0
    for i, (file_hash, keep_file, delete_files) in enumerate(planned_actions):
        print(f"\nSet {i+1} (Hash: {file_hash}):")
        print(f"  KEEPING: {keep_file} {get_file_info_str(keep_file)}")
        if delete_files:
            print("  WILL DELETE:")
            for del_file in delete_files:
                print(f"    - {del_file} {get_file_info_str(del_file)}")
                total_to_delete += 1
        else:
            print("  (No other files in this set to delete)")
    
    if total_to_delete == 0:
        print("\nNo files are marked for deletion based on the criteria (e.g., duplicates already managed).")
        return

    print(f"\nSUMMARY: {total_to_delete} file(s) will be deleted.")

    # --- 3. Single Confirmation ---
    confirm = input(f"Proceed with deleting these {total_to_delete} files? (yes/no): ").lower()

    if confirm == 'yes':
        print("\n--- Performing Deletions ---")
        deleted_count = 0
        kept_count = 0 # This will count files that were part of duplicate sets and were kept
        
        for _, keep_file, delete_files in planned_actions:
            if keep_file.exists(): # Ensure it wasn't deleted by another action
                kept_count +=1
            for file_to_del in delete_files:
                if file_to_del.exists(): # Check if it still exists (e.g. not deleted manually)
                    try:
                        file_to_del.unlink() # os.remove(file_to_del) also works
                        print(f"  DELETED: {file_to_del}")
                        deleted_count += 1
                    except OSError as e:
                        print(f"  ERROR deleting {file_to_del}: {e}")
                else:
                    print(f"  SKIPPED (already gone): {file_to_del}")
        print(f"\nDeletion complete. {deleted_count} file(s) deleted.")
        # Note: kept_count here only counts files that were the chosen "keeper" from a duplicate set.
        # Other unique files are implicitly kept.
    else:
        print("Deletion cancelled. No files were changed.")

if __name__ == "__main__":
    folder_to_check = input("Enter the path to the folder containing PDF files: ")
    find_and_process_duplicates_auto(folder_to_check)
