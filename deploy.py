__author__ = 'ciacicode'

import os
from yaml import load, dump
try:
    with open('app.yaml', 'rb') as yam:
        configuration = load(yam)
        version = configuration.version
        application = configuration.application
        #deploy new version
    command = 'appcfg.py update -A ' + str(application)+ ' -V v' + str(version) + ' .'
    os.system(command)
    #make new version default
    update_default= 'appcfg.py set_default_version -V v' + str(version) + ' -A ' + str(application)
    os.system()
except IOError as e:
    print e
except SystemError as e:
    print e





