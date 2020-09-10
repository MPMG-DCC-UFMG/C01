"""
"""

class TextsProcessor():
    """
    """

    def __init__(self, input, **kwargs):
        self.input = input
        self.header = self.header_detection()
        self.footer = self.footer_detection()
        self.elements = self.element_detection(self.input.splitlines())

    # recognition:

    @abc.abstractmethod
    def is_header(self, element):
        pass

    @abc.abstractmethod
    def is_footer(self, element):
        pass

    @abc.abstractmethod
    def is_title(self, element):
        pass

    @abc.abstractmethod
    def end_text(self, element):
        pass

    # processing:
    @abc.abstractmethod
    def element_detection(self):
        pass

    def process(self):

        product = {}
        section = []
        text = []
        title = '-' + self.header
        product[title] = section

        for i, element in enumerate(self.elements):
            if not is_title(i, self.elements):
                text.append(element)

                if end_text(element):
                # new text, but not new subject (same title)
                    section.append(text)
                    text = []
            else:
                section.append(text)
                # new subject: starts a new section and a new text
                title = str(i) + '-' + self.elements[i]
                section = []
                product[title] = section
                text = []
        section.append(text)

        return product

    # retrieval:

    def return_product(self):
        product = self.process()
        title, content = texts_to_columns(product)

        return columns_to_dataframe(title, content, 'Título', 'Conteúdo')

    # retrieval metadata:
