Crawler for https://prefeitura.pbh.gov.br/licitacoes. 

As of March 18th 2020, there are 2210 processes. The crawler should run for approximately 5 hours to achieve full coverage (expected: 13GB of data).
 
### Features
- Using ``requests`` and ``wget``
- Downloads the following: 
    - base html for each process page
    - external links
    - attached files (pdf/zip/doc/docx/odt/odf/eml)
- Stops after 5 consecutive void pages 
- Full coverage 

### TODO
- [ ] Access IDs randomly to avoid blocking