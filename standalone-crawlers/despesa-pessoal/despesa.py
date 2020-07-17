import requests, os, time
base = "http://transparencia.mg.gov.br/estado-pessoal/despesa-com-pessoal/despesapessoal-orgaosFiltro/"
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

#year iteration
for year in range(2009, 2021):
    #months iteration
    for month in range(1,13):
        query = "{}/{}/{}".format(month, month, year)
        if year >= 2020 and month >=3:
            exit()
        url = base + query
        print(url)
        # exit()
        response = requests.get(url, headers=headers)
        content = response.text
        destination_dir = "./despesa-pessoal"
        if not os.path.exists(destination_dir):
            os.makedirs(destination_dir) 
        with open(destination_dir + "/ano-mes" + query.replace("/", "-") + ".html", "w") as f:
            f.write(content)
        time.sleep(2)
