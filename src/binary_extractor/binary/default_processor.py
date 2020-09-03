"""
"""

class DefaultProcessor(TextsProcessor):

    def element_detection(self):
        lines = self.input.splitlines()
        lines = [i for i in lines if i and not(is_header(i, head) or is_footer(i))]

        return lines

    def is_header(self, line):
        return False

    def is_footer(self, line):
        return False

    def is_title(self, i):
        """
        This function tries to determine if a line is a title or a part of a text.

        Args:
            i (int): Index of the line.
            lines (list): List of all the text lines.

        Return:
            boolean: True if the line can be a title, False otherwise.

        """

        line = self.elements[i]

        if not is_between_parenthesis(line):
            if len(lines) > i + 1:
                next_line = self.elements[i + 1]

                if not final_sentence(line) and not line[-1:] == ',':
                    if line.isupper() and not end_text(next_line):
                        return True
                    if line.istitle():
                        return True
                    if line[0].isupper() and line[-1:] == ':':
                        if next_line[0].isupper():
                            return True
        return False


    def end_text(self, i):
        """
        Determines if a line from the content looks like a final sentence line.

        Args:
            line (str): The line from the content.

        Returns:
            boolean: True, if it looks final, False otherwise.

        """

        return self.elements[i][-1:] in END_PUNCTUATION

    def is_between_parenthesis(line):
        """
        This function determines if a line from the content is between parenthesis.

        Args:
            line (str): The line from the content.

        Returns:
            boolean: True, if the line is between parenthesis, False otherwise.

        """

        return line[0] == '(' and line[-1:] == ')'
