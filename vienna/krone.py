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

#NOTE: This scraper is only able to scrape the last 24 hours of the website, please make sure it runs at midnight rather than during the day

from urlparse import urljoin
from datetime import date, timedelta

from amcat.scraping.document import Document, HTMLDocument
from amcat.scraping.scraper import DatedScraper, HTTPScraper
from amcat.tools.toolkit import readDate

class KroneScraper(HTTPScraper, DatedScraper):
    medium_name = "krone.at"
    base_url = "http://krone.at"
    index_url = "http://www.krone.at/schlagzeilen-aktualitaet"

    def _get_units(self):
        self.open(self.base_url)
        
        for div in self.getdoc(self.index_url).cssselect("div.c_schlagzeilen_content_4xn div.c_item"):
            a = div.cssselect("h2.c_titel a")[0]
            url = urljoin(self.index_url, a.get('href'))
            article = HTMLDocument(url = url)
            article.props.headline = a.text_content().strip()
            article.props.kicker = div.cssselect("h3.l_vorleger")[0].text_content().strip()
            article.props.section = div.cssselect("span.c_label")[0].text.split("|")[1].strip()
            article.props.externalid = article.props.url.split("-")[-1]

            date_str = div.cssselect("span.c_time")[0].text_content()
            _date = date.today()
            if 'gestern' in date_str:
                _date -= timedelta(days = 1)
            _date = readDate(str(_date) + " " + date_str.strip().split()[-1])
            article.props.date = _date
            if _date.date() == self.options['date']:
                yield article

    def _scrape_unit(self, article):
        article.prepare(self)
        article.props.text = article.doc.cssselect("div.block_3 div.content_lead,div.objekt_content")
        text = "".join([t.text_content() for t in article.props.text])
        if len(text) < 10:
            raise ValueError("no text")
        article.props.author = article.doc.cssselect("div.c_author")[0].text_content().strip()
        tags = article.doc.cssselect("div.c_tags a.content_body font")
        article.props.tags = [tag.text_content().strip() for tag in tags]
        yield article

if __name__ == '__main__':
    from amcat.scripts.tools import cli
    from amcat.tools import amcatlogging
    amcatlogging.info_module("amcat.scraping")
    cli.run_cli(KroneScraper)


