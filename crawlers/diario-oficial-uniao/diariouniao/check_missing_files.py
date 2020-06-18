import os
import json

file_names = {}
with open("list_of_files.txt", "r") as f:
    for line in f:
        f_dict = json.loads(line)
        file_names[f_dict["file_name"]] = f_dict

files_downloaded = []
for f in os.listdir("jornais-completos"):
    files_downloaded.append(f)
files_downloaded = set(files_downloaded)

for f in file_names:
    if f not in files_downloaded:
        print(f)
