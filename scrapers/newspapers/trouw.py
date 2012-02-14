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

from amcat.tools.scraping.processors import PCMScraper
from amcat.tools.scraping.objects import HTMLDocument, IndexDocument
from amcat.tools.scraping import toolkit as stoolkit

from amcat.models.scraper import Scraper

INDEX_URL = "http://www.trouw.nl/digitalekrant/TR/%(year)d%(month)02d%(day)02d___/TRN01_001/"
LOGIN_URL = "https://caps.trouw.nl/service/login"

try:
    from urllib import urlencode
    from urlparse import urljoin
except ImportError:
    from urllib.parse import urlencode, urljoin


class TrouwScraper(PCMScraper):
    def __init__(self, exporter, max_threads=3):
        self.login_url = LOGIN_URL
        self.login_data = Scraper.objects.get(class_name=TrouwScraper.__name__).get_data()

        super(TrouwScraper, self).__init__(exporter, max_threads)

    def init(self, date):
        """
        @type date: datetime.date, datetime.datetime
        @param date: date to scrape for.
        """
        index = INDEX_URL % dict(year=date.year, month=date.month, day=date.day)

        doc = self.getdoc(index)
        for opt in doc.cssselect('#toolbar optgroup > option'):
            url = urljoin(index, '../%s' % opt.get('value')) + '/'
            
            if 'TRN01' in url:
                # We're not interested in the newspaper-attachments (sports, etc.)
                yield IndexDocument(url=url, date=date)

    def get(self, ipage):
        ipage.bytes = self.getdoc(urljoin(ipage.props.url, './page.jpg'), lxml=False)
        ipage.page = ipage.props.url.split('_')[-1].strip('/')
        ipage.doc = self.getdoc(ipage.props.url)

        for art in ipage.doc.cssselect('div.page #articles > area'):
            artname = art.get('class').split('_')[-1]

            page = HTMLDocument(date=ipage.props.date)
            page.coords = stoolkit.parse_coords(ipage.doc.cssselect('div.%s' % artname))
            page.props.url = urljoin(ipage.props.url, artname + '.html')

            page.prepare(self)
            yield self.get_article(page)

            ipage.addchild(page)

        yield ipage

    def get_article(self, page):
        page.props.headline = page.doc.cssselect('h1')[0].text
        page.props.text = page.doc.cssselect('div.body p')

        return page

if __name__ == '__main__':
    from amcat.tools.scraping.manager import main
    
    main(TrouwScraper)
