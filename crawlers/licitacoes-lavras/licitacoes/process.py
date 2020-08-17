"""
Rúbia Reis Guerra
rubia-rg@github
Treats 'Licitaçoes' processes at https://lavras.mg.gov.br/
"""
from licitacoes import utils
from selenium.common import exceptions


class BiddingProcess:
    def __init__(self, process_count, search_results):
        self.process = search_results.find_element_by_xpath("/html/body/div[7]/div[1]/div[1]/div[2]/"
                                                            "div/div[3]/table/tbody/tr[2]/td/div/table/"
                                                            "tbody/tr/td/table/tbody/tr[" +
                                                            str(2 * process_count) + "]/td[1]/a")
        self.process_id = utils.get_process_id(self.process)

        try:
            self.process.click()
        except exceptions.ElementClickInterceptedException:
            search_results.execute_script("arguments[0].scrollIntoView();", self.process)
            self.process.click()

    def extract_html_table(self, tab, driver):
        try:
            table = self.process.find_element_by_xpath("/html/body/div[7]/"
                                                       "div[1]/div[1]/div[2]/"
                                                       "div/div[4]/table")
            tab = table.find_element_by_xpath("/html/body/div[7]/div[1]/"
                                              "div[1]/div[2]/div/div[4]/"
                                              "table/tbody/"
                                          "tr[2]/td/table/tbody/tr[1]/td/"
                                              "table/tbody/tr/td[" + str(tab) +
                                          "]/table/tbody/tr[2]/td[2]/div/div/"
                                          "div")
            tab_title = tab.get_attribute('innerHTML')
            tab.click()
            if tab_title in 'Participantes do Processo':
                self.extract_contracts(driver)
            # TODO
            # elif tab_title in 'Atas de Registro de Preços'
            #     self.extract_atas()
            table_html = table.get_attribute('innerHTML')
            utils.save_html(table_html, self.process_id, tab_title)
        except:
            raise

    def return_search_results(self):
        return_button = self.process.find_element_by_xpath("/html/body/div[7]"
                                                           "/div[1]/div[1]/"
                                                           "div[2]/div/div[4]/"
                                                           "div[1]/a[3]")
        return_button.click()

    def extract_process_data(self, driver):
        for tab in range(2, 7):
            self.extract_html_table(tab, driver)
        self.return_search_results()
        return driver

    def extract_contracts(self, driver):
        for contract_number in range(2, 21):
            try:
                contract = self.process.find_element_by_xpath(
                    '/html/body/div[7]/div[1]/div[1]/div[2]/div/div[4]/'
                    'table/tbody/tr[2]/td/table/tbody/tr[2]/td/div/div[2]'
                    '/table/tbody/tr[' + str(contract_number) +
                    ']/td[5]/table/tbody/tr/td/table/tbody/tr/td/a')
                contract.click()
            except exceptions.ElementClickInterceptedException:
                contract = self.process.find_element_by_xpath('/html/body/div[7]/div[1]/div[1]/div[2]/div/div[4]/'
                                                              'table/tbody/tr[2]/td/table/tbody/tr[2]/td/div/div[2]'
                                                              '/table/tbody/tr[' + str(contract_number) +
                                                              ']/td[5]/table/tbody/tr/td/table/tbody/tr/td/a')
                self.process.execute_script("arguments[0].scrollIntoView();", contract)
                contract.click()
            except exceptions.NoSuchElementException:
                continue

            # TODO
            # download_link = contract.find_element_by_xpath("/html/body/div[8]/div/table/tbody/tr[2]/td[2]/div/table/"
            #                                                "tbody/tr[1]/td/div/table/tbody/tr[10]/td/div/table/tbody/"
            #                                                "tr[2]/td[5]/table/tbody/tr/td/a")
            # download_link.click()
            utils.wait_page_load(driver, element_xpath="/html/body/div[10]/div/table/tbody/tr[2]/td[2]/div/table"
                                                       "/tbody/tr[2]/td/table/tbody/tr/td/button")
            contract_table = driver.find_element_by_xpath("/html/body/div[10]/div")
            contract_id = contract_table.find_element_by_xpath("/html/body/div[10]/div/table/tbody/tr[2]/td[2]/"
                                                               "div/table/tbody/tr[1]/td/div/table/tbody/tr[1]/td["
                                                               "2]/div").get_attribute('innerHTML')
            contract_number, contract_year = utils.parse_process_id(contract_id)
            contract_filename = "Contrato " + contract_year + '-' + contract_number
            contract_html = contract_table.get_attribute('innerHTML')
            utils.save_html(contract_html, self.process_id, contract_filename)
            close_button = contract.find_element_by_xpath("/html/body/div[10]/div/table/tbody/tr[2]/td[2]/div/table/"
                                                          "tbody/tr[2]/td/table/tbody/tr/td/button")
            close_button.click()

    # TODO
    # def extract_atas(self):
    #     pass
