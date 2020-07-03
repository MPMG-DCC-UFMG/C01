import sys
sys.path.append("../code")
import unittest
import atomizer as atom
import json


class TestExtractInfo(unittest.TestCase):
    def test_track_parallelizable_fors(self):
        with open("recipe_examples.json") as json_file:
            recipe_examples = json.load(json_file)

        self.assertEqual(atom.track_parallelizable_fors(recipe_examples["unique_for"]["recipe"]),
            [{'iterator': 'i', 'iterable':{'call':{'step': 'range_', 'arguments': {'stop': 2}}}}])
        self.assertEqual(atom.track_parallelizable_fors(recipe_examples["unbreakable_between_breakables"]["recipe"]),
            [
                {'iterator': 'i', 'iterable':{'call':{'step': 'range_', 'arguments': {'stop': 2}}}},
                {'iterator': 'k', 'iterable':{'call':{'step': 'range_', 'arguments': {'stop': 2}}}}
            ])
        self.assertEqual(atom.track_parallelizable_fors(recipe_examples["step_after_the_for"]["recipe"]),[])
        self.assertEqual(atom.track_parallelizable_fors(recipe_examples["step_before_the_for"]["recipe"]),
            [{'iterator': 'i', 'iterable':{'call':{'step': 'range_', 'arguments': {'stop': 2}}}}])
        self.assertEqual(atom.track_parallelizable_fors(recipe_examples["all_cases"]["recipe"]),
            [
                {'iterator': 'h', 'iterable':{'call':{'step': 'range_', 'arguments': {'stop': 2}}}},
                {'iterator': 'j', 'iterable':{'call':{'step': 'range_', 'arguments': {'stop': 2}}}}
            ])

    def test_get_iterable_objects(self):
        ffe = __import__('functions_file_example')
        call_1 = [
            {'iterator': 'j', 'iterable':{'call':{'step': 'no_params', 'arguments': {}}}}
        ]
        self.assertEqual(atom.get_iterable_objects(call_1, module = ffe),
            [{'iterator': 'j', 'iterable':[1,2]}])
        self.assertEqual(atom.get_iterable_objects([], module = ffe),[])

    def test_decrase_depth(self):
        recipe_example = {
            "depth": 1,
            "children":[
                {"depth": 2},
                {
                    "depth": 2,
                    "children":[{"depth": 3}]
                }
            ]
        }
        expected_result = {
            "depth": 0,
            "children":[
                {"depth": 1},
                {
                    "depth": 1,
                    "children":[{"depth": 2}]
                }
            ]
        }

        self.assertEqual(atom.decrase_depth(recipe_example),expected_result)
        self.assertEqual(atom.decrase_depth({"children":[], "depth":1}),{"children":[], "depth":0})


    def test_for_to_attribution(self):
        with open('recipe_examples.json') as file:
            recipe_examples = json.load(file)

        expected_result = [
            {
                "step": "attribution",
                "source": 0,
                "target": "i",
                "depth": 1,
            },
            {
                "step": "print_",
                "arguments": {
                    "word": "teste"
                },
                "depth": 1
            }
        ]


        self.assertEqual(atom.for_to_attribution(recipe_examples['unique_for']['recipe']['children'][0], "i", 0), expected_result)
        self.assertEqual(atom.for_to_attribution({"step":"for", "depth":0, "children":[]}, 'i', 2), [{"step":"attribution", "depth":0, "target":"i", "source":2}])


    def test_replace_fors_to_attributions(self):
        pass

    def test_extend(self):
        pass    

    


if __name__ == '__main__':
    unittest.main()
