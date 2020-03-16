from datetime import timedelta, date
import os
import requests
import re

def daterange(start_date, end_date):
    for n in range(int ((end_date - start_date).days)):
        yield start_date + timedelta(n)

start_date = date(1996, 1, 1)
end_date = date(2020, 3, 13)
for single_date in daterange(start_date, end_date):
    date = single_date.strftime("%d/%m/%Y")
    base = "http://portal6.pbh.gov.br/dom/iniciaEdicao.do?method=DomDia&dia="
    url = base + date
    response = requests.get(url)
    content = response.text
    if "Nenhum Artigo publicado em " in content:
        continue
    destination_dir = date.split("/")[-1] + "/" +  date.replace("/", "-")
    if not os.path.exists(destination_dir):
        os.makedirs(destination_dir)
    with open(destination_dir + "/diario-" + date.replace("/", "-") + ".html", "w") as f:
            f.write(content)
    base_files = "http://portal6.pbh.gov.br/dom/iniciaEdicao.do?method=DetalheArtigo&pk="
    files = re.findall(r"method=DetalheArtigo&pk=\d+", content)
    for f in files:
        f = f.split("=")[-1]
        url = base_files + f
        print(url)
        response = requests.get(url)
        content = response.text
        with open(destination_dir + "/anexo-" + date.replace("/", "-") + "-" + f +".html", "w") as f:
            f.write(content)
