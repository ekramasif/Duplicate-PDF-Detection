# PDF Duplicate Finder & Deleter (Keep First Encountered)

This Python script scans a specified folder for PDF files, identifies duplicates based on their content (MD5 hash), and then offers to delete redundant copies.

For each set of duplicate files, the script will automatically propose to **keep the first file encountered** during its scan and delete all other identical files in that set. You will be shown a detailed plan of which files will be kept and which will be deleted before any action is taken. Deletion only occurs after a single, final confirmation from you.

## Features

*   **Content-based duplicate detection:** Uses MD5 hashing to ensure files are true duplicates.
*   **Automatic selection:** Keeps the "first encountered" PDF in a duplicate set.
*   **Detailed plan:** Shows exactly which files will be kept and which will be deleted.
*   **Single confirmation:** All proposed deletions are performed with one "yes" confirmation.
*   **Progress indicator:** Shows progress during the hashing phase.
*   **File information:** Displays size, modification date, and full path for files in the plan.

## Requirements

*   Python 3.x (no external libraries beyond the standard library are needed).

## How to Use

1.  **Save the Script:** Save the Python code as a `.py` file (e.g., `main.py`).
2.  **Backup Your Data (IMPORTANT!):** Before running this script, **it is strongly recommended to back up the folder containing your PDFs.** This script deletes files, and actions are irreversible without a backup.
3.  **Open Terminal/Command Prompt:** Navigate to the directory where you saved the script.
4.  **Run the Script:**
    ```bash
    python main.py
    ```
5.  **Enter Folder Path:** When prompted, enter the full path to the folder containing the PDF files you want to check.
    ```
    Enter the path to the folder containing PDF files: /path/to/your/pdf_folder
    ```
6.  **Review the Plan:** The script will process the files and then display a "Deletion Plan". This plan will list each set of duplicates, indicating:
    *   The file to be **KEPT**.
    *   The file(s) that **WILL DELETE**.
    Carefully review this plan to ensure it aligns with your expectations.
7.  **Confirm Deletion:** You will be asked for a final confirmation:
    ```
    Proceed with deleting these X file(s)? (yes/no):
    ```
    *   Type `yes` and press Enter to proceed with the deletions.
    *   Type `no` (or anything else) and press Enter to cancel, and no files will be changed.

## How "First Encountered" is Determined

The "first encountered" file in a duplicate set is determined by the order in which files are listed by the operating system when the script scans the directory (`Path.iterdir()`) and subsequently processed. While generally consistent for a given run, this order might not be strictly alphabetical or by date across all systems or if files are added/removed between scans.

If you need a more deterministic way to choose which file to keep (e.g., always the oldest, or shortest name), the script logic would need to be modified accordingly (see previous versions of the script for examples of sorting).

## Disclaimer

Use this script at your own risk. The author is not responsible for any data loss. **Always back up your data before running scripts that modify or delete files.**
