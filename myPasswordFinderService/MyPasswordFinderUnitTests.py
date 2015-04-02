__author__ = 'michal'

import unittest
from myPasswordFinderService.MyPasswordFinder import MyPasswordFinder


class StorageUnitTest(unittest.TestCase):
    def find_pass_test(self):
        with open('Post.txt', 'rU') as f:

            read_data = f.read()
            finder = MyPasswordFinder().find_pass(read_data)
            assert type(finder) is dict or finder is None
