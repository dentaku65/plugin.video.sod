# -*- coding: iso-8859-1 -*-
#------------------------------------------------------------
# streamondemand
# XBMC entry point
# http://blog.tvalacarta.info/plugin-xbmc/streamondemand/
#------------------------------------------------------------

# Constants
__plugin__  = "streamondemand"
__author__  = "streamondemand"
__url__     = "http://blog.tvalacarta.info/plugin-xbmc/streamondemand/"
__date__ = "26/03/2015"
__version__ = "4.0"

import os
import sys
from core import config
from core import logger

logger.info("streamondemand.default init...")

librerias = xbmc.translatePath( os.path.join( config.get_runtime_path(), 'lib' ) )
sys.path.append (librerias)

from platformcode import launcher

if sys.argv[1] == "1":
    # Esto solo se ejecuta la primera vez que entramos en el plugin
    launcher.start()

launcher.run()