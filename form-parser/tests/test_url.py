# -*- coding: utf-8 -*-
"""
Rúbia Reis Guerra
rubia-rg@github
Test cases for extracting parameters with URLParser
"""
import unittest
from formparser.url import URLParser


class MyTestCase(unittest.TestCase):
    def test_get_parameters_with_processo_compras_mg(self):
        url = 'https://www1.compras.mg.gov.br/processocompra/processo/' \
              'consultaProcessoCompra.html?' \
              'idProcessoCompraSelecionado=&procedimentoProcessoSelecionado=' \
              '&unidadeCompra=&possuiPregao=&' \
              'possuiEdital=&estaPesquisando=true&metodo=pesquisar' \
              '&textoConfirmacao=&orgaoEntidade=&' \
              'codigoUnidadeCompra=&numero=&ano=&situacao=SUSPENSO' \
              '&procedimentoModificado=&procedimento1=&' \
              'procedimento2=&procedimento3=&procedimento4=&especializacao=' \
              '&dataCriacaoDe=&dataCriacaoAte=&' \
              'dataLicitacaoDe=&dataLicitacaoAte=&linhaFornecimento=' \
              '&linhaFornecimentoOpcaoEOu=E&' \
              'linhaFornecimentoOpcaoSem=&descricaoMaterialOuServico=' \
              '&descricaoMaterialOuServicoOpcaoEOu=E&' \
              'descricaoMaterialOuServicoOpcaoSem=' \
              '&especificacaoItemMaterialOuServico=&' \
              'especificacaoItemMaterialOuServicoOpcaoEOu=E' \
              '&especificacaoItemMaterialOuServicoOpcaoSem='
        params = {'idProcessoCompraSelecionado': [''],
                  'procedimentoProcessoSelecionado': [''],
                  'unidadeCompra': [''],
                  'possuiPregao': [''], 'possuiEdital': [''],
                  'estaPesquisando': ['true'], 'metodo': ['pesquisar'],
                  'textoConfirmacao': [''], 'orgaoEntidade': [''],
                  'codigoUnidadeCompra': [''], 'numero': [''],
                  'ano': [''], 'situacao': ['SUSPENSO'],
                  'procedimentoModificado': [''], 'procedimento1': [''],
                  'procedimento2': [''], 'procedimento3': [''],
                  'procedimento4': [''], 'especializacao': [''],
                  'dataCriacaoDe': [''], 'dataCriacaoAte': [''],
                  'dataLicitacaoDe': [''], 'dataLicitacaoAte': [''],
                  'linhaFornecimento': [''], 'linhaFornecimentoOpcaoEOu': ['E'],
                  'linhaFornecimentoOpcaoSem': [''],
                  'descricaoMaterialOuServico': [''],
                  'descricaoMaterialOuServicoOpcaoEOu': ['E'],
                  'descricaoMaterialOuServicoOpcaoSem': [''],
                  'especificacaoItemMaterialOuServico': [''],
                  'especificacaoItemMaterialOuServicoOpcaoEOu': ['E'],
                  'especificacaoItemMaterialOuServicoOpcaoSem': ['']}
        parser = URLParser(url)
        self.assertDictEqual(params, parser.parameters())

    def test_get_parameters_with_no_parameters(self):
        url = 'google.com'
        params = {}
        parser = URLParser(url)
        self.assertDictEqual(params, parser.parameters())

    def test_get_query_with_processo_compras_mg(self):
        url = 'https://www1.compras.mg.gov.br/processocompra/processo/' \
              'consultaProcessoCompra.html?' \
              'idProcessoCompraSelecionado=&procedimentoProcessoSelecionado=' \
              '&unidadeCompra=&possuiPregao=&' \
              'possuiEdital=&estaPesquisando=true&metodo=pesquisar' \
              '&textoConfirmacao=&orgaoEntidade=&' \
              'codigoUnidadeCompra=&numero=&ano=&situacao=SUSPENSO' \
              '&procedimentoModificado=&procedimento1=&' \
              'procedimento2=&procedimento3=&procedimento4=&especializacao=' \
              '&dataCriacaoDe=&dataCriacaoAte=&' \
              'dataLicitacaoDe=&dataLicitacaoAte=&linhaFornecimento=' \
              '&linhaFornecimentoOpcaoEOu=E&' \
              'linhaFornecimentoOpcaoSem=&descricaoMaterialOuServico=' \
              '&descricaoMaterialOuServicoOpcaoEOu=E&' \
              'descricaoMaterialOuServicoOpcaoSem=' \
              '&especificacaoItemMaterialOuServico=&' \
              'especificacaoItemMaterialOuServicoOpcaoEOu=E' \
              '&especificacaoItemMaterialOuServicoOpcaoSem='
        query = 'idProcessoCompraSelecionado=&procedimentoProcessoSelecionado='\
                '&unidadeCompra=&possuiPregao=&' \
                'possuiEdital=&estaPesquisando=true&metodo=pesquisar' \
                '&textoConfirmacao=&orgaoEntidade=&' \
                'codigoUnidadeCompra=&numero=&ano=&situacao=SUSPENSO' \
                '&procedimentoModificado=&procedimento1=&' \
                'procedimento2=&procedimento3=&procedimento4=&especializacao=' \
                '&dataCriacaoDe=&dataCriacaoAte=&' \
                'dataLicitacaoDe=&dataLicitacaoAte=&linhaFornecimento=' \
                '&linhaFornecimentoOpcaoEOu=E&' \
                'linhaFornecimentoOpcaoSem=&descricaoMaterialOuServico=' \
                '&descricaoMaterialOuServicoOpcaoEOu=E&' \
                'descricaoMaterialOuServicoOpcaoSem=' \
                '&especificacaoItemMaterialOuServico=&' \
                'especificacaoItemMaterialOuServicoOpcaoEOu=E' \
                '&especificacaoItemMaterialOuServicoOpcaoSem='
        parser = URLParser(url)
        self.assertEqual(query, parser.query())

    def test_get_query_with_empty_query(self):
        url = 'google.com'
        query = ''
        parser = URLParser(url)
        self.assertEqual(query, parser.query())


if __name__ == '__main__':
    unittest.main()
