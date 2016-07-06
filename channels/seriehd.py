# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# streamondemand.- XBMC Plugin
# Canal para seriehd - based on guardaserie channel
# http://blog.tvalacarta.info/plugin-xbmc/streamondemand.
# ------------------------------------------------------------
import re
import urlparse

from core import config
from core import logger
from core import scrapertools
from core.item import Item
from core.tmdb import infoSod

__channel__ = "seriehd"
__category__ = "S"
__type__ = "generic"
__title__ = "Serie HD"
__language__ = "IT"

headers = [
    ['User-Agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:39.0) Gecko/20100101 Firefox/39.0'],
    ['Accept-Encoding', 'gzip, deflate']
]

host = "http://www.seriehd.org"


def isGeneric():
    return True


def mainlist(item):
    logger.info("[seriehd.py] mainlist")

    itemlist = [Item(channel=__channel__,
                     action="fichas",
                     title="[COLOR azure]Serie TV[/COLOR]",
                     url=host + "/serie-tv-streaming/",
                     thumbnail="http://i.imgur.com/rO0ggX2.png"),
                Item(channel=__channel__,
                     action="sottomenu",
                     title="[COLOR orange]Sottomenu...[/COLOR]",
                     url=host,
                     thumbnail="http://i37.photobucket.com/albums/e88/xzener/NewIcons.png"),
                Item(channel=__channel__,
                     action="search",
                     title="[COLOR green]Cerca...[/COLOR]",
                     thumbnail="http://dc467.4shared.com/img/fEbJqOum/s7/13feaf0c8c0/Search")]

    return itemlist


def search(item, texto):
    logger.info("[seriehd.py] search")

    item.url = host + "/?s=" + texto

    try:
        return fichas(item)

    # Se captura la excepción, para no interrumpir al buscador global si un canal falla.
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def sottomenu(item):
    logger.info("[seriehd.py] sottomenu")
    itemlist = []

    data = scrapertools.anti_cloudflare(item.url, headers)

    patron = '<a href="([^"]+)">([^<]+)</a>'

    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedtitle in matches:
        itemlist.append(
            Item(channel=__channel__,
                 action="fichas",
                 title=scrapedtitle,
                 url=scrapedurl))

    # Elimina 'Serie TV' de la lista de 'sottomenu'
    itemlist.pop(0)

    return itemlist


def fichas(item):
    logger.info("[seriehd.py] fichas")
    itemlist = []

    data = scrapertools.anti_cloudflare(item.url, headers)

    # ------------------------------------------------
    cookies = ""
    matches = re.compile('(.seriehd.org.*?)\n', re.DOTALL).findall(config.get_cookie_data())
    for cookie in matches:
        name = cookie.split('\t')[5]
        value = cookie.split('\t')[6]
        cookies += name + "=" + value + ";"
    headers.append(['Cookie', cookies[:-1]])
    import urllib
    _headers = urllib.urlencode(dict(headers))
    # ------------------------------------------------

    patron = '<h2>(.*?)</h2>\s*'
    patron += '<img src="([^"]+)" alt="[^"]*"/>\s*'
    patron += '<A HREF="([^"]+)">'

    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedtitle, scrapedthumbnail, scrapedurl in matches:
        scrapedthumbnail += "|" + _headers
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle).strip()
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="episodios",
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 fulltitle=scrapedtitle,
                 url=scrapedurl,
                 show=scrapedtitle,
                 thumbnail=scrapedthumbnail), tipo='tv'))

    patron = "<span class='current'>\d+</span><a rel='nofollow' class='page larger' href='([^']+)'>\d+</a>"
    next_page = scrapertools.find_single_match(data, patron)
    if next_page != "":
        itemlist.append(
            Item(channel=__channel__,
                 action="fichas",
                 title="[COLOR orange]Successivo>>[/COLOR]",
                 url=next_page))

    return itemlist


