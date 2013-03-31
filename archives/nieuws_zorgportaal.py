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

try:
    from amcatscraping.google.search import GoogleSearch
except ImportError:
    from scraping.google.search import GoogleSearch

from amcat.scraping.scraper import HTTPScraper


from amcat.tools.toolkit import readDate

import re

class Zorgportaal_nlNieuwsScraper(HTTPScraper):
    medium_name = "Zorgportaal.nl nieuws"

    def __init__(self, *args, **kwargs):
        super(Zorgportaal_nlNieuwsScraper, self).__init__(*args, **kwargs)      
        
        
    def _get_units(self):
        pattern = "http://site.zorgportaal.nl/index.php/component/content/article/\d+-nieuws/nieuws"
        otherpattern = "http://site.zorgportaal.nl/index.php/zorgkrant/nieuwsl-lijst/\d+"
        self.open("https://www.google.com")
        gs = GoogleSearch("site:http:site.zorgportaal.nl nieuws")
        gs.results_per_page = 100
        total = 0
        while True:
            results = gs.get_results()
            total += len(results)
            if not results:
                break
            else:
                for res in results:
                    if re.match(pattern,res.url) or re.match(otherpattern,res.url):
                        yield HTMLDocument(url=res.url)
                    
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
        page.props.text = page.doc.cssselect("div.nieuws_tekst")[0]
        info = page.doc.cssselect("div.nieuws_box p")
        for p in info:
            if "Plaatsingsdatum" in p.cssselect("b")[0].text:
                page.props.date = readDate(p.text_content().split(":")[1])
                break

            
        for comment in self.scrape_comments(page):
            comment.is_comment = True
            yield comment

        yield page

    def scrape_comments(self,page):
        for li in page.doc.cssselect("ul.uiList li.fbFeedbackPost"):
            comment = HTMLDocument(parent=page,url=page.url)
            comment.props.text = li.cssselect("div.postText")[0].text
            comment.props.author = li.cssselect("a.profileName")[0].text
            comment.props.date = readDate(li.cssselect("abbr.timestamp")[0].get('title'))
            yield comment


if __name__ == '__main__':
    from amcat.scripts.tools import cli
    from amcat.tools import amcatlogging
    amcatlogging.debug_module("amcat.scraping.scraper")
    amcatlogging.debug_module("amcat.scraping.document")
    cli.run_cli(Zorgportaal_nlNieuwsScraper)


