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

from amcat.scraping.document import HTMLDocument
from amcat.tools.toolkit import readDate


INDEX_URL = "http://www.nieuws.nl"

from amcat.scraping.scraper import HTTPScraper,DatedScraper

class Nieuws_nlScraper(HTTPScraper, DatedScraper):
    medium_name = "nieuws.nl"

    def __init__(self, *args, **kwargs):
        super(Nieuws_nlScraper, self).__init__(*args, **kwargs)


    def _get_units(self):

        url = INDEX_URL
        index = self.getdoc(url)
        for unit in index.cssselect('div.submenu a'):
            href = unit.get('href')
            for page in self.get_pages(self.getdoc(href)):
                i = 0
                for _article in page.cssselect("#mainlayout_rundown .mainlayout_datum"):
                    if readDate(_article.text_content()).date() == self.options['date']:
                        i += 1
                for article in page.cssselect("h2 a"):
                    if i > 0:
                        yield HTMLDocument(url=article.get('href'),headline=article.get('title'))
                    i-=1


                    
    def get_pages(self, doc):
        for page in doc.cssselect("#page_navigation_bar a")[:-1]:
            url = page.get('href')
            yield self.getdoc(url)


        
    def _scrape_unit(self, article): 
        
        article.prepare(self)
        article.doc = self.getdoc(article.props.url)
        article.props.section = article.doc.cssselect("div.page_title h1")[0].text
        article.props.date = self.options['date']
        article.props.text = "\n".join([p.text_content() for p in article.doc.cssselect("p")])
        yield article
        




if __name__ == '__main__':
    from amcat.scripts.tools import cli
    from amcat.tools import amcatlogging
    amcatlogging.debug_module("amcat.scraping.scraper")
    amcatlogging.debug_module("amcat.scraping.document")
    cli.run_cli(Nieuws_nlScraper)


