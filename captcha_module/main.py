from image_solver import ImageSolver
from audio_solver import AudioSolver

#####################
url = 'https://eproc.trf2.jus.br/eproc/externo_controlador.php?acao=processo_consulta_publica&acao_origem=&acao_retorno=processo_consulta_publica'
solver = ImageSolver(url)
text = solver.solve(xpath='//*[@id="imgCaptcha"]')
print(text)

#####################
url = "https://www4.tjmg.jus.br/juridico/sf/proc_resultado.jsp?listaProcessos=00000001&comrCodigo=24&numero=1"
solver = ImageSolver(url)
text = solver.solve(url="https://www4.tjmg.jus.br/juridico/sf/captcha.svl?0.9921973389121602")
print(text)
solver = AudioSolver(url)
text = solver.solve(url="https://www4.tjmg.jus.br/juridico/sf/captchaAudio.svl")
print(text)

######################
url = "https://www2.trf4.jus.br/trf4/"
solver = ImageSolver(url)
text = solver.solve(url="https://www2.trf4.jus.br/trf4/processos/acompanhamento/gera_imagem.php?refid=c753348455a58e99ed5c3e2628b1ebd1")
print(text)

