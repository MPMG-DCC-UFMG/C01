import unittest
import numpy as np
from image_solver import ImageSolver
from PIL import Image, ImageDraw, ImageFont


class ImageSolverTest(unittest.TestCase):
    def setUp(self):
        self.solver = ImageSolver()

    def test_solver(self):
        with self.assertRaises(Exception) as context:
            self.solver.solve(image=1, source="")
            self.assertTrue("Usuário deve informar apenas uma fonte para imagem" in context.exception)

        self.assertRaises(Exception, self.solver.solve)

        img = Image.new('RGB', (100,100), color = (73, 109, 137))
        self.assertEqual(self.solver.solve(img), "")

    def test_ocr(self):
        img = Image.new('RGB', (100,100), color = (73, 109, 137))
        self.assertEqual(self.solver._ocr(img), "")

    def test_preprocess(self):
        img = Image.new('RGB', (100,100), color = (0, 0, 0))
        self.assertTrue((self.solver.preprocess(img) == np.zeros(shape=(100,100))).all())

