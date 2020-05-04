from binary_extractor import BinaryExtractor

text_output_dict = {
    'table': True,
    'texts': True,
}

table_output_dict = {
    'table': True,
    'texts': False,
}

class Factory():
    def __init__(self, path, meta):
        self.output_dict = None

        def type_of_file(self):
            #detection
            pass

    def extractor(path):

        #self.output_dict = text_output_dict
        DOCExtractor = BinaryExtractor(path, doc_output_dict).output()
        PDFExtractor = BinaryExtractor(path, pdf_output_dict).output()
        PPTExtractor = BinaryExtractor(path, ppt_output_dict).output()

        ExcelExtractor = BinaryExtractor(path, excel_output_dict).output()
