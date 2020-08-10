import unittest
from audio_solver import AudioSolver

class AudioSolverTest(unittest.TestCase):
    def setUp(self):
        self.solver = AudioSolver()

    def test_solver(self):
        with self.assertRaises(Exception) as context:
            self.solver.solve(image=1, source="")
            self.assertTrue("Usuário deve informar apenas uma fonte para imagem" in context.exception)

        self.assertRaises(Exception, self.solver.solve)

    def test_preprocess(self):
        self.assertEqual(self.solver.preprocess(1), 1)
