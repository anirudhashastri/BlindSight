import os
import pandas as pd
from tqdm import tqdm

class DriveScanner:
    def __init__(self, drive_letters):
        """
        Initialize the DriveScanner with a list of drive letters to scan.
        """
        self.drive_letters = drive_letters
        self.files_data = []

    def scan_drives(self):
        """
        Scan the specified drives and collect file information.
        """
        # Traverse each drive specified
        for drive in tqdm(self.drive_letters, desc="Scanning Drives"):
            # Define the drive path (e.g., "C:\\")
            drive_path = f"{drive}:/"

            # Walk through all directories and files in the drive
            for root, dirs, files in tqdm(os.walk(drive_path), desc=f"Scanning {drive}:\\", leave=False, position=1):
                for file in files:
                    # Get full file path
                    file_path = os.path.join(root, file)
                    # Get file extension/type
                    file_type = os.path.splitext(file)[1][1:]  # Remove the dot

                    # Append file information
                    self.files_data.append({
                        "File name": file,
                        "Drive": drive,
                        "filetype": file_type,
                        "Path": file_path
                    })

    def save_to_pickle(self, filename="file_list.pkl"):
        """
        Save the collected file information to a pickle file.
        """
        # Create a DataFrame from the collected file data
        files_df = pd.DataFrame(self.files_data)

        # Save the DataFrame to a pickle file
        files_df.to_pickle(filename)
        print(f"Data saved as {filename}")

# Usage
# drives_to_scan = ['C', 'E', 'D', 'G', 'H']
# scanner = DriveScanner(drives_to_scan)
# scanner.scan_drives()
# scanner.save_to_pickle("file_list.pkl")
