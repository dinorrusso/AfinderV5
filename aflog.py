#!/usr/bin/env python3
import logging
import os
from posixpath import abspath
import sys

if getattr(sys, 'frozen', False):
    #running in a bundle
    bundle_dir = sys._MEIPASS
else:
    #running in python env
    bundle_dir = os.path.dirname(os.path.abspath(__file__))


LOGFILE=bundle_dir + '/log/afv5.log'
log_file = LOGFILE
# Gets or creates a logger
# logger = logging.getLogger(__name__)  
# set log level
logging.basicConfig(format = '%(asctime)s — %(name)s — %(levelname)s — %(funcName)s:%(lineno)d — %(message)s',
                    level = logging.INFO, 
                    filename = log_file, 
                    filemode = 'w')
# def af_log():
#     logger.info('logfile={}'.format(log_file))
#     return logger