def episodios(item):
    logger.info("[seriehd.py] episodios")
    itemlist = []

    data = scrapertools.anti_cloudflare(item.url, headers)

    patron = r'<iframe width=".+?" height=".+?" src="([^"]+)" allowfullscreen frameborder="0">'
    url = scrapertools.find_single_match(data, patron).replace("?seriehd", "")

    data = scrapertools.cache_page(url).replace('\n', '').replace(' class="active"', '')

    section_stagione = scrapertools.find_single_match(data, '<h3>STAGIONE</h3><ul>(.*?)</ul>')
    patron = '<li[^>]+><a href="([^"]+)">(\d)<'
    seasons = re.compile(patron, re.DOTALL).findall(section_stagione)

    for scrapedseason_url, scrapedseason in seasons:

        season_url = urlparse.urljoin(url, scrapedseason_url)
        data = scrapertools.cache_page(season_url).replace('\n', '').replace(' class="active"', '')

        section_episodio = scrapertools.find_single_match(data, '<h3>EPISODIO</h3><ul>(.*?)</ul>')
        patron = '<li><a href="([^"]+)">(\d+)<'
        episodes = re.compile(patron, re.DOTALL).findall(section_episodio)

        for scrapedepisode_url, scrapedepisode in episodes:
            episode_url = urlparse.urljoin(url, scrapedepisode_url)

            title = scrapedseason + "x" + scrapedepisode.zfill(2)

            itemlist.append(
                Item(channel=__channel__,
                     action="findvideos",
                     title=title,
                     url=episode_url,
                     fulltitle=item.fulltitle,
                     show=item.show,
                     thumbnail=item.thumbnail))

    if config.get_library_support() and len(itemlist) != 0:
        itemlist.append(
            Item(channel=__channel__,
                 title=item.title + " (Add Serie to Library)",
                 url=item.url,
                 action="add_serie_to_library",
                 extra="episodios",
                 show=item.show))
        itemlist.append(
            Item(channel=item.channel,
                 title="Scarica tutti gli episodi della serie",
                 url=item.url,
                 action="download_all_episodes",
                 extra="episodios",
                 show=item.show))

    return itemlist


def findvideos(item):
    logger.info("[seriehd1.py] findvideos")
    itemlist = []

    data = scrapertools.cache_page(item.url).replace('\n', '')

    patron = '<iframe id="iframeVid" width=".+?" height=".+?" src="([^"]+)" allowfullscreen="">'
    url = scrapertools.find_single_match(data, patron)

    if 'hdpass.xyz' in url:
        data = scrapertools.cache_page(url, headers=headers).replace('\n', '').replace('> <', '><')

        patron = '<form method="get" action="">'
        patron += '<input type="hidden" name="([^"]*)" value="([^"]*)"/>'
        patron += '<input type="hidden" name="([^"]*)" value="([^"]*)"/>'
        patron += '<input type="hidden" name="([^"]*)" value="([^"]*)"/>'
        patron += '<input type="hidden" name="([^"]*)" value="([^"]*)"/>'
        patron += '<input type="submit" class="[^"]*" name="([^"]*)" value="([^"]*)"/>'
        patron += '</form>'

        for name1, val1, name2, val2, name3, val3, name4, val4, name5, val5 in re.compile(patron).findall(data):

            get_data = '%s=%s&%s=%s&%s=%s&%s=%s&%s=%s' % (
            name1, val1, name2, val2, name3, val3, name4, val4, name5, val5)

            tmp_data = scrapertools.cache_page('http://hdpass.xyz/film.php?' + get_data, headers=headers)

            patron = r'<input type="hidden" name="urlEmbed" data-mirror="([^"]+)" id="urlEmbed" value="([^"]+)"/>'

            for media_label, media_url in re.compile(patron).findall(tmp_data):
                media_label = scrapertools.decodeHtmlentities(media_label.replace("hosting", "hdload"))

                itemlist.append(
                    Item(channel=__channel__,
                         server=media_label,
                         action="play",
                         title=' - [Player]' if media_label == '' else ' - [Player @%s]' % media_label,
                         url=media_url,
                         folder=False))

    return itemlist


def unescape(par1, par2, par3):
    var1 = par1
    for ii in xrange(0, len(par2)):
        var1 = re.sub(par2[ii], par3[ii], var1)

    var1 = re.sub("%26", "&", var1)
    var1 = re.sub("%3B", ";", var1)
    return var1.replace('<!--?--><?', '<!--?-->')
