from step_crawler import atomizer as atom
from step_crawler import code_generator as cg
from pyext import RuntimeModule
import json
import unittest
import sys
sys.path.append("../")




class TestExtractInfo(unittest.TestCase):
    def test_dict_to_arguments(self):
        result = cg.dict_to_arguments({'a': 'a', 'b': 'b', 'c': 'c'})
        expected_result = "a = a, b = b, c = c"
        self.assertEqual(expected_result, result)

        result = cg.dict_to_arguments({'a': 'a'})
        expected_result = "a = a"
        self.assertEqual(expected_result, result)

        result = cg.dict_to_arguments({})
        expected_result = ""
        self.assertEqual(expected_result, result)

    def test_generate_call(self):
        result = cg.generate_call("print", {'a': 'a', 'b': 'b', 'c': 'c'})
        expected_result = "print(a = a, b = b, c = c)"
        self.assertEqual(expected_result, result)

        result = cg.generate_call("print", {'a': 'a'})
        expected_result = "print(a = a)"
        self.assertEqual(expected_result, result)

        result = cg.generate_call("print", {})
        expected_result = "print()"
        self.assertEqual(expected_result, result)

        result = cg.generate_call("print", {'a': 'a', 'b': 'b', 'c': 'c'},
                                  True)
        expected_result = "await print(**missing_arguments, " \
                          "a = a, b = b, c = c)"
        self.assertEqual(expected_result, result)

        result = cg.generate_call("print", {'a': 'a'}, True)
        expected_result = "await print(**missing_arguments, a = a)"
        self.assertEqual(expected_result, result)

        result = cg.generate_call("print", {}, True)
        expected_result = "await print(**missing_arguments, )"
        self.assertEqual(expected_result, result)

    def test_generate_head(self):
        result = cg.generate_head(json)
        expected_result = "import step_crawler\n"
        expected_result += "from " + "json" + " import *\n\n"
        expected_result += "async def "
        expected_result += "execute_steps(**missing_arguments):\n"
        expected_result += "    pages = {}\n"
        expected_result += "    page = missing_arguments['page']\n"
        self.assertEqual(expected_result, result)

    def test_generate_body(self):
        with open("tests/test_step_by_step/examples/recipe_examples.json") as file:
            recipe_examples = json.load(file)
        ff = __import__("step_crawler").functions_file

        result = cg.generate_body(
            recipe_examples['unbreakable_between_breakable']['recipe'], ff)
        expected_result = "    for i in [1, 2, 3]:\n"
        expected_result += "        for j in range_(stop = 2):\n"
        expected_result += "            for k in range_(stop = 2):\n"
        expected_result += "                print_(word = \"teste\")\n"
        self.assertEqual(expected_result, result)

        result = cg.generate_body(atom.extend(
            recipe_examples['unbreakable_between_breakable']['recipe'])[0], ff)
        expected_result = "    i = 1\n"
        expected_result += "    for j in range_(stop = 2):\n"
        expected_result += "        k = 0\n"
        expected_result += "        print_(word = \"teste\")\n"
        self.assertEqual(expected_result, result)

    # def test_generate_code(self):
    #     with open("tests/test_step_by_step/examples/recipe_examples.json") as file:
    #         recipe_examples = json.load(file)

    #     ff = __import__("step_crawler").functions_file

    #     code  = "import step_crawler\n"
    #     code += "from " + "step_crawler.functions_file" + " import *\n\n"
    #     code += "async def "
    #     code += "execute_steps(**missing_arguments):\n"
    #     code += "    pages = {}\n"
    #     code += "    page = missing_arguments['page']\n"
    #     code += "    for i in range_(stop = 2):\n"
    #     code += "        for j in range_(stop = 2):\n"
    #     code += "            for k in range_(stop = 2):\n"
    #     code += "                print_(word = \"teste\")\n"
    #     code += "    return pages"


    #     expected_result = RuntimeModule.from_string("steps", code)
    #     result = cg.generate_code(recipe_examples['unbreakable_between_breakable']['recipe'], ff)
    #     self.assertEqual(expected_result, result)


if __name__ == '__main__':
    unittest.main()
