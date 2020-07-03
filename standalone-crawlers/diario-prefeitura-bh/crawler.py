from datetime import timedelta, date
import os
import requests
import re
from time import sleep

def daterange(start_date, end_date):
    for n in range(int ((end_date - start_date).days)):
        yield start_date + timedelta(n)


def download(single_date):
    try:
        date = single_date.strftime("%d/%m/%Y")
        print(date)
        url = "http://portal6.pbh.gov.br/dom/iniciaEdicao.do?method=DomDia&dia="  + date
        content = requests.get(url).text
        if "Nenhum Artigo publicado em " in content:
            return True
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
            response = requests.get(url)
            content = response.text
            with open(destination_dir + "/anexo-" + date.replace("/", "-") + "-" + f +".html", "w") as f:
                f.write(content)
            if "Capa" in content:
                for capa in re.findall(r"/dom\d+ ", content):
                    capa = capa.replace("/", "").replace(" ", "")
                    response = requests.get("http://portal6.pbh.gov.br/dom/Files/" + capa + " - assinado.pdf")
                    with open(destination_dir + "/capa-" + date.replace("/", "-") + ".pdf", 'wb') as f:
                        f.write(response.content)
        return True
    except Exception as err:
        print(err)
        print("Deu erro")
        sleep(60)
        return False

start_date = date(2018,11, 28)
end_date = date(2020, 3, 13)
for single_date in daterange(start_date, end_date):
    while True:
        print("Tentativa")
        if download(single_date):
            break
