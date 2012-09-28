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


from urlparse import urljoin


INDEX_URL = "http://www.nrc.nl/nieuws/overzicht/{y:04d}/{m:02d}/{d:02d}/"

from amcat.scraping.scraper import HTTPScraper,DatedScraper

class WebNieuwsNRCScraper(HTTPScraper, DatedScraper):
    medium_name = "NRC website - nieuws"

    def __init__(self, *args, **kwargs):
        super(WebNieuwsNRCScraper, self).__init__(*args, **kwargs) 


    def _get_units(self):

        
        y = self.options['date'].year
        m = self.options['date'].month
        d = self.options['date'].day
        

        url = INDEX_URL.format(**locals())
        index = self.getdoc(url)
        index.cssselect("div.watskeburt section")[1].drop_tree()
        for unit in index.cssselect('div.watskeburt article'): #long live the semantic web!
            try:
                href = unit.cssselect('h2 a')[0].get('href').lstrip("./")
            except IndexError:
                href = unit.cssselect('dd a')[0].get('href').lstrip("./")
            url = urljoin("http://www.nrc.nl/",href)
            yield HTMLDocument(url=url, date=self.options['date'])


        
    def _scrape_unit(self, page): 
        page.prepare(self)
        page.doc = self.getdoc(page.props.url)

        page.props.author = page.doc.cssselect("div.author a")[0].text
        page.props.headline = page.doc.cssselect("div.article h1")[0].text
        page.props.text = page.doc.cssselect("#broodtekst")[0].text_content()
        yield page




if __name__ == '__main__':
    from amcat.scripts.tools import cli
    from amcat.tools import amcatlogging
    amcatlogging.debug_module("amcat.scraping.scraper")
    amcatlogging.debug_module("amcat.scraping.document")
    cli.run_cli(WebNieuwsNRCScraper)


