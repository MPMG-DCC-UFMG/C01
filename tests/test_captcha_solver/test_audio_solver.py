import unittest

from captcha_solver.audio_solver import AudioSolver

class AudioSolverTest(unittest.TestCase):
    def setUp(self):
        self.solver = AudioSolver()

    def test_solver(self):
        """
            Test main method in the class, which the user access
        """

        self.assertRaises(Exception, self.solver.solve, **{"audio":1, "source":""})
        self.assertRaises(Exception, self.solver.solve)

    def test_preprocess(self):
        """
            Tests the default method for audio preprocessing
        """

        self.assertEqual(self.solver.preprocess(1), 1)

if __name__ == '__main__':
    unittest.main()