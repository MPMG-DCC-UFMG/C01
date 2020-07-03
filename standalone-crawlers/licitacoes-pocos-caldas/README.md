Crawler for https://pocosdecaldas.mg.gov.br/glossario/licitacoes/. 

As of March 30th 2020, there are 3868 processes. The crawler should run for a few hours achieve full coverage.
 
### Features
- Using selenium (geckodriver)
- Downloads the following: 
    - html for search results
    - html of each tab in 'Saiba mais...'
- Checks process IDs from 1 to 4000
    - Stops after 50 consecutive void IDs 
    
### TODO
- [ ] Access IDs randomly to avoid blocking
- [ ] Download files in `Participantes do Processo > Contratos`
- [ ] Download files in `Atas de Registro de Preços > Atas`