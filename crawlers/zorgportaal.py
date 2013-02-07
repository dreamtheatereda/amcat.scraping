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

from amcat.scraping.document import Document, HTMLDocument
from amcat.scraping.scraper import Crawler, AuthCrawler
import re
from amcat.tools.toolkit import readDate

class ZorgportaalCrawler(Crawler):
    medium_name = "Zorgportaal.nl"
    allow_url_patterns = [
        re.compile("zorgportaal.nl")
        ]

    ignore_url_patterns = [
        re.compile("/home/log-in-pagina")
        ]

    article_pattern = re.compile("(/component/content/article/[0-9]+-nieuws/[a-zA-Z0-9\-]+)|(/zorgkrant/nieuwsl-lijst/[0-9]+\-[a-zA-Z\-]+)")

    initial_urls = [
        "http://site.zorgportaal.nl/index.php/nieuws/nieuws/toon-alle-nieuwsberichten"
        ]

    def __init__(self, *args, **kwargs):
        super(ZorgportaalCrawler, self).__init__(*args, **kwargs)
        
    def _scrape_unit(self, url): 
        page = HTMLDocument(url=url)
        page.prepare(self)
        yield self.get_article(page)

    def get_article(self, page):
        nieuws_box = page.doc.cssselect("div.nieuws_box")[0]
        for p in nieuws_box.cssselect("p"):

            title = p.cssselect("b")[0].text
            content = p.text_content().split(":")[1].strip()

            if "Plaatsingsdatum" in title:
                page.props.date = readDate(content)
            elif "Auteur" in title:
                page.props.author = content
            elif "Bron" in title:
                page.props.source = content

        page.props.headline = page.doc.cssselect("div.content h2")[0].text
        page.props.text = page.doc.cssselect("div.nieuws_tekst")[0]

        if len(page.props.author)>50:
            page.props.author = "javascript protected"
        return page

    def get_comments(self,page):
        pass #no comments


if __name__ == '__main__':
    from amcat.scripts.tools import cli
    from amcat.tools import amcatlogging
    amcatlogging.debug_module("amcat.scraping.scraper")
    amcatlogging.debug_module("amcat.scraping.document")
    cli.run_cli(ZorgportaalCrawler)


