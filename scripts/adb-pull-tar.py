"""
File: adb-tar-pull.py
Description: TODO
Author: ogmini (https://ogmini.github.io/)
Created: 2025-10-19
Modified: 2025-10-19
Version: 0.1
License: MIT
Usage:
    python adb-pull-tar.py /sdcard/DCIM -t .jpg .png -o output.csv
    
Dependencies:
    - ADB (Android Debug Bridge) - https://developer.android.com/tools/adb
    - Python 3.6+
"""

import subprocess
import argparse
from pathlib import Path
import fadbfuncs
    
def main():
    parser = argparse.ArgumentParser(description="TODO")
    parser.add_argument("data_folder_path", help="TODO")
    parser.add_argument("-s", "--storage", default="/storage/self/primary/Download/", help="Location to store tar file on device before pull")
    parser.add_argument("--wifi", action="store_true", help="Connects to phone over wifi instead of USB")

    args = parser.parse_args()
    
    if args.wifi:
        fadbfuncs.adb_connect_wifi()
    
    data_folder_path = args.data_folder_path
    data_folder_name = Path(data_folder_path).name
    storage_path = args.storage
    output_file = "hash.csv"
    tar_path = f"{storage_path}/{data_folder_name}.tar"
    print(tar_path)
    
    # Verify Folder Exists
    find_command = ["adb", "shell", "su -c 'ls ", data_folder_path, "'"]
    files = fadbfuncs.run_adb_command(find_command)
    
    if not files:
        print("No Files Found")
        return
        
    for f in files:
        print(f)
        
    # adb shell su -c "tar -cvf /storage/self/primary/Download/dji_fly.tar /data/data/dji.go.v5/"
    
    tar_command = ["adb", "shell", "su -c 'tar -cvf ", tar_path, data_folder_path, "'"]
    # print(tar_command)
    tar = fadbfuncs.run_adb_command(tar_command)
    print(tar[0])
    
    # Calculate MD5/SHA256 Hash of tar
    md5sum_command = ["adb", "shell", "md5sum", "-b", tar_path]
    md5sum_output = fadbfuncs.run_adb_command(md5sum_command)
    print(md5sum_output)
    
    sha256sum_command = ["adb", "shell", "sha256sum", "-b", tar_path]
    sha256sum_output = fadbfuncs.run_adb_command(sha256sum_command)
    print(sha256sum_output)
    
    # Generate txt file with hashes
    with open(output_file, "w", encoding="utf-8") as f_out:
        f_out.write("filename, md5, sha256\n")
        f_out.write(tar_path + "," + md5sum_output[0] + "," + sha256sum_output[0])

    # adb pull file
    pull_command = ["adb", "pull", tar_path]
    fadbfuncs.run_adb_command(pull_command, track_progress=True)
    
    #TODO: Show progress of adbpull if possible
    
    if args.wifi:
        fadbfuncs.adb_disconnect_wifi()
          
if __name__ == "__main__":
    main()