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

import re
from datetime import date, datetime, time
from time import strptime
from urlparse import urljoin
from lxml import html

from amcat.scraping.document import HTMLDocument
from amcat.scraping.scraper import HTTPScraper, DatedScraper
from amcat.tools.toolkit import readDate


class TTScraper(HTTPScraper, DatedScraper):
    medium_name = "tt.com"
    index_url="http://tt.com/newsticker/?back={back}"

    def _get_units(self):
        back = (date.today() - self.options['date']).days
        index_text = self.open(self.index_url.format(**locals())).read().decode('utf-8')
        #A character in the header makes the html library fail to parse the page correctly (it silently returns half the page without warning -.-)
        #The character is located in the class attribute of each article tag that is to be scraped, so we take the article tag's inner wrapper and parse that instead.
        article = 0
        arts = []
        for part in index_text.split("<article"):
            article = part.split("</article>")[0]
            arts.append(article)

        for art in set(arts):
            item = html.fromstring(art)
            try:
                _time = time(*map(int,item.cssselect("div.time")[0].text.split(":")))
            except IndexError:
                continue
            article = HTMLDocument(
                date = datetime.combine(self.options['date'], _time),
                headline = item.cssselect("h2.title")[0].text,
                url = urljoin(self.index_url.format(**locals()), 
                              item.cssselect("h2.title")[0].getparent().get('href')),
                )
            yield article

    def _scrape_unit(self, article):
        article.doc = self.getdoc(article.props.url)
        page = self.open(article.props.url).read().decode('utf-8')
        article.props.section = " > ".join([a.text_content().strip() for a in article.doc.cssselect("#breadcrumb a")[1:-1]])
        article.props.externalid = int("".join(article.props.url.split("/")[-2].split("-")))
        text = page.split("<div class=\"BA_Grundtext\"")[1].split("</div>")[0]
        article.props.text = html.fromstring(text)
        yield article
        
if __name__ == '__main__':
    from amcat.scripts.tools import cli
    from amcat.tools import amcatlogging
    amcatlogging.info_module("amcat.scraping")
    cli.run_cli(TTScraper)


