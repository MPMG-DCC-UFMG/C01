import requests
import logging
import os

logging.basicConfig(level=logging.INFO)

base = "http://geoobras.tce.mg.gov.br/cidadao/Obras/ObrasPaginaInteiraDetalhes.aspx?IDOBRA="
not_found = "possivel localizar a obra"
for i in range(50000):
    # logging.info("Coletando obra de ID: " + str(i))
    url = base + str(i)
    response = requests.get(url)
    content = response.text
    if not_found in content:
        continue
    folder = "obras" + str(i%100)
    if not os.path.exists("obras_tce/" + folder):
        os.makedirs("obras_tce/" + folder)
    with open("obras_tce/" + folder + "/obra_id" + str(i), "w") as f:
        f.write(content)
