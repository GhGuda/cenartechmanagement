import os
import shutil

def delete_report_cards():
    # Define the path to the report_cards folder inside the media folder
    report_cards_folder = os.path.join('media', 'report_cards')

    # Check if the folder exists
    if os.path.exists(report_cards_folder) and os.path.isdir(report_cards_folder):
        # Loop through the files in the folder
        for filename in os.listdir(report_cards_folder):
            file_path = os.path.join(report_cards_folder, filename)
            try:
                # Check if it is a file (not a folder) and delete it
                if os.path.isfile(file_path):
                    os.remove(file_path)
                # If it's a directory (just in case), delete the directory
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f"Error deleting {file_path}: {e}")
        print("All files in the report_cards folder have been deleted.")
    else:
        print("The report_cards folder does not exist.")