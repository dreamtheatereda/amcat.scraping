# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import
###########################################################################
#          (C) Vrije Universiteit, Amsterdam (the Netherlands)            #
#                                                                         #
# This file is part of AmCAT - The Amsterdam Content Analysis Toolkit     #
#                                                                         #
# AmCAT is free software: you can redistribute it and/or modify it under  #
# the terms of the GNU Affero General Public License as published by the  #
# Free Software Foundation, either version 3 of the License, or (at your  #
# option) any later version.                                              #
#                                                                         #
# AmCAT is distributed in the hope that it will be useful, but WITHOUT    #
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or   #
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public     #
# License for more details.                                               #
#                                                                         #
# You should have received a copy of the GNU Affero General Public        #
# License along with AmCAT.  If not, see <http://www.gnu.org/licenses/>.  #
###########################################################################

from amcat.tools.scraping.processors import HTTPScraper
from amcat.tools.scraping.objects import Document

from amcat.models.medium import Medium
from amcat.tools import toolkit

import re, json, locale, urllib, urlparse

from lxml.html import tostring

locale.setlocale(locale.LC_TIME, str('nl_NL.UTF-8'))

getm = lambda m: Medium.objects.get(id=m)

ARTS = json.load(open('/home/martijn/arts.json'))

SEARCH_URL = "http://beta.uitzendinggemist.nl/quicksearch/episodes?series_id=%d&periode=&query=%s&episode_id="
OEMBED_URL = "http://beta.uitzendinggemist.nl/oembed.xml?url=%s"

NAME_SERIES_MAP = {
    'nieuwsuur' : 975,
    'nos 20:00' : 51,
    'de ochtendspits' : 1054,
    'een vandaag' : 17,
    'uitgesproken vara' : 973,
    'pownews' : 1225,
    'brandpunt' : 1128,
    'altijd wat' : 1084,
    'moraalridders' : 1029,
    'journaal op 3' : 297,
    'tegenlicht' : 1221,
    'goudzoekers' : 1027,
    'in de schaduw van het nieuws' : 1790,
    'zembla' : 181,
    'reporter' : 605,
    'rondom 10' : 1114
}

EPISODE_RE = re.compile('episode_([0-9]+)')
OBJECT_RE = re.compile('(\<object.+\<\/object\>)')

class UGScraper(HTTPScraper):
    def init(self):
        self.scraped_headlines = []

        return (Document(aid=aid, mid=mid, headline=headline) for aid, mid, headline in ARTS)

    def get(self, page):
        medium = unicode(getm(page.props.mid)).lower()
        headline = page.props.headline

        date = toolkit.readDate(headline).strftime('%a %d %b %Y')
        sid = NAME_SERIES_MAP[medium]

        url = SEARCH_URL % (sid, urllib.quote(date))

        try:
            episode = EPISODE_RE.search(self.getdoc(url, lxml=False)).groups(1)[0]
        except:
            #print(url)
            return []

        page.props.episode_url = urlparse.urljoin(SEARCH_URL, '/afleveringen/%s' % episode)
        
        url = OEMBED_URL % urlparse.urljoin(SEARCH_URL, '/afleveringen/%s' % episode)
        page.props.embed_url = url

        #print(self.getdoc(url, lxml=False))

        page.props.embed_flash = OBJECT_RE.search(self.getdoc(url, lxml=False)).groups()[0]

        del page.props.headline
        del page.props.mid

        return [page,]


if __name__ == '__main__':
    #from amcat.tools.scraping.manager import main
    #main(BorstkankerPrikbordScraper)

    import logging; log=logging.getLogger(__name__)

    from amcat.tools.scraping.exporters.builtin import JSONExporter
    s = UGScraper(JSONExporter('/home/martijn/embeds.json'), max_threads=10)
    s.scrape()
