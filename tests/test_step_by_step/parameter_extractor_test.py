from step_crawler.parameter_extractor import *
import unittest
import sys
import examples.functions_file_example as ffe



class TestExtractInfo(unittest.TestCase):
    expected_results = [
        {
            "name": "mandatory_and_optional_params",
            "executable_contexts": ["page", "tab", "iframe"],
            "name_display": "Mandatory and optional params",
            "mandatory_params": [
                "some",
                "parameters"
            ],
            "optional_params": {
                "to": 1,
                "test": None
            },
            'field_options': {}
        },
        {
            "name": "only_mandatory_params",
            "executable_contexts": ["page", "tab", "iframe"],
            "name_display": "Only mandatory params",
            "mandatory_params": [
                "some",
                "parameters",
                "to",
                "test"
            ],
            "optional_params": {},
            'field_options': {}
        },
        {
            "name": "only_optional_params",
            "executable_contexts": ["page", "tab", "iframe"],
            "name_display": "Only optional params",
            "mandatory_params": [],
            "optional_params": {
                "some": "some",
                "parameters": "parameters",
                "to": "to",
                "test": "test"
            },
            'field_options': {}
        },
        {
            "name": "no_params",
            "executable_contexts": ["page", "tab", "iframe"],
            "name_display": "No params",
            "mandatory_params": [],
            "optional_params": {},
            'field_options': {}
        },
        {
            "name": "with_params_and_field_options",
            "executable_contexts": ["page", "tab", "iframe"],
            "name_display": "With params and field_options",
            "mandatory_params": [
                "test"
            ],
            "optional_params": {},
            "field_options": {"test" : {"field_type" : "number", "input_placeholder" : "test"}}
        }
    ]

    def test_extract_info(self):
        self.assertEqual(extract_info(ffe.mandatory_and_optional_params),
                         self.expected_results[0])
        self.assertEqual(extract_info(ffe.only_mandatory_params),
                         self.expected_results[1])
        self.assertEqual(extract_info(ffe.only_optional_params),
                         self.expected_results[2])
        self.assertEqual(extract_info(ffe.no_params),
                         self.expected_results[3])

    def test_get_module_functions_info(self):
        # Testing this function, the get_module_functions
        # is also implicitly tested

        result = get_module_functions_info(ffe)

        # Because they may be out of order, and contains unhashable items
        self.assertEqual(
            [i in result for i in self.expected_results], [1, 1, 1, 1, 1])


if __name__ == '__main__':
    unittest.main()
