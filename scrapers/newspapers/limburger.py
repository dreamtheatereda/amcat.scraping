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

from amcat.tools.scraping.processors import PCMScraper
from amcat.tools.scraping.objects import HTMLDocument, IndexDocument
from amcat.tools.scraping import toolkit as stoolkit

from amcat.models.scraper import Scraper

import re

SESSION_URL = "http://mgl.x-cago.net/session.do"
LOGINURL = "http://mgl.x-cago.net/login.do?pub=ddl&auto=false"

INDEX_URL = "http://krantdigitaal.ddl.x-cago.net/DDL/%(year)d%(month)02d%(day)02d/public/index_editions_js.html"
INDEX_PAGE_URL = "http://krantdigitaal.ddl.x-cago.net/DDL/%(year)d%(month)02d%(day)02d/public/index.html"

INDEX_RE = re.compile('"(DDL-.+)"')

try:
    from urllib import urlencode
    from urlparse import urljoin
except ImportError:
    from urllib.parse import urlencode, urljoin

DEBUG = True

class LimburgerScraper(PCMScraper):
    def __init__(self, exporter, max_threads=None, editie='MA'):
        """
        @type editie: str
        @param editie: 'editie' to scrape:
         * HL: Heuvelland
         * HE: Heerlen
         * MA: Maastricht
         * SI: Sittard-Geleen
         * NL: Venray / Venlo
         * ML: Weert / Roermond
        """
        self.editie = editie

        super(LimburgerScraper, self).__init__(exporter, max_threads=max_threads)

    def login(self):
        POST_DATA = Scraper.objects.get(class_name=LimburgerScraper.__name__).get_data()
        login1 = self.session.open(LOGINURL, urlencode(POST_DATA))

        if "Sessie overschrijven" in login1.read():
            data = urlencode(dict(overwrite='on', pub='ddl'))
            return self.session.open(SESSION_URL, data)

    def _get_codes(self, lines, edition):
        # See krantdigitaal.ddl.x-cago.net/DDL/20110712/public/index_editions_js.html
        while True:
            line = lines.pop(0)
            if edition in line:
                lines.pop(0)
                break

        for line in lines:
            mo = INDEX_RE.search(line)
            if mo:
                yield mo.groups()[0]
            else:
                break

    def init(self, date):
        """
        @type date: datetime.date, datetime.datetime
        @param date: date to scrape for.
        """
        def _search(lines, code):
            for line in lines:
                if code in line:
                    return line

        index_dic = {
            'year' : date.year,
            'month' : date.month,
            'day' : date.day,
        }

        index = INDEX_URL % index_dic
        edition = "DDL_%s" % self.editie
        lines = list(self.getdoc(index, read=False).readlines())
        codes = self._get_codes(lines, edition)

        index = self.getdoc(INDEX_PAGE_URL % index_dic)
        referer_codes = index.cssselect('head > script')[5].text.split('\n')

        for code in codes:
            ref = _search(referer_codes, code).split(',')[3][3:-1]
            ref = urljoin(INDEX_PAGE_URL % index_dic, ref) + '.html'

            yield IndexDocument(url=ref, date=date)

    def get(self, ipage): # ipage --> index_page
        def _parsecoord(elem):
            top, left = elem.get('style').split(';')[1:3]
            top, left = int(top[4:-2]), int(top[5:-2])

            table = elem.cssselect('table')[0]
            width, height = map(int, (table.get('width'), table.get('height')))

            return (left, top, width, height)

        imgurl = urljoin(ipage.props.url, ipage.doc.cssselect('#pgImg')[0].get('src'))
        ipage.bytes = self.getdoc(imgurl, lxml=False)
        ipage.page = int(ipage.props.url.split('/')[-1].split('-')[2])
        ipage.props.category = int(ipage.props.url.split('/')[-1].split('-')[1])

        for div in ipage.doc.cssselect('body > div')[1:]:
            page = HTMLDocument(date=ipage.props.date)
            page.coords = [_parsecoord(el) for el in div.cssselect('div > div')]

            # Get url
            relref = div.cssselect('table')[0].get('onclick')[13:-9].strip("'")
            page.props.url = urljoin(ipage.props.url, relref)[:-5] + '_body.html'

            # Get article
            page.doc = self.getdoc(page.props.url, encoding='latin-1') # Bad x-cago.net! >:(
            yield self.get_article(page)

            # Add article to index page
            ipage.addchild(page)

        yield ipage

    def get_article(self, page):
        try:
            page.props.author = page.doc.cssselect('td.artauthor')[0].text.strip()[5:]
        except IndexError:
            pass

        page.props.headline = page.doc.cssselect('td.artheader')[0].text
        page.props.text = page.doc.cssselect('p')

        return page

if __name__ == '__main__':
    from amcat.tools.scraping.manager import main
    
    main(LimburgerScraper)
