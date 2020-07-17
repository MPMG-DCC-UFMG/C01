import json
import pprint
pp = pprint.PrettyPrinter(indent=2)

with open("links_ammg.json", "r") as f:
    data = json.loads(f.read())

url_index = {}
for d, i in zip(data, range(len(data))):
    url_index[d["url"]] = i

with open("scrapy_download_pdfs.log", "r") as f:
    for line in f:
        if line[:11] == "{'file_urls":
            attr = json.loads(line.replace("'", "\""))["files"][0]

            data[url_index[attr['url']]]['path'] = attr['path']
            data[url_index[attr['url']]]['checksum'] = attr['checksum']

for d in data:
    if len(d) == 3:
        print("Probelm with:", d["date"], d["url"])

with open("info.txt", "w+") as f:
    f.write(json.dumps(data, indent=1))
