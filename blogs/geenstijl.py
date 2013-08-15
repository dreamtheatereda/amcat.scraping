
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
from amcat.scraping.document import HTMLDocument, Document
from amcat.tools.toolkit import readDate
import datetime


INDEX_URL = "http://www.geenstijl.nl/mt/archieven/maandelijks/{y}/{m}/"

class GeenstijlScraper(HTTPScraper, DatedScraper):
    medium_name = "geenstijl"

    def _get_units(self):
        month = self.options['date'].month
        if len(str(month)) == 1:
            month = '0'+str(month)
        year = self.options['date'].year
        yield INDEX_URL.format(y=year,m=month)
        
    
    def _scrape_unit(self, url):
        doc = self.getdoc(url)
        units = doc.cssselect('div.content ul li')
        correct_date = self.options['date'].strftime("%d-%m-%y").strip()
        for article_unit in units:
            try:
                _date = article_unit.text.strip()
            except AttributeError:
                continue
            if _date == correct_date:
                
                href = article_unit.cssselect("a")[0].get('href')
                page = HTMLDocument(url=href, date=self.options['date'])
                
                page.prepare(self)
                page = self.get_article(page)
                for comment in self.get_comments(page):
                    comment.is_comment = True
                    comment.parent = page
                    yield comment
                yield page
                

    def get_article(self, page):
        page.props.author = page.doc.cssselect("article footer")[0].text_content().split("|")[0].strip()
        page.props.headline = page.doc.cssselect("article h1")[0].text.strip()
        if page.props.headline[0] == '#': page.props.headline = page.props.headline[1:].strip()
        datestring = page.doc.cssselect("footer time")[0].text_content()
        page.props.date = datetime.datetime.strptime(datestring, '%d-%m-%y | %H:%M')
        page.doc.cssselect("footer")[0].drop_tree()
        page.props.text = page.doc.cssselect("article")[0]
        page.coords = ""
        return page

    def get_comments(self,page):
        for article in page.doc.cssselect("#comments article"):
            comment = HTMLDocument(parent = page)
            footer = article.cssselect("footer")[0].text_content().split(" | ")
            comment.props.date = readDate(footer[1])
            comment.props.author = footer[0]
            comment.props.text = article.cssselect("p")
            yield comment

if __name__ == '__main__':
    from amcat.scripts.tools import cli
    from amcat.tools import amcatlogging
    amcatlogging.info_module("amcat.scraping")
    cli.run_cli(GeenstijlScraper)
