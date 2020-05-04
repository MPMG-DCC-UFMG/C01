# Módulo responsável por camuflar coletores baseado em Selenium
De maneira geral, webdrivers do Selenium ou sessões da biblioteca Requests são especializados para rotacionar IPs, controlar número de requisições por tempo, introduzir aleatoriedade, rotacionar User-Agents, evitar Honeypots, etc.   

## Rotação de IPs
A rotação de IPs ocorrem apenas via Tor. Para seu uso, crie uma instância de TorFirefoxWebdriver ou TorChromeWebdriver e defina pelo parâmetro **change_ip_after** com quantas requisições o IP será alterado. Essas duas classes herdam da classe webdriver.Firefox e webdriver.Chrome, respectivamente. Portanto, os mesmos parâmetros dessas superclasses estão disponíveis em Tor*Webdriver.

É necessário configurar o Tor:
- Instale-o, se necessário
    ```bash
    sudo apt install tor
    ```
- Pare sua execução para configurá-lo:
    ```bash
    sudo service tor stop
    ```
- Gere uma senha de acesso (lembre-se dela, será necessária posteriormente):
    ```bash
    tor --hash-password "sua senha"
    ```
- O comando acima gerará um hash como o abaixo, copie-o:
    ```bash
    16:75928863A1C80E19600A03DB8AB2E733765FBFD229330A24536F3BA82E
    ```
- Acesse o arquivo de configuração do Tor:
    ```bash
    sudo nano /etc/tor/torrc
    ```
- Coloque os comandos abaixo:
    ```bash
    ControlPort 9051
    HashedControlPassword <cole_aqui_o_hash_copiado>
    ```
- Reinicie o Tor:
    ```bash
    sudo service tor start
    ```

É possível específicar as origens dos IPs alterando o arquivo de configuração do Tor, para isso, acesse o mesmo como **root** com seu editor favorito. Sua localização é:
```bash
/etc/tor/torrc
```

É necessário ter o código dos países de origem dos IPs, que são listados abaixo: 

