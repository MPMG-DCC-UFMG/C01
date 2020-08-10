# Captcha Solvers

This module can solve audio and image captcha, for each solver a simple preprocessing were implemented but the users
can create their own.

## Instalation
User must install tesseract to user the image solver

On Linux
```
sudo apt-get update
sudo apt-get install libleptonica-dev
sudo apt-get install tesseract-ocr tesseract-ocr-dev
sudo apt-get install libtesseract-dev
```

## Usage

For dynamic pages:
```python
from image_solver import ImageSolver

# user must create selenium options variable
# options = ...
driver = webdriver.Chrome("/usr/bin/chromedriver", chrome_options=options)

url = 'https://eproc.trf2.jus.br/eproc/externo_controlador.php?acao=processo_consulta_publica \
       &acao_origem=&acao_retorno=processo_consulta_publica'
driver.get(url)

solver = ImageSolver()
text = solver.solve(image=screenshot('//*[@id="imgCaptcha"]', driver))
print(text)
```

For static pages:
```python
from image_solver import ImageSolver

url = "https://www4.tjmg.jus.br/juridico/sf/proc_resultado.jsp?listaProcessos=00000001&comrCodigo=24&numero=1"
solver = ImageSolver()
text = solver.solve(source="https://www4.tjmg.jus.br/juridico/sf/captcha.svl?0.9921973389121602")
print(text)
```