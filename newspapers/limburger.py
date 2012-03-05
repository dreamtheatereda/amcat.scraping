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

from amcat.scraping.scraper import DBScraper, HTTPScraper, DatedScraper
from amcat.scraping.document import HTMLDocument, IndexDocument


import re

SESSION_URL = "http://mgl.x-cago.net/session.do"
LOGINURL = "http://mgl.x-cago.net/login.do?pub=ddl&auto=false"

INDEX_URL = "http://krantdigitaal.ddl.x-cago.net/DDL/%(year)d%(month)02d%(day)02d/public/index_editions_js.html"
INDEX_PAGE_URL = "http://krantdigitaal.ddl.x-cago.net/DDL/%(year)d%(month)02d%(day)02d/public/index.html"

INDEX_RE = re.compile('"(DDL-.+)"')

from urllib import urlencode
from urlparse import urljoin

DEBUG = True

class LimburgerScraper(HTTPScraper, DBScraper):
    medium_name = "De Limburger"

    def __init__(self, *args, **kwargs):
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
        self.editie = 'MA'

        super(LimburgerScraper, self).__init__(*args, **kwargs)

    def _login(self, username, password):
        POST_DATA = {
            'email' : username,
            'password' : password,
            'pub' : 'ddl',
            'r' : 'krantdigitaal.ddl.x-cago.net'
        }

        login1 = self.opener.opener.open(LOGINURL, urlencode(POST_DATA))

        if "Sessie overschrijven" in login1.read():
            data = urlencode(dict(overwrite='on', pub='ddl'))
            return self.opener.opener.open(SESSION_URL, data)

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

    def _get_units(self):
        def _search(lines, code):
            for line in lines:
                if code in line:
                    return line

        index_dic = {
            'year' : self.options['date'].year,
            'month' : self.options['date'].month,
            'day' : self.options['date'].day,
        }

        index = INDEX_URL % index_dic
        edition = "DDL_%s" % self.editie
        lines = list(self.opener.opener.open(index).readlines())
        codes = self._get_codes(lines, edition)

        index = self.getdoc(INDEX_PAGE_URL % index_dic)
        referer_codes = index.cssselect('head > script')[5].text.split('\n')

        for code in codes:
            ref = _search(referer_codes, code).split(',')[3][3:-1]
            ref = urljoin(INDEX_PAGE_URL % index_dic, ref) + '.html'

            yield IndexDocument(url=ref, date=self.options['date'])

    def _scrape_unit(self, ipage): # ipage --> index_page
        ipage.prepare(self)

        def _parsecoord(elem):
            top, left = elem.get('style').split(';')[1:3]
            top, left = int(top[4:-2]), int(top[5:-2])

            table = elem.cssselect('table')[0]
            width, height = map(int, (table.get('width'), table.get('height')))

            return (left, top, width, height)

        imgurl = urljoin(ipage.props.url, ipage.doc.cssselect('#pgImg')[0].get('src'))
        ipage.bytes = self.opener.opener.open(imgurl).read()
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
            if len(page.props.author) >= 100: del page.props.author
        except IndexError:
            pass

        page.props.headline = page.doc.cssselect('td.artheader')[0].text
        page.props.text = page.doc.cssselect('p')

        return page

if __name__ == '__main__':
    from amcat.scripts.tools import cli
    from amcat.tools import amcatlogging
    amcatlogging.debug_module("amcat.scraping.scraper")
    amcatlogging.debug_module("amcat.scraping.document")
    cli.run_cli(LimburgerScraper)