| País de origem do IP | Código |
| ------------- |:-------------:|
| ASCENSION ISLAND| {ac} |
| AFGHANISTAN| {af} |
| ALAND| {ax} |
| ALBANIA| {al} |
| ALGERIA| {dz} |
| ANDORRA| {ad} |
| ANGOLA| {ao} |
| ANGUILLA| {ai} |
| ANTARCTICA| {aq} |
| ANTIGUA AND BARBUDA| {ag} |
| ARGENTINA REPUBLIC| {ar} |
| ARMENIA| {am} |
| ARUBA| {aw} |
| AUSTRALIA| {au} |
| AUSTRIA| {at} |
| AZERBAIJAN| {az} |
| BAHAMAS| {bs} |
| BAHRAIN| {bh} |
| BANGLADESH| {bd} |
| BARBADOS| {bb} |
| BELARUS| {by} |
| BELGIUM| {be} |
| BELIZE| {bz} |
| BENIN| {bj} |
| BERMUDA| {bm} |
| BHUTAN| {bt} |
| BOLIVIA| {bo} |
| BOSNIA AND HERZEGOVINA| {ba} |
| BOTSWANA| {bw} |
| BOUVET ISLAND| {bv} |
| BRAZIL| {br} |
| BRITISH INDIAN OCEAN TERR| {io} |
| BRITISH VIRGIN ISLANDS| {vg} |
| BRUNEI DARUSSALAM| {bn} |
| BULGARIA| {bg} |
| BURKINA FASO| {bf} |
| BURUNDI| {bi} |
| CAMBODIA| {kh} |
| CAMEROON| {cm} |
| CANADA| {ca} |
| CAPE VERDE| {cv} |
| CAYMAN ISLANDS| {ky} |
| CENTRAL AFRICAN REPUBLIC| {cf} |
| CHAD| {td} |
| CHILE| {cl} |
| PEOPLE’S REPUBLIC OF CHINA| {cn} |
| CHRISTMAS ISLANDS| {cx} |
| COCOS ISLANDS| {cc} |
| COLOMBIA| {co} |
| COMORAS| {km} |
| CONGO| {cg} |
| CONGO (DEMOCRATIC REPUBLIC)| {cd} |
| COOK ISLANDS| {ck} |
| COSTA RICA| {cr} |
| COTE D IVOIRE| {ci} |
| CROATIA| {hr} |
| CUBA| {cu} |
| CYPRUS| {cy} |
| CZECH REPUBLIC| {cz} |
| DENMARK| {dk} |
| DJIBOUTI| {dj} |
| DOMINICA| {dm} |
| DOMINICAN REPUBLIC| {do} |
| EAST TIMOR| {tp} |
| ECUADOR| {ec} |
| EGYPT| {eg} |
| EL SALVADOR| {sv} |
| EQUATORIAL GUINEA| {gq} |
| ESTONIA| {ee} |
| ETHIOPIA| {et} |
| FALKLAND ISLANDS| {fk} |
| FAROE ISLANDS| {fo} |
| FIJI| {fj} |
| FINLAND| {fi} |
| FRANCE| {fr} |
| FRANCE METROPOLITAN| {fx} |
| FRENCH GUIANA| {gf} |
| FRENCH POLYNESIA| {pf} |
| FRENCH SOUTHERN TERRITORIES| {tf} |
| GABON| {ga} |
| GAMBIA| {gm} |
| GEORGIA| {ge} |
| GERMANY| {de} |
| GHANA| {gh} |
| GIBRALTER| {gi} |
| GREECE| {gr} |
| GREENLAND| {gl} |
| GRENADA| {gd} |
| GUADELOUPE| {gp} |
| GUAM| {gu} |
| GUATEMALA| {gt} |
| GUINEA| {gn} |
| GUINEA-BISSAU| {gw} |
| GUYANA| {gy} |
| HAITI| {ht} |
| HEARD & MCDONALD ISLAND| {hm} |
| HONDURAS| {hn} |
| HONG KONG| {hk} |
| HUNGARY| {hu} |
| ICELAND| {is} |
| INDIA| {in} |
| INDONESIA| {id} |
| IRAN, ISLAMIC REPUBLIC OF| {ir} |
| IRAQ| {iq} |
| IRELAND| {ie} |
| ISLE OF MAN| {im} |
| ISRAEL| {il} |
| ITALY| {it} |
| JAMAICA| {jm} |
| JAPAN| {jp} |
| JORDAN| {jo} |
| KAZAKHSTAN| {kz} |
| KENYA| {ke} |
| KIRIBATI| {ki} |
| KOREA, DEM. PEOPLES REP OF| {kp} |
| KOREA, REPUBLIC OF| {kr} |
| KUWAIT| {kw} |
| KYRGYZSTAN| {kg} |
| LAO PEOPLE’S DEM. REPUBLIC| {la} |
| LATVIA| {lv} |
| LEBANON| {lb} |
| LESOTHO| {ls} |
| LIBERIA| {lr} |
| LIBYAN ARAB JAMAHIRIYA| {ly} |
| LIECHTENSTEIN| {li} |
| LITHUANIA| {lt} |
| LUXEMBOURG| {lu} |
| MACAO| {mo} |
| MACEDONIA| {mk} |
| MADAGASCAR| {mg} |
| MALAWI| {mw} |
| MALAYSIA| {my} |
| MALDIVES| {mv} |
| MALI| {ml} |
| MALTA| {mt} |
| MARSHALL ISLANDS| {mh} |
| MARTINIQUE| {mq} |
| MAURITANIA| {mr} |
| MAURITIUS| {mu} |
| MAYOTTE| {yt} |
| MEXICO| {mx} |
| MICRONESIA| {fm} |
| MOLDAVA REPUBLIC OF| {md} |
| MONACO| {mc} |
| MONGOLIA| {mn} |
| MONTENEGRO| {me} |
| MONTSERRAT| {ms} |
| MOROCCO| {ma} |
| MOZAMBIQUE| {mz} |
| MYANMAR| {mm} |
| NAMIBIA| {na} |
| NAURU| {nr} |
| NEPAL| {np} |
| NETHERLANDS ANTILLES| {an} |
| NETHERLANDS, THE| {nl} |
| NEW CALEDONIA| {nc} |
| NEW ZEALAND| {nz} |
| NICARAGUA| {ni} |
| NIGER| {ne} |
| NIGERIA| {ng} |
| NIUE| {nu} |
| NORFOLK ISLAND| {nf} |
| NORTHERN MARIANA ISLANDS| {mp} |
| NORWAY| {no} |
| OMAN| {om} |
| PAKISTAN| {pk} |
| PALAU| {pw} |
| PALESTINE| {ps} |
| PANAMA| {pa} |
| PAPUA NEW GUINEA| {pg} |
| PARAGUAY| {py} |
| PERU| {pe} |
| PHILIPPINES (REPUBLIC OF THE)| {ph} |
| PITCAIRN| {pn} |
| POLAND| {pl} |
| PORTUGAL| {pt} |
| PUERTO RICO| {pr} |
| QATAR| {qa} |
| REUNION| {re} |
| ROMANIA| {ro} |
| RUSSIAN FEDERATION| {ru} |
| RWANDA| {rw} |
| SAMOA| {ws} |
| SAN MARINO| {sm} |
| SAO TOME/PRINCIPE| {st} |
| SAUDI ARABIA| {sa} |
| SCOTLAND| {uk} |
| SENEGAL| {sn} |
| SERBIA| {rs} |
| SEYCHELLES| {sc} |
| SIERRA LEONE| {sl} |
| SINGAPORE| {sg} |
| SLOVAKIA| {sk} |
| SLOVENIA| {si} |
| SOLOMON ISLANDS| {sb} |
| SOMALIA| {so} |
| SOMOA,GILBERT,ELLICE ISLANDS| {as} |
| SOUTH AFRICA| {za} |
| SOUTH GEORGIA, SOUTH SANDWICH ISLANDS| {gs} |
| SOVIET UNION| {su} |
| SPAIN| {es} |
| SRI LANKA| {lk} |
| ST. HELENA| {sh} |
| ST. KITTS AND NEVIS| {kn} |
| ST. LUCIA| {lc} |
| ST. PIERRE AND MIQUELON| {pm} |
| ST. VINCENT & THE GRENADINES| {vc} |
| SUDAN| {sd} |
| SURINAME| {sr} |
| SVALBARD AND JAN MAYEN| {sj} |
| SWAZILAND| {sz} |
| SWEDEN| {se} |
| SWITZERLAND| {ch} |
| SYRIAN ARAB REPUBLIC| {sy} |
| TAIWAN| {tw} |
| TAJIKISTAN| {tj} |
| TANZANIA, UNITED REPUBLIC OF| {tz} |
| THAILAND| {th} |
| TOGO| {tg} |
| TOKELAU| {tk} |
| TONGA| {to} |
| TRINIDAD AND TOBAGO| {tt} |
| TUNISIA| {tn} |
| TURKEY| {tr} |
| TURKMENISTAN| {tm} |
| TURKS AND CALCOS ISLANDS| {tc} |
| TUVALU| {tv} |
| UGANDA| {ug} |
| UKRAINE| {ua} |
| UNITED ARAB EMIRATES| {ae} |
| UNITED KINGDOM (no new registrations)| {gb} |
| UNITED KINGDOM| {uk} |
| UNITED STATES| {us} |
| UNITED STATES MINOR OUTL.IS.| {um} |
| URUGUAY| {uy} |
| UZBEKISTAN| {uz} |
| VANUATU| {vu} |
| VATICAN CITY STATE| {va} |
| VENEZUELA| {ve} |
| VIET NAM| {vn} |
| VIRGIN ISLANDS (USA)| {vi} |
| WALLIS AND FUTUNA ISLANDS| {wf} |
| WESTERN SAHARA| {eh} |
| YEMEN| {ye} |
| ZAMBIA| {zm} |
| ZIMBABWE| {zw} |

