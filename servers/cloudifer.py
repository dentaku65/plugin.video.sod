# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Conector para cloudifer
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------

import urlparse,urllib2,urllib,re
import os

from core import scrapertools
from core import logger
from core import config

def get_video_url( page_url , premium = False , user="" , password="", video_password="" ):
    logger.info("[cloudifer.py] get_video_url(page_url='%s')" % page_url)
    video_urls = []
    return video_urls

# Encuentra vídeos del servidor en el texto pasado
def find_videos(data):
    encontrados = set()
    devuelve = []

    # http://cloudifer.net/embed/6ls
    patronvideos  = '(cloudifer.net/embed/[a-z0-9]+)'
    logger.info("[cloudifer.py] find_videos #"+patronvideos+"#")
    matches = re.compile(patronvideos,re.DOTALL).findall(data)

    for match in matches:
        titulo = "[cloudifer]"
        url = "http://"+match
        if url not in encontrados:
            logger.info("  url="+url)
            devuelve.append( [ titulo , url , 'cloudifer' ] )
            encontrados.add(url)
        else:
            logger.info("  url duplicada="+url)

    return devuelve
