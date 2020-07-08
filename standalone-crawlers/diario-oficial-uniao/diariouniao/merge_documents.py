import os
import threading
import time
import concurrent.futures
import PyPDF2.utils

def merge_doc_pages(docs):
    docs.sort()

    name_parts = docs[0].split("_")
    name_key = name_parts[0] + "_" + name_parts[1]
    
    pdf_merger = PyPDF2.PdfFileMerger()
    for text_pdf_file in docs:
        pdf_merger.append(PyPDF2.PdfFileReader("jornais/" + text_pdf_file, strict=False))
    pdf_merger.write(f"jornais-completos/{name_key}.pdf")
    
    print(name_key, "merged!")

    for text_pdf_file in docs:
        os.remove("jornais/" + text_pdf_file)

    pdf_merger.close()

while True:
    print("main loop starting...")
    docs = {}
    folder = "jornais"
    docs_completed = []
    for file_name in os.listdir(folder):
        name_parts = file_name.split("_")
        name_key = name_parts[0] + "_" + name_parts[1]
        
        if name_key not in docs:
            docs[name_key] = {
                "n_pages": int(name_parts[2]),
                "pages": []
            }
        
        docs[name_key]["pages"].append(file_name)
        if len(docs[name_key]["pages"]) == docs[name_key]["n_pages"]:
            print(name_key, "pages downloaded")
            docs_completed.append(name_key)

    docs_completed = set(docs_completed)

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        executor.map(merge_doc_pages, [
            docs[doc]["pages"] for doc in docs if doc in docs_completed
        ])

    print("main loop sleeping...")
    time.sleep(300)