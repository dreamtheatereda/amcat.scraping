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


from amcat.scraping.scraper import DatedScraper, HTTPScraper
from amcat.scraping.document import HTMLDocument, IndexDocument, Document
from amcat.tools.toolkit import readDate


INDEX_URL = "http://www.geenstijl.nl/mt/archieven/maandelijks/{y}/{m}/"

class GeenstijlScraper(HTTPScraper, DatedScraper):
    medium_name = "geenstijl.nl"

    def __init__(self, *args, **kwargs):
        super(GeenstijlScraper, self).__init__(*args, **kwargs)

    def _get_units(self):
        month = self.options['date'].month
        if len(str(month)) == 1:
            month = '0'+str(month)
        year = self.options['date'].year
        url = INDEX_URL.format(y=year,m=month)
        yield IndexDocument(url=url,date=self.options['date'])
    
    def _scrape_unit(self, ipage):
        ipage.prepare(self)
        ipage.doc = self.getdoc(ipage.props.url)
        ipage.page = " "
        units = ipage.doc.cssselect('div.content ul li')
        correct_date = self.options['date'].strftime("%d-%m-%y").strip()
        for article_unit in units:
            try:
                _date = article_unit.text.strip()
            except AttributeError:
                break
            if _date == correct_date:
                
                href = article_unit.cssselect("a")[0].get('href')
                page = HTMLDocument(url=href, date=self.options['date'])
                page.prepare(self)
                page.doc = self.getdoc(href)
                page = self.get_article(page)
                for comment in self.get_comments(page):
                    yield comment
                yield page
                ipage.addchild(page)

        yield ipage
        

    def get_article(self, page):
        page.props.author = page.doc.cssselect("article footer")[0].text_content().split("|")[0].strip()
        page.props.headline = page.doc.cssselect("article h1")[0].text
        page.doc.cssselect("footer")[0].drop_tree()
        page.props.text = page.doc.cssselect("article")[0].text_content()
        page.coords = ""
        return page

    def get_comments(self,page):
        for article in page.doc.cssselect("#comments article"):
            comment = Document(parent=page)
            footer = article.cssselect("footer")[0].text_content().split(" | ")
            comment.props.date = readDate(footer[1])
            comment.props.author = footer[0]
            try:
                comment.props.text = article.cssselect("p")[0].text_content()
            except IndexError: #empty comment
                continue
            yield comment

if __name__ == '__main__':
    from amcat.scripts.tools import cli
    from amcat.tools import amcatlogging
    amcatlogging.debug_module("amcat.scraping.scraper")
    amcatlogging.debug_module("amcat.scraping.document")
    cli.run_cli(GeenstijlScraper)