Após a escolha do país de origem dos IPs, altere o arquivo de configuração do Tor da seguinte forma:

```bash
ExitNodes {codigo_pais}
StrictNodes 1
```

Por exemplo, para especificar que os IPs tem origem apenas no Brasil, adicione as linhas: 

```bash
ExitNodes {br}
StrictNodes 1
```

Também é possível específicar uma lista de países de onde os IPs se originam, da seguinte forma: 

```bash
ExitNodes {br}, {ar}, {cl}
```

Neste exemplo, os países de origem dos IPs são Brasil, Argentina e Chile. 

Também é possível configurar o Tor para que se nunca use IPs de alguns países, da seguinte forma:

```bash
ExcludeExitNodes {codigo_pais}
```

Por exemplo, restringindo IPs dos EUA e Canadá:
```bash
ExcludeExitNodes {us}, {ca}
```

Por fim, para garantir as mudanças, reinicie o Tor:
```bash
sudo service tor restart
```

Restringir IPs a certos países pode ser útil de diversas formas. Por exemplo, caso algum site ofereça algum bloqueio para países estrangeiros. Por outro lado, o número de IPs disponíveis tende a diminuir com a restrição ou especificação de países de origem.

# Detalhes de módulos
## tor_controller.TorController 

Classe responsável por gerenciar o Tor. Nem sempre ao mandar sinal de mudança de IP ao Tor ele o muda para um diferente, além de que isso pode demorar certo tempo. A principal função dessa classe é cuidar disso e garantir que um IP já usado não seja escolhido novamente por um número antes que outros sejam usados.

