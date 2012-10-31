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


#from urllib import urlencode
from urlparse import urljoin
from amcat.tools.toolkit import readDate
from datetime import date
from datetime import timedelta

FROM_DATE = date(year=2012,month=1,day=1)

INDEX_URL = "http://www.rijksoverheid.nl/nieuws/nieuwsoverzicht"
ARCHIVE_URL = "http://www.rijksoverheid.nl/nieuws/nieuwsoverzicht?keyword=&form-period-from={d:02d}-{m:02d}-{y:04d}&form-period-to={nd:02d}-{nm:02d}-{ny:04d}&form-department="

from amcat.scraping.scraper import HTTPScraper

class OverheidNieuwsScraper(HTTPScraper):
    medium_name = "rijksoverheid.nl/nieuws"

    def __init__(self, *args, **kwargs):
        super(OverheidNieuwsScraper, self).__init__(*args, **kwargs)
        self.open(INDEX_URL)

    def _get_units(self):

        #scraping from today, backwards in time until hardcoded date
        _date = date.today() + timedelta(days=1)
        _date = date(year=2012,month=9,day=22)
        while _date > FROM_DATE:
            prevdate = _date - timedelta(days=1)
            urldict = {
                'nd' : _date.day,
                'nm' : _date.month,
                'ny' : _date.year,
                'd' : prevdate.day,
                'm' : prevdate.month,
                'y' : prevdate.year
                }
            url = ARCHIVE_URL.format(**urldict)
            doc = self.getdoc(url)
            
            print("\n"+url+"\n")
            for page in self.get_pages(doc,url):
                
                for _url in [urljoin(url,a.get('href')) for a in page.cssselect("div.search-results a")]:
                    yield _url
            _date = prevdate



    def get_pages(self,doc,url):

        try:
            lastpage = int(doc.cssselect("#content-column ul.paging li")[-2].text_content())
        except IndexError: #no pagination
            yield doc;return
        else:
            yield doc
        for x in range(lastpage):
            href = "{}&page={}".format(url,x)
            yield self.getdoc(href)
        


    def _scrape_unit(self, url):
        article = HTMLDocument(url=url)
        article.prepare(self)

        content = article.doc.cssselect("#content-column")[0]
        article.props.date = readDate(content.cssselect("p.article-meta")[0].text.split("|")[1])
        article.props.headline = content.cssselect("h1")[0].text
        
        for x in [
            content.cssselect("h1")[0],
            content.cssselect("p.article-meta")[0],
            content.cssselect("p.sharing")[0]
        ]:
            x.drop_tree()

        article.props.text = content.text_content()

        for block in article.doc.cssselect("#aside-column div.block"):
            title = block.cssselect("h2")[0].text
            if "Verantwoordelijk" in title and "ministerie" in title:
                article.props.author = "; ".join([a.text for a in block.cssselect("ul.list-common li a")])
                break

        yield article
        




if __name__ == '__main__':
    from amcat.scripts.tools import cli
    from amcat.tools import amcatlogging
    amcatlogging.debug_module("amcat.scraping.scraper")
    amcatlogging.debug_module("amcat.scraping.document")
    cli.run_cli(OverheidNieuwsScraper)


