import unittest
from .test_board import BoardTestSuite
from .test_ai import AiTestSuite


def run_mytests():
    test_classes = [BoardTestSuite, AiTestSuite]

    loader = unittest.TestLoader()
    test_suites = []
    for test_class in test_classes:
        suite = loader.loadTestsFromTestCase(test_class)
        test_suites.append(suite)

    final_suite = unittest.TestSuite(test_suites)

    runner = unittest.TextTestRunner()
    runner.run(final_suite)


if __name__ == "__main__":
    run_mytests()
