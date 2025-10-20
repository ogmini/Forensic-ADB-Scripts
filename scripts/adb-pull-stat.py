"""
File: adb-pull-stat.py
Description: Recursively collects files and their EXT4 timestamps and hashes from an Android device using ADB. Leverages the find, stat, md5sum, and sha256sum commands. More information can be found at https://github.com/ogmini/Forensic-ADB-Scripts.
Author: ogmini (https://ogmini.github.io/)
Created: 2025-10-13
Modified: 2025-10-13
Version: 0.1
License: MIT
Usage:
    python adb-pull-stat.py /sdcard/DCIM -t .jpg .png -o output.csv

Dependencies:
    - ADB (Android Debug Bridge) - https://developer.android.com/tools/adb
    - Python 3.6+
"""

import subprocess
import argparse
import fadbfuncs
    
def main():
    parser = argparse.ArgumentParser(description="TODO")
    parser.add_argument("storage_path", help="TODO")
    parser.add_argument("-o", "--output", default="timestamps.csv", help="Output CSV filename")
    parser.add_argument("-t", "--types", nargs="+", default=["*"], help="File extensions to include, e.g., -t .jpg .png .mp4")
    parser.add_argument("--wifi", action="store_true", help="Connects to phone over wifi instead of USB")

    args = parser.parse_args()

    if args.wifi:
        fadbfuncs.adb_connect_wifi()
        
    storage_path = args.storage_path
    output_file = args.output
    extensions = [ext.lower() for ext in args.types]
    
    find_command = ["adb", "shell", "find", storage_path, "-type f"]
    files = fadbfuncs.run_adb_command(find_command)
    
    if not files:
        print("No Files Found")
        return
        
    if extensions == ["*"]:
        filtered_files = files
    else:
        filtered_files = [ 
            f for f in files
            if any(f.lower().endswith(ext) for ext in extensions)
        ]
        
    if not filtered_files:
        print("No Files Matched Types Filter")
        return
        
    with open(output_file, "w", encoding="utf-8") as f_out:
        f_out.write("filename, last_access, last_mod, change_time, md5, sha256\n")
        
        for f in filtered_files:
            stat_command = ["adb", "shell", "stat", f'--format=%n,%x,%y,%z', f]
            stat_output = fadbfuncs.run_adb_command(stat_command)
            
            md5sum_command = ["adb", "shell", "md5sum", "-b", f]
            md5sum_output = fadbfuncs.run_adb_command(md5sum_command)
            
            sha256sum_command = ["adb", "shell", "sha256sum", "-b", f]
            sha256sum_output = fadbfuncs.run_adb_command(sha256sum_command)
            
            if stat_output:
                f_out.write(stat_output[0] +"," + md5sum_output[0] + "," + sha256sum_output[0] + "\n")
                print(stat_output[0] + "," + md5sum_output[0] + "," + sha256sum_output[0])
                
        pull_command = ["adb", "pull", storage_path]
        fadbfuncs.run_adb_command(pull_command)
        
    if args.wifi:
        fadbfuncs.adb_disconnect_wifi()
        
if __name__ == "__main__":
    main()