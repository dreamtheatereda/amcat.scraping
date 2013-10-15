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

from urlparse import urljoin
from urllib import urlencode

from amcat.scraping.document import HTMLDocument
from amcat.scraping.scraper import HTTPScraper, DBScraper
from amcat.scraping.toolkit import parse_form
from amcat.tools.toolkit import readDate

class NRCArchiveScraper(HTTPScraper, DBScraper):
    medium_name = "NRC Handelsblad"
    index_url = "http://archief.nrc.nl/index.php/{self.options[date].year}/{month}/{self.options[date].day}/"
    login_url = "http://login.nrc.nl/login"

    def _login(self, username, password):
        self.open(self.index_url)

        login_form = self.getdoc(self.login_url).cssselect("#command")[0]
        form = parse_form(login_form)
        form['username'] = username
        form['password'] = password
        self.open(self.login_url, urlencode(form))

    months = ["januari","februari","maart","april","mei","juni","juli","augustus","september","oktober","november","december"]

    def _get_units(self):
        month = self.months[self.options['date'].month - 1].capitalize()
        index_doc = self.getdoc(self.index_url.format(**locals()))
        for li in index_doc.cssselect("div.main_content ul.list li"):
            try:
                a = li.cssselect("a")[0]
            except IndexError:
                raise Exception(li.text_content())
            page_doc = self.getdoc(urljoin(index_doc.url, a.get('href')))
            for li2 in page_doc.cssselect("div.main_content ul.list li"):
                if li2.cssselect("a"):
                    url = urljoin(page_doc.url, li2.cssselect("a")[0].get('href'))
                    yield url

    def _scrape_unit(self, url):
        article = HTMLDocument(url = url)
        article.prepare(self)

        article.props.text = article.doc.cssselect("#article p:not(#article-info):not(#metadata)")
        info = article.doc.cssselect("#article-info a")
        article.props.date = readDate(info[0].text)
        article.props.section = info[1].text
        article.props.page_str = info[2].text
        article.props.headline = article.doc.cssselect("#article h1")[0].text
        if article.doc.cssselect("#metadata"):
            metadata = article.doc.cssselect("#metadata")[0].text_content().split("|")
            for m in metadata:
                if m.strip().startswith("Trefwoord"):
                    article.props.tags = [t.strip() for t in m.strip().split(";")]
        yield article

if __name__ == '__main__':
    from amcat.scripts.tools import cli
    from amcat.tools import amcatlogging
    amcatlogging.info_module("amcat.scraping")
    cli.run_cli(NRCArchiveScraper)


