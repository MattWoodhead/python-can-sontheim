# -*- coding: utf-8 -*-
"""
Created on Sun Dec  4 17:12:37 2022

init.py

python-can-sontheim
"""

from .version import __version__
from ._canlib import SontheimBus
from .constants import IS_PYTHON_64BIT
