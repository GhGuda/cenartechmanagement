import os
import shutil
from django.contrib import messages


def delete_report_cards():
    report_cards_folder = os.path.join('media', 'report_cards')

    if os.path.exists(report_cards_folder) and os.path.isdir(report_cards_folder):
        for filename in os.listdir(report_cards_folder):
            file_path = os.path.join(report_cards_folder, filename)
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                messages.error(f"Error deleting {file_path}: {e}")
    else:
        messages.error("The report_cards folder does not exist.")
        