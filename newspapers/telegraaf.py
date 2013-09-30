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

from amcat.scraping.scraper import HTTPScraper, DBScraper
from amcat.scraping.document import HTMLDocument

from amcat.scraping import toolkit
from amcat.scraping.toolkit import parse_coord


import logging; log = logging.getLogger("amcat.scraping.scraper")

INDEX_URL = "https://telegraaf-i.telegraaf.nl/telegraaf/_main_/%(year)d/%(month)02d/%(day)02d/001"
LOGIN_URL = "https://telegraaf-i.telegraaf.nl/telegraaf/_main_/{y}/{m:02d}/{d:02d}/001/page.html"
other_url = "https://telegraaf-i.telegraaf.nl/tmg/login.php"
from urllib import urlencode
from urlparse import urljoin

CREDENTIALS_ERR = "Login page returned code %s. Wrong credentials?"

class TelegraafScraper(HTTPScraper, DBScraper):
    medium_name = "De Telegraaf"
    pagenr = 0

    def _login(self, username, password):
        l_url = LOGIN_URL.format(
                y=self.options['date'].year,
                m=self.options['date'].month,
                d=self.options['date'].day)
        pagel = self.getdoc(l_url)
        form = toolkit.parse_form(pagel)
        form["sso:field:username"] = username
        form["sso:field:password"] = password
        pagel = self.open(other_url,urlencode(form))

        if pagel.getcode() != 200:
            raise ValueError(CREDENTIALS_ERR % pagel.getcode())


    def _get_units(self):
        """
        @type date: datetime.date, datetime.datetime
        @param date: date to scrape for.
        """
        date = self.options['date']
        index = INDEX_URL % dict(year=date.year, month=date.month, day=date.day)
        doc = self.getdoc(index)
        self.categories = self.get_categories(doc)
        for td in doc.cssselect('td.select_page option'):
            url = urljoin(index, td.get('value') + '/page.html')
            yield url

    def get_categories(self, doc):
        borders = {}
        for a in doc.cssselect("td.nav tr")[1].cssselect("a"):
            try:
                pagenr = int(a.get('href').split("/")[-1])
            except AttributeError:
                #some html fail
                continue
            cat = a.text_content()
            borders[pagenr] = cat

        categories = {}
        cat = borders[1]
        for td in doc.cssselect('td.select_page option'):
            pagenr = int(td.get('value'))
            if pagenr in borders.keys():
                cat = borders[pagenr]
                
            categories[pagenr] = cat

        return categories
            
        

    def _scrape_unit(self, url):
        doc = self.getdoc(url)
        # Articles with an id higher than 100 are advertisements,
        # which can be filtered by excluding classnames lager than
        # 9 (articleXXX).
        articles = doc.cssselect('#page div')
        articles = set(div.get('class') for div in articles
                            if len(div.get('class')) <= 9)

        for clsname in articles:
            page = HTMLDocument()

            # Delete images
            for img in doc.cssselect('#article img'):
                img.delete_tree()

            divs = doc.cssselect('div.%s' % clsname)
            page.props.url = urljoin(url,
                                     "article/%s.html" % clsname[7:])
            page.prepare(self)
            page.props.pagenr = int(url.split("/")[-2])
            page.props.section = self.categories[page.props.pagenr]
            page.props.text = page.doc.cssselect('#article .body p')
            if page.doc.cssselect("#article p.dateline"):
                page.props.dateline = page.doc.cssselect("#article p.dateline")[0].text_content()
            if page.doc.cssselect("#article .kicker"):
                page.props.kicker = page.doc.cssselect("#article .kicker")[0].text_content()
            if page.doc.cssselect("#article address"):
                page.props.author = page.doc.cssselect("#article address")[0].text_content().strip().lstrip("dor").strip()
            if page.doc.cssselect('#article h1'):
                page.props.headline = page.doc.cssselect('#article h1')[0].text_content()
                all_text = "".join([p.text_content() for p in page.props.text])
                if len(all_text) < 300:
                    continue
                yield page




if __name__ == '__main__':
    from amcat.scripts.tools import cli
    from amcat.tools import amcatlogging
    amcatlogging.debug_module("amcat.scraping.scraper")
    amcatlogging.debug_module("amcat.scraping.document")
    cli.run_cli(TelegraafScraper)
