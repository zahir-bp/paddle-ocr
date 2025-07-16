import os
import glob

def clear_ocr_output(directory='ocr_output'):
    if not os.path.exists(directory):
        print(f"Directory '{directory}' does not exist.")
        return

    files = glob.glob(os.path.join(directory, '*'))
    for file_path in files:
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
        except Exception as e:
            print(f"Error deleting {file_path}: {e}")