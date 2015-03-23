__author__ = 'michal'

import unittest
from Storage import Storage


class StorageUnitTest(unittest.TestCase):
    def append_to_file_test(self):
        storage = Storage(file_name='UnitTest.txt')
        storage.append_to_file(
            {
                'A': 10,
                'B': 'XYZ'
            })


