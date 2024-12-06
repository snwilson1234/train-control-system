import os
import shutil

def copy_all_files(src, dst):
    src_files = os.listdir(src)
    for file_name in src_files:
        full_file_name = os.path.join(src, file_name)
        if os.path.isfile(full_file_name):
            print(f"Copying file {full_file_name} to {dst}/{file_name}")
            shutil.copy(full_file_name,dst)


source_green = "./plc_programs/green_line/og_var_files"
destination_green = "./plc_programs/green_line/var_files"
source_red = "./plc_programs/red_line/og_var_files"
destination_red = "./plc_programs/red_line/var_files"
track_db_path = "./track_model/track.db"

copy_all_files(source_green, destination_green)
copy_all_files(source_red, destination_red)

if os.path.exists(track_db_path):
    print(f"Removing file {track_db_path}")
    os.remove(track_db_path)
else:
    print(f"File {track_db_path} does not exist.")

