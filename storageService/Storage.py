__author__ = 'michal'

import json


class Storage:
    file_name = ''

    def __init__(self, file_name='Storage.txt'):
        self.file_name = file_name

    def append_to_file(self, o):
        with open(self.file_name, 'a+') as fs:

            fs.write('\n')
            json.dump(o, fs)
