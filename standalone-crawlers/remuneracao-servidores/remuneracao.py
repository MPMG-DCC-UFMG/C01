import requests
import argparse
import numpy
import time
import os

parser = argparse.ArgumentParser(description='Baixa os arquivos csv referentes a remuneracao dos servidores de Minas Gerais.')
parser.add_argument("inicio", metavar='Inicio', nargs='+', type=str, help='Mes de inicio da coleta')
parser.add_argument("final", metavar='Final', nargs='+', type=str, help='Mes final da coleta')

args = vars(parser.parse_args())
inicio_mes = args["inicio"][0][0:2]
inicio_ano = args["inicio"][0][2:4]
final_mes = args["final"][0][0:2]
final_ano = args["final"][0][2:4]

if (int(final_ano) > int(time.strftime("%Y")[2:4]) or int(inicio_ano) < 19 or int(final_ano) < int(inicio_ano) or (int(final_ano ) == int(inicio_ano) and int(final_mes) < int(inicio_mes))
    or int(inicio_mes) > 12 or int(inicio_mes)<1 or int(final_mes) > 12 or int(final_mes)<1  or (int(final_ano) == int(time.strftime("%Y")[2:4]) and int(final_mes) > int(time.strftime("%m"))  ) ):
    raise Exception("Valor dos anos incorreto, tente novamente.")

print("Baixando dados de", inicio_mes, "de", inicio_ano,"a", final_mes,"de",final_ano)

if not os.path.exists("Data"):
    os.makedirs("Data")

for ano in range( int(inicio_ano), int(final_ano)+1, 1):
    inicio = 1
    if int(inicio_ano) == ano:
        inicio = int(inicio_mes)
    final = 12
    if int(final_ano) == ano:
        final = int(final_mes)
    for mes in range(inicio, final+1,1):
        url = None
        if mes < 10:
            url = "http://200.198.22.105/fgs-adm/remuneracao/downloadRemuneracao.php?mes=0" + str(mes) + str(ano)
            r = requests.get(url)  
            with open("Data/" + '0' + str(mes) + str(ano)+ ".csv", 'wb') as f:
                f.write(r.content)
        else:
            url = "http://200.198.22.105/fgs-adm/remuneracao/downloadRemuneracao.php?mes=" + str(mes) + str(ano)
            r = requests.get(url)  
            with open("Data/" + str(mes) + str(ano)+ ".csv", 'wb') as f:
                f.write(r.content)
        print(url)
