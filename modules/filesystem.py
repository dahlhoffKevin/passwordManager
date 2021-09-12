##############################
###     Filesystem         ###
### Author: Kevin Dahlhoff ###
### Version: 1.0           ###
##############################


import os
import getpass
import pathlib
import modules.settings as settings

class Filesystem():
    def __init__(self):
        self.standard_path = settings.Settings().standard_path
        self.file_ending = '.log'
        self.log_dir = 'logs'
    
    # check if a directory already exists
    def check_for_dir(self, dir):
        if os.path.isdir(f"{self.standard_path}{dir}"):
            return True
        else:
            return False

    # creating a directory
    def create_dir(self, dir):
        if not self.check_for_dir(dir) == True:
            os.mkdir(f"{self.standard_path}{dir}")
            return True
        else:
            return False

    # check if a file already exists
    def check_for_file(self, dir, file):
        if os.path.isfile(f"{self.standard_path}{dir}/{file}"):
            return True
        else:
            return False

    # creating a file
    def create_file(self, dir, file):
        if not self.check_for_file(dir, file) == True:
            open(f'{self.standard_path}{dir}/{file}.{self.file_ending}', 'x')

    # write in file
    def write_file(self, dir, file, contents):
        f = file
        f = open(f'{self.standard_path}{dir}/{file}.{self.file_ending}', 'a')
        f.write(f'{contents}')
        f.close()

    # overwrite everything in a file
    def overwrite_file(self, dir, file, contents):
        f = file
        f = open(f'{self.standard_path}{dir}/{file}.{self.file_ending}', 'w')
        f.write(f'{contents}')
        f.close()