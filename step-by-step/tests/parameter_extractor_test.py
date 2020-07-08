import unittest

from step_crawler.tests import functions_file_example as ffe
from step_crawler.parameter_extractor import *


class TestExtractInfo(unittest.TestCase):
    expected_results = [
        {
            "name": "mandatory_and_optional_params",
            "mandatory_params": [
                "some",
                "parameters"
            ],
            "optional_params": {
                "to": 1,
                "test": None
            }
        },
        {
            "name": "only_mandatory_params",
            "mandatory_params": [
                "some",
                "parameters",
                "to",
                "test"
            ],
            "optional_params": {}
        },
        {
            "name": "only_optional_params",
            "mandatory_params": [],
            "optional_params": {
                "some": "some",
                "parameters": "parameters",
                "to": "to",
                "test": "test"
            }
        },
        {
            "name": "no_params",
            "mandatory_params": [],
            "optional_params": {}
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
        ffe = __import__('step_crawler.tests.functions_file_example')
        result = get_module_functions_info(ffe)

        # Because they may be out of order, and contains unhashable items
        self.assertEqual(
            [i in result for i in self.expected_results], [1, 1, 1, 1])


if __name__ == '__main__':
    unittest.main()
