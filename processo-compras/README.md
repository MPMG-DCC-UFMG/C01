Crawler for https://www1.compras.mg.gov.br/processocompra/processo/consultaProcessoCompra.html. 

As of February 28th 2020, there are 309374 processes. The crawler should run for approximately 20 days to achieve full coverage (expected: 25GB of data).
 
### Features
- Using selenium (geckodriver)
- Downloads the following: 
    - html for tab "visualizacaoArquivosProcesso"
    - relatorioDetalhesProcessoCompra (pdf)
    - Edital (pdf/zip/doc/docx/odt/odf/eml)
    - PublicJornalGrandeCirculacao (pdf/zip/doc/docx/odt/eml)
    - ExtratoPublicacaoEdital (pdf/zip/doc/docx/odt/eml)
- Checks process IDs from 1 to 1000000
    - Stops after 5000 consecutive void IDs 
- Full coverage except for files in "Visualizar dados do pregão"
    - The files from "Visualizar dados do pregão" are identical to the ones obtained by ``consulta-pregoes`` (~45000 processes) 
    
### TODO
- [x] Catch thread exceptions
- [ ] Handle urllib3.connectionpool warnings
- [ ] Access IDs randomly to avoid blocking
- [ ] Merge crawler with ``consulta-pregoes``
