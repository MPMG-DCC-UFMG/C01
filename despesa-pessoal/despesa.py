import requests, os
base = "http://transparencia.mg.gov.br/estado-pessoal/despesa-com-pessoal/despesapessoal-orgaosFiltro/"

#year iteration
for year in range(2009, 2021):
    #months iteration
    for month in range(1,13):
        query = "{}/{}/{}".format(month, month, year)
        if year >= 2020 and month >=3:
            exit()
        url = base + query
        response = requests.get(url)
        content = response.text
        destination_dir = "./despesa-pessoal"
        if not os.path.exists(destination_dir):
            os.makedirs(destination_dir) 
        with open(destination_dir + "/ano-mes" + query.replace("/", "-") + ".html", "w") as f:
            f.write(content)
