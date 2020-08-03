from step_crawler import step_generators as sg
import step_crawler.functions_file as ff
import json
import unittest
import sys
sys.path.append("../")






class TestExtractInfo(unittest.TestCase):
    def test_generate_for(self):
        with open("examples/recipe_examples.json") as file:
            recipe_examples = json.load(file)


        expected_result = "    for i in [1, 2, 3]:\n"
        expected_result += "        for j in range_(stop = 2):\n"
        expected_result += "            for k in range_(stop = 2):\n"
        expected_result += "                print_(word = \"teste\")\n"

        result = sg.generate_for(recipe_examples['unbreakable_between_breakable']['recipe']['children'][0], ff)

        self.assertEqual(expected_result, result)



if __name__ == '__main__':
    unittest.main()
