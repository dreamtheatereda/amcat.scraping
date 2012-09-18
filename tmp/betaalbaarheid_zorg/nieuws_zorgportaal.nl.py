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

from amcat.scraping.document import Document, HTMLDocument, IndexDocument

from amcat.tools.toolkit import readDate


URLS = ["http://site.zorgportaal.nl/index.php/nieuws/nieuws/service/nieuws-via-rss/zorgportaal-nl","http://site.zorgportaal.nl/index.php/nieuws/nieuws/service/nieuws-via-rss/rss-feed-product-en-organisatie-nieuws"]

from amcat.scraping.scraper import HTTPScraper,DatedScraper

class Zorgportaal_nlNieuwsScraper(HTTPScraper, DatedScraper):
    medium_name = "Zorgportaal.nl nieuws"

    def __init__(self, *args, **kwargs):
        super(Zorgportaal_nlNieuwsScraper, self).__init__(*args, **kwargs)      


    def _get_units(self):
        
        for url in URLS:
            doc = self.getdoc(url)
            entries = doc.cssselect('item')
            for entry in entries:
                _date = entry.cssselect("pubdate")[0].text
                date = readDate(_date)
                if str(self.options['date']) in str(date):
                    href = entry.cssselect("link")[0].tail
                    yield HTMLDocument(url=href, date=date)

        
    def _scrape_unit(self, page): 

        page.prepare(self)
        page.doc = self.getdoc(page.props.url)
        author = page.doc.cssselect("div.nieuws_box p")[2]
        for script in author.cssselect("script"):
            script.drop_tree()
        try:
            page.props.author = author.cssselect("a")[0].text
        except IndexError:
            page.props.author = author.text_content().split(":")[1].strip()
        if len(page.props.author) >=99:
            page.props.author="author protected"
        
        page.props.headline = page.doc.cssselect("#container_content div.content h2")[0].text
        page.props.text = page.doc.cssselect("div.nieuws_tekst")[0].text_content()

        yield page




if __name__ == '__main__':
    from amcat.scripts.tools import cli
    from amcat.tools import amcatlogging
    amcatlogging.debug_module("amcat.scraping.scraper")
    amcatlogging.debug_module("amcat.scraping.document")
    cli.run_cli(Zorgportaal_nlNieuwsScraper)


