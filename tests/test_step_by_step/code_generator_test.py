from step_crawler import atomizer as atom
from step_crawler import code_generator as cg
import step_crawler.functions_file as ff
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
        result = cg.generate_head(json, "test_path")
        expected_result = "import step_crawler\n"
        expected_result += "from " + "json" + " import *\n\n"
        expected_result += "async def "
        expected_result += "execute_steps(**missing_arguments):\n"
        expected_result += "    pages = {}\n"
        expected_result += "    page = missing_arguments['pagina']\n"
        expected_result += "    page_stack = []\n"
        expected_result += "    iframe_stack = []\n"
        expected_result += "    scrshot_path = \"test_path\"\n"
        self.assertEqual(expected_result, result)

    def test_generate_body(self):
        with open("tests/test_step_by_step/examples/recipe_examples.json") as file:
            recipe_examples = json.load(file)
        ff = __import__("step_crawler").functions_file

        result = cg.generate_body(
            recipe_examples['unbreakable_between_breakable']['recipe'], ff,
            False)
        expected_result = "    for i in [1, 2, 3]:\n"
        expected_result += "        for j in repete(vezes = 2):\n"
        expected_result += "            for k in repete(vezes = 2):\n"
        expected_result += "                imprime(texto = \"teste\")\n"
        self.assertEqual(expected_result, result)

        result = cg.generate_body(atom.extend(
            recipe_examples['unbreakable_between_breakable']['recipe'])[0],
            ff, False)
        expected_result = "    i = 1\n"
        expected_result += "    for j in repete(vezes = 2):\n"
        expected_result += "        k = 0\n"
        expected_result += "        imprime(texto = \"teste\")\n"
        self.assertEqual(expected_result, result)

    def test_generate_para_cada(self):
        with open("tests/test_step_by_step/examples/recipe_examples.json") as file:
            recipe_examples = json.load(file)


        expected_result = "    for i in [1, 2, 3]:\n"
        expected_result += "        for j in repete(vezes = 2):\n"
        expected_result += "            for k in repete(vezes = 2):\n"
        expected_result += "                imprime(texto = \"teste\")\n"

        result = cg.generate_para_cada(
            recipe_examples['unbreakable_between_breakable']['recipe']['children'][0],
            ff, False)

        self.assertEqual(expected_result, result)

        # test case with iteration-skipping on errors
        result = cg.generate_para_cada(
            recipe_examples['unique_for']['recipe']['children'][0], ff,
            True)
        expected_result = "    for i in repete(vezes = 2):\n"
        expected_result += "        initial_page_stack_len1 = len(page_stack)\n"
        expected_result += "        try:\n"
        expected_result += "            imprime(texto = \"teste\")\n"
        expected_result += "        except Exception as e:\n"
        expected_result += "            print(\"Erro em iteração: \" + str(e))\n"
        expected_result += "            print(\"Continuando para a próxima iteração.\")\n"
        expected_result += "            while len(page_stack) > initial_page_stack_len1:\n"
        expected_result += cg.generate_fechar_aba({'depth': 4}, ff)

        self.assertEqual(expected_result, result)

    def test_generate_enquanto(self):
        with open("tests/test_step_by_step/examples/recipe_examples.json") as file:
            recipe_examples = json.load(file)

        # Regular while loop
        result = cg.generate_body(atom.extend(
            recipe_examples['simple_while']['recipe'])[0], ff, False)
        expected_result = "    while await objeto(**missing_arguments, objeto = True == 1):\n"
        expected_result += "        imprime(texto = \"teste\")\n"
        self.assertEqual(expected_result, result)

        # Inverted while loop
        result = cg.generate_body(atom.extend(
            recipe_examples['inverted_while']['recipe'])[0], ff, False)
        expected_result = "    while not await objeto(**missing_arguments, objeto = True == 1):\n"
        expected_result += "        imprime(texto = \"teste\")\n"
        self.assertEqual(expected_result, result)

    def test_generate_se(self):
        with open("tests/test_step_by_step/examples/recipe_examples.json") as file:
            recipe_examples = json.load(file)

        # Regular if statement
        result = cg.generate_body(atom.extend(
            recipe_examples['simple_if']['recipe'])[0], ff, False)
        expected_result = "    if await objeto(**missing_arguments, objeto = True == 1):\n"
        expected_result += "        imprime(texto = \"teste\")\n"
        self.assertEqual(expected_result, result)

        # Inverted if statement
        result = cg.generate_body(atom.extend(
            recipe_examples['inverted_if']['recipe'])[0], ff, False)
        expected_result = "    if not await objeto(**missing_arguments, objeto = True == 1):\n"
        expected_result += "        imprime(texto = \"teste\")\n"
        self.assertEqual(expected_result, result)

    def test_generate_executar_em_iframe(self):
        with open("tests/test_step_by_step/examples/recipe_examples.json") as file:
            recipe_examples = json.load(file)

        # Getting in and out of an iframe
        result = cg.generate_body(atom.extend(
            recipe_examples['iframe_exec']['recipe'])[0], ff, False)

        expected_result = "\n"
        expected_result += "    ### Início: Passando o contexto de execução para iframe ###\n"
        expected_result += '    el_locator_xpath = "teste"\n'
        expected_result += '    el_locator = missing_arguments["pagina"].locator(f"xpath={el_locator_xpath}")\n'
        expected_result += '    await el_locator.wait_for()\n'
        expected_result += '    el_handler = await el_locator.first.element_handle()\n'
        expected_result += '    iframe_stack.append(await el_handler.content_frame())\n'
        expected_result += '    missing_arguments["pagina"] = iframe_stack[-1]\n'
        expected_result += "    ### Fim: Passando o contexto de execução para iframe ###\n"
        expected_result += "\n"
        expected_result += "    ### Início: Saindo do contexto de iframe ###\n"
        expected_result += '    iframe_stack.pop()\n'
        expected_result += '    if not iframe_stack:\n'
        expected_result += '        missing_arguments["pagina"] = page\n'
        expected_result += '    else:\n'
        expected_result += '        missing_arguments["pagina"] = iframe_stack[-1]\n'
        expected_result += "    ### Fim: Saindo do contexto de iframe ###\n\n"

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
    #     code += "    for i in repete(vezes = 2):\n"
    #     code += "        for j in repete(vezes = 2):\n"
    #     code += "            for k in repete(vezes = 2):\n"
    #     code += "                imprime(texto = \"teste\")\n"
    #     code += "    return pages"


    #     expected_result = RuntimeModule.from_string("steps", code)
    #     result = cg.generate_code(recipe_examples['unbreakable_between_breakable']['recipe'], ff)
    #     self.assertEqual(expected_result, result)


if __name__ == '__main__':
    unittest.main()
