import subprocess

with open("execute_log.txt", "w+") as f:
    pass

while True:
    with open("last_call.txt", "r") as f:
        last_call = int(f.read()) 
    
    if last_call >= 1107:
        break
    
    with open("execute_log.txt", "a") as f:
        f.write(f"{last_call}\n")

    process = subprocess.Popen(
        "python -m scrapy crawl fetch_missing --loglevel=INFO",
        shell=True, stdout=subprocess.PIPE
    )
    process.wait()

 