Parâmetros:
- control_port: **Int** - Porta de controle do Tor (default 9051)
- password: **String** - Senha usada para controlar Tor (definida passos acima)
- host: **String** - Endereço do servidor proxy Tor (default '127.0.0.1')
- port: **Int** - Porta do servidor proxy Tor
- allow_reuse_ip_after: **Int** - Após um IP ser usado, ele poderá ser usado novamente somente após esse número de outros IPs usados (default 5)

## CamouflageHandler

Classe responsável por mudar IP do Tor, retornar user-agents de uma lista passada e, por fim, gerenciar tempo entre uma requisição feita e outra. 

Utiliza uma instância da classe TorController e são esses seus parâmetros:

- tor_host: **String** - Paramêtro da instância de TorController (default '127.0.0.1')
- tor_port:  **Int** - Paramêtro da instância de TorController (default 9050)
- control_port: **Int** - Paramêtro da instância de TorController (default 9051)
- password: **String** - Paramêtro da instância de TorController (default '')
- allow_reuse_ip_after: **Int** - Paramêtro da instância de TorController (default 5)
- user_agents: **List** - Lista de user-agents (default Lista Vazia) 
- time_between_calls: **Int** -  Tempo fixo entre uma requisição e outra.  
- random_time_between_calls: **Bool** - Se este argumento for verdadeiro, um tempo escolhido ao acaso entre **min_time_between_calls** e **max_time_between_calls** será escolhido **sempre** entre uma requisição e outra. (default False) 
- min_time_between_calls: **Int** - Caso **random_time_between_calls** for verdadeiro, este será o valor mínimo de espera entre uma requisição e outra. (default 0) 
- max_time_between_calls:  **Int** - Caso **random_time_between_calls** for verdadeiro, este será o valor máximo de espera entre uma requisição e outra. (default 10) 

Métodos:
- renew_ip(): Executa o comando para mudar o IP do Tor e espera um certo tempo (7.5s) para que o efeito surja.
- get_user_agent(): Retorna uma **String** representando um user-agent da lista passada na instanciação da classe.
- wait(): Interrompe a execução do programa por um tempo fixo definido em **time_between_calls** ou aleatório, escolhido entre **min_time_between_calls** e **min_time_between_calls**, se **random_time_between_calls** estiver definido como **True**.

