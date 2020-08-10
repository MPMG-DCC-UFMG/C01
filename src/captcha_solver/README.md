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

## Building

This module is packaged as a Python Wheel file. To build the .whl file from the
source code you need to have `setuptools` and `wheel` installed. After both
packages are installed, run:

```
python setup.py bdist_wheel
```

The Wheel file will be created inside the `dist` folder, and the name may vary
depending on the version. To install it, you must have the `entry_probing`
module installed. Run the following command in the `range_inference` folder,
replacing the file name accordingly:

```
pip install dist/<wheel file name>
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
image = screenshot('//*[@id="imgCaptcha"]', driver)

solver = ImageSolver()
text = solver.solve(image=image)
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