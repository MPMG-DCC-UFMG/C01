import unittest
import numpy as np
from unittest.mock import patch

from captcha_solver.image_solver import ImageSolver
from PIL import Image, ImageDraw, ImageFont


class ImageSolverTest(unittest.TestCase):
    def setUp(self):
        self.solver = ImageSolver()

    @patch("captcha_solver.image_solver.pytesseract")
    def test_solver(self, pytesseract_mock):
        """
            Test main method in the class, which the user access
        """
        self.assertRaises(Exception, self.solver.solve, **{"image":1, "source":""})
        self.assertRaises(Exception, self.solver.solve)
        pytesseract_mock.image_to_string.return_value = "test_string"

        img = Image.new('RGB', (100,100), color = (73, 109, 137))
        self.assertEqual(self.solver.solve(img), "test_string")

    @patch("captcha_solver.image_solver.pytesseract")
    def test_ocr(self, pytesseract_mock):
        """
            Test the OCR method in the class
            this method is based in the Googles' Tesseract
            optical character recognition
        """
        pytesseract_mock.image_to_string.return_value = "test_string"
        img = Image.new('RGB', (100,100), color = (73, 109, 137))
        self.assertEqual(self.solver._ocr(img), "test_string")

    def test_preprocess(self):
        """
            Tests the default method for image preprocessing
        """

        img = Image.new('RGB', (100,100), color = (0, 0, 0))
        self.assertTrue((self.solver.preprocess(img) == np.zeros(shape=(100,100))).all())

if __name__ == '__main__':
    unittest.main()
