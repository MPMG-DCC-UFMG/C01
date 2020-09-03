"""
"""
class KeywordProcessor(TextsProcessor):

    def __init__(self, input, kwargs):
        super().__init___(self, input, kwargs)

        self.title_keyword = kwargs.get(title_keyword)
        self.header_keyword = kwargs.get(header_keyword)
        self.footer_keyword = kwargs.get(footer_keyword)
        self.end_text_keyword = kwargs.get(end_keyword)

    def process_header(header):
        """
        This function processes the document header.

        Args:
            header(str): the header line of the document.

        """

        pass

    def element_detection(self):
        lines = self.input.splitlines()
         = [i for i in lines if i and not(is_header(i, head) or is_footer(i))]

        return lines

    # recognition:

    def is_header(self, line):
        """
        This function determines if a line is a header of the document.

        Args:
            line(str): a line of the document.
            header(str): the document header.

        Returns:
            True, if they are equal, False otherwise.

        """

        return self.header.startswith(line)

    def is_footer(self, line):
        """
        This function determines if a line is a footer of the document.

        Args:
            line(str): a line of the document.
            footer(str): initial text of a footer line.

        Returns:
            True, if the line is a footer, False otherwise.
        """

        return self.footer.startswith(line)

    def is_title(self, i):
        """
        This function determines if a line starts a new text.

        Args:
            line(str): a line of the document.
            nextline(str): the next line of the document.
            startline(str): the initial text of a new title line.

        Returns:
            True, if the lines indicate a new title, False otherwise.

        """

        line = self.elements[i]
        prev_line = self.elements[i - 1]
        next_line = self.elements[i + 1]

        is_line_1 = line.startswith(self.title_keyword) and next_line.isupper()
        is_line_2 = prev_line.startswith(title_keyword) and line.isupper()

        return is_line_1 or is_line_2

    def end_text(self, line):
        """
        This function determines if a line ends a text.

        Args:
            line(str): a line of the document.
            endline(str): the initial text of a text line.

        Returns:
            True, if the line indicates end the of the text, False otherwise.

        """

        return line.startswith(self.end_text_keyword)
