# Captcha Solvers

This module can solve audio and image captcha.
For each solver a simple preprocessing were implemented but the users can create their own.

For image captchas, the Tesseract OCR (https://github.com/tesseract-ocr/tesseract) is set as the default OCR.

For audio captchas, the SpeechRecognition (https://pypi.org/project/SpeechRecognition/) is the default method.

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
source code you need to have `setuptools`, `wheel` and `python3` installed. After both
packages are installed, go to src/captcha_solver and run:

```
python3 setup.py bdist_wheel
pip3 install dist/captcha_solver-1.0-py3-none-any.whl
```

## Usage

For dynamic pages:
```python
from image_solver import ImageSolver

# user must create provide image variable, eg:
# image = screenshot('//*[@id="imgCaptcha"]', driver)

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