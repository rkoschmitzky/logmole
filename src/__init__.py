__version__ = "0.7.0"

import logging
import sys

LOG = logging.getLogger("logmole")
logging.basicConfig(stream=sys.__stdout__, level=logging.INFO)


from logmole import *