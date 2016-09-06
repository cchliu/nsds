from mininet.node import Controller
from os import environ
import os

POXDIR = os.path.join(environ['HOME'] + '/Mininet/pox')

class POX(Controller):
        def __init__(self, name, cdir=POXDIR,
                        command='python pox.py',
                        cargs=('openflow.of_01 --port=%s '
                        'pox.controller.controller_v1'),
                        **kwargs):
                Controller.__init__(self, name, cdir=cdir, command=command, cargs=cargs, **kwargs)

controllers={'pox': POX}