## Tor*Webdriver

Classe que herda de **CamouflageHandler** e **selenium.webdriver.***, onde * é Chrome ou Firefox. 

Essa classe especializa determinados métodos (listados abaixo) e são capazes de alterar o IP por determinado número de requisições, limpar cookies e, no caso do Firefox, mudar o user-agent. 

Os parâmetros para gerar uma instância são, na ordem, os mesmos de selenium.webdriver.[Firefox ou Chrome], CamouflageHandler e os seus próprios, mostrado abaixo:

Parâmetros próprios:
- change_ip_after: **Int** - Número de requisições feitas antes de se alterar o IP. (default 42)
- change_user_agent_after: **Int** - (Exclusivo para o Firefox) Número de requisições feitas antes de mudar o user-agent. Caso esse número seja negativo, o user-agent original nunca será alterado. (default -1)
- clear_cookies_after: **Int** - Número de requisições feitas até que se limpe os cookies da sessão.

Métodos:

- get(url: **String**): Especialização do método *get* dos webdrivers. Muda IP, troca user-agent (Firefox) e limpa cookies de acordo com determinado número de requisições feitas, além de controlar o tempo entre uma requisição e outra em um intervalo de tempo fixo ou aleatório. 
- bezier_mouse_move(webelement_to_mouse_move: **webelement**, control_points: **List**, num_random_control_points: **Int**, plot: **Bool**): Método responsável para simular movimentos do mouse em forma de [curvas de Bézier](https://en.wikipedia.org/wiki/B%C3%A9zier_curve). Caso **webelement_to_mouse_move** seja passado, os movimentos ocorrerão sobre ele. Caso contrário, um webelement será criado tendo como base o elemento/tag html. Se **control_points**, uma lista de pontos de controles, for passado, as curvas serão geradas tendo como base esses pontos (devem ser 2-D). Caso contrário, será gerado uma lista com **num_random_control_points** aleatória. Por fim, se **plot**
- renew_user_agent():  (Exclusivo para Firefox) Muda o user-agent aleatoriamente.

Exemplo de uso:

```python
    driver = Tor*Webdriver(tor_password='my password')
```

## TorRequestSession

Herda de CamouflageHandler e de requests.sessions.Session, responsável por criar objetos requests com IPs anônimos.

Os parâmetros para gerar nova instância são os mesmos da classe CamouflageHandler mais dois parâmetros próprios.

Por ser mais leve que os webdrivers, pode ser bastante útil em tarefas simples.

Parâmetros próprios:
- change_ip_after: **Int** - Número de requisições feitas antes de se alterar o IP. (default 42)
- change_user_agent_after: **Int** - Número de requisições feitas antes de mudar o user-agent. Caso esse número seja negativo, o user-agent original nunca será alterado. (default -1)

Métodos:
- get(url: Union[Text, bytes], **kwargs): Especialização do método *get* de requests.Session. Muda IP e troca user-agent de acordo com determinado número de requisições feitas, além de controlar o tempo entre uma requisição e outra em um intervalo de tempo fixo ou aleatório. 


Exemplo de uso:

```python
    driver = TorRequestSession(tor_password='my password')
```

## bezier_curve

Módulo responsável por gerar [curvas de Bézier](https://en.wikipedia.org/wiki/B%C3%A9zier_curve), usadas em movimentos de mouse.

Métodos:
- binomial_coef(n: **Float**, i: **Float**): Retorna o coeficiente binômial de  n e i.
- bernstein(i: **Float**, n: **Float**, t: **Float**): Calcula e retorna o valor de t e i na base polinomial de Bernstein de grau n.
- generate(control_points: **List**, intervals: **Int**): Gera n (default 10) pontos da curva de Bernstein para a lista de pontos de controle, control_points, passada. 
- plot(points: **List**): 'Plota' os pontos, points, em um arquivo salvo com 'bezier_curve_' + data_hora_atual + '.png' 
