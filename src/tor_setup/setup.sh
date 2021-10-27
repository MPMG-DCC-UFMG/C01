# instala o Tor
sudo apt-get install tor
sudo service tor stop

# copia o arquivo de configuração do Tor 
sudo cp src/tor_setup/torrc /etc/tor/
sudo service tor start


# instala Privoxy
sudo apt-get install privoxy
sudo service privoxy stop

# copia o arquivo de configuração do Privoxy
sudo cp src/tor_setup/config /etc/privoxy/
sudo service privoxy start