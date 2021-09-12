##############################
###     Logging System     ###
### Author: Kevin Dahlhoff ###
### Version: 1.0           ###
##############################

from datetime import datetime

import os
import getpass
import pathlib
import modules.filesystem as filesystem
# import modules.settings as settings

class ValueException(Exception):
    pass

class Logging():
    def __init__(self):
        #self.standard_path = settings.Settings().standard_path
        self.file_ending = '.log'
        self.log_dir = 'logs'
    
    def init(self, file_name):
        pass
    
    def log(self, level, log, console):
        
        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")

        if type(console) != bool:
            raise ValueException('the specified value is not a bool')
        if level == '':
            raise ValueException('the specified value is not allowed to be empty')

        if console:
            if level == "DEBUG":
                print(f'[DEBUG][{dt_string}] > {log}')
            elif level == "INFO":
                print(f'[INFO][{dt_string}] > {log}')
            elif level == "WARNING":
                print(f'[WARNING][{dt_string}] > {log}')
            elif level == "ERROR":
                print(f'[ERROR][{dt_string}] > {log}')
            elif level == "CRITICAL":
                print(f'[CRITICAL][{dt_string}] > {log}')
        else:
            if filesystem.Filesystem().check_for_dir(self.log_dir):
                pass
            else:
                filesystem.Filesystem().create_dir(self.log_dir)

log = Logging()
log.log('ERROR', 's', False)