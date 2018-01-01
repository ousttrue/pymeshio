import pathlib
import sys
import unittest

HERE = pathlib.Path(__file__).parent
sys.path.append(str(HERE.parent))

from pmd_test import PmdTestCase


def main():
    suite = unittest.TestSuite()
    suite.addTest(PmdTestCase('test_read'))
    runner = unittest.TextTestRunner()
    runner.run(suite)


if __name__ == '__main__':
    main()
