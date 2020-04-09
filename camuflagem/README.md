# Módulo responsável por camuflar coletores
De maneira geral, webdrivers do Selenium ou sessões da biblioteca Requests são especializados para rotacionar IPs, controlar número de requisições por tempo, introduzir aleatoriedade, rotacionar User-Agents, evitar Honeypots, etc.   

## Rotação de IPs
A rotação de IPs ocorrem apenas via Tor. Para seu uso, crie uma instância de TorFirefoxWebdriver ou TorChromeWebdriver e defina pelo parâmetro **change_ip_after** com quantas requisições o IP será alterado. Essas duas classes herdam da classe webdriver.Firefox e webdriver.Chrome, respectivamente. Portanto, os mesmos parâmetros dessas superclasses estão disponíveis em Tor*Webdriver.

Requisitos:
- Acesso **root**
- Instalar o Tor 
    > sudo apt-get install tor

Tor*Webdriver precisa de acesso root para que alterar programaticamente o IP, que é definido pelo Tor. 

É possível específicar as origens dos IPs alterando o arquivo de configuração do Tor, para isso, acesse o mesmo como **root** com seu editor favorito. Sua localização é:
> /etc/tor/torrc

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

> ExitNodes {codigo_pais}

> StrictNodes 1

Por exemplo, para especificar que os IPs tem origem apenas no Brasil, adicione as linhas: 

> ExitNodes {br}

> StrictNodes 1

Também é possível específicar uma lista de países de onde os IPs se originam, da seguinte forma: 

> ExitNodes {br}, {ar}, {cl}

Neste exemplo, os países de origem dos IPs são Brasil, Argentina e Chile. 

Também é possível configurar o Tor para que se nunca use IPs de alguns países, da seguinte forma:

> ExcludeExitNodes {codigo_pais}

Por exemplo, restringindo IPs dos EUA e Canadá:

> ExcludeExitNodes {us}, {ca}

Por fim, para garantir as mudanças, reinicie o Tor:
> sudo service tor restart

Restringir IPs a certos países pode ser útil de diversas formas. Por exemplo, caso algum site ofereça algum bloqueio para países estrangeiros. Por outro lado, o número de IPs disponíveis tende a diminuir com a restrição ou especificação de países de origem.