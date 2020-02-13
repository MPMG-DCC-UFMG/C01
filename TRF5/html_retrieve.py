import urllib.request
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException 

url_base = 'http://www5.trf5.jus.br/precatorio/'

# define xpaths válidos em páginas de processos nos dois formatos existentes
xpath_model1 = '//*[@id="wrapper"]/h1'
xpath_model2 = '/html/body/p[2]'

# opções para não abrir navegador
chrome_options = Options()
chrome_options.add_argument("--headless")
driver = webdriver.Chrome(chrome_options=chrome_options)

# arquivo para armazenar as páginas que tiveram exceção
excs = open('exceptions.txt', 'a')

# checa se um dado xpath existe
def check_exists_by_xpath(xpath, url):
	driver.get(url)
	try:
		driver.find_element_by_xpath(xpath)
	except NoSuchElementException:		
		return False
	return True

# URLs de forma sequencial
i = 70078

# contador de exceções
exc_counter = 0

while True:
	url = url_base + str(i)
	
	if exc_counter >= 3:
		break

	# se a página contiver um xpath específico de um dos dois modelos, ela é armazenada
	if check_exists_by_xpath(xpath_model1, url) or check_exists_by_xpath(xpath_model2, url):

		exc_counter = 0

		filename = 'precatorio-' + str("{:06d}".format(i)) + '.html'
		path = './pages/' + filename
		
		# guarda o conteúdo html da página acessada
		urllib.request.urlretrieve(url, path)
		i += 1
	else:
		excs.write(url + '\n')
		exc_counter += 1
		i += 1