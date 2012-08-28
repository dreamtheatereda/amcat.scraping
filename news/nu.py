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


from amcat.scraping.scraper import HTTPScraper, DatedScraper
from amcat.scraping.document import HTMLDocument, IndexDocument
import urllib2
from urlparse import urljoin

INDEX_URL = "http://www.nu.nl/"
MONTHS = [
    'januari',
    'februari',
    'maart',
    'april',
    'mei',
    'juni',
    'juli',
    'augustus',
    'september',
    'oktober',
    'novembter',
    'december'
]

class NuScraper(HTTPScraper, DatedScraper):
    medium_name = "Nu.nl"

    def __init__(self, *args, **kwargs):
        super(NuScraper, self).__init__(*args, **kwargs) 


    def _get_units(self):
        """papers are often organised in blocks (pages) of articles, this method gets the blocks, articles are to be gotten later"""
        index = self.getdoc(INDEX_URL) 
        menu_options = index.cssselect('ul.listleft li')[1:]
        index_units = []
        for unit in menu_options:
            index_units.append(unit)
                
        page_int = 0
        for index_unit in index_units:
            href = index_unit.cssselect('a')[0].get('href')
            category = href.strip("/")
            page_int = page_int + 1
            yield IndexDocument(url=urljoin(INDEX_URL,href), date=self.options['date'],category = category,page = page_int)


    def _scrape_unit(self, ipage):
        """gets articles from an index page"""
        ipage.prepare(self)
        #ipage.bytes = "?" what is this?
        ipage.doc = self.getdoc(ipage.props.url)

        
        #nu.nl articles are not ordered by date anywhere. To be as accurate as possible, all recent articles will be opened, checked for a correct date and then listed 
        #this only works correctly if the scraped day is less than ~10 hours ago, more if there are not so many articles

        article_links = []
        try:
            for a in ipage.doc.cssselect(".leadarticle h2 a"):
                article_links.append(urljoin(INDEX_URL,a.get('href')))
        except IndexError:
            pass
        for a in ipage.doc.cssselect(".subarticle h2 a"):
            article_links.append(urljoin(INDEX_URL,a.get('href')))
        for a in ipage.doc.cssselect(".list ul li a"):
            article_links.append(urljoin(INDEX_URL,a.get('href')))

        try:
            if "nuzakelijk" in article_links[0]:
                article_links.pop(0)
        except IndexError:
            pass
        for url in article_links:
            try:
                doc = self.getdoc(url)
            except urllib2.HTTPError:
                break
            date_str = "{day} {month} {year}".format(day = self.options['date'].day,month = MONTHS[self.options['date'].month-1],year = self.options['date'].year)
            try:
                bla = doc.cssselect(".header .dateplace-data")[0].text 
            except IndexError:
                pass
            else:
                if date_str in doc.cssselect(".header .dateplace-data")[0].text:
                    page = HTMLDocument(date = self.options['date'],url=url)
                    page.prepare(self)
                    page.doc = doc
                    yield self.get_article(page)
                    ipage.addchild(page)
                
                        
        yield ipage
 
    def get_article(self, page):
        page.props.author = page.doc.cssselect("#leadarticle span.smallprint")[0].text.split("Door:")[1].strip()
        page.props.headline = page.doc.cssselect("#leadarticle .header h1")[0].text
        try:
            page.doc.cssselect("#leadarticle center")[0].drop_tree()
            page.doc.cssselect("#leadarticle .footer")[0].drop_tree()
        except IndexError:
            pass
        page.props.text = page.doc.cssselect("#leadarticle .content")[0].text_content()
        
        
        page.coords = ""
        return page




if __name__ == '__main__':
    from amcat.scripts.tools import cli
    from amcat.tools import amcatlogging
    amcatlogging.debug_module("amcat.scraping.scraper")
    amcatlogging.debug_module("amcat.scraping.document")
    cli.run_cli(NuScraper)
    
