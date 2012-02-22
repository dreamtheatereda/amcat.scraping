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

LOGIN_URL = "https://login.nrc.nl/login"
INDEX_URL = "http://digitaleeditie.nrc.nl/digitaleeditie/NH/%(year)d/%(month_minus)d/%(year)d%(month)02d%(day)02d___/1_01/"

try:
    from urllib import urlencode
    from urlparse import urljoin
except ImportError:
    from urllib.parse import urlencode, urljoin


class NRCHandelsbladScraper(PCMScraper):
    def __init__(self, exporter, max_threads=None):
        self.login_url = LOGIN_URL
        self.login_data = Scraper.objects.get(class_name=NRCHandelsbladScraper.__name__).get_data()

        super(NRCHandelsbladScraper, self).__init__(exporter, max_threads=max_threads)

    def init(self, date):
        """
        @type date: datetime.date, datetime.datetime
        @param date: date to scrape for.
        """
        index = INDEX_URL % {
            'year' : date.year,
            'month' : date.month,
            'day' : date.day,
            'month_minus' : date.month - 1
        }

        sections = self.getdoc(index).cssselect('#Sections a.thumbnail-link')
        for s in sections:
            break
            url = urljoin(index, s.get('href'))
            yield IndexDocument(url=url, date=date)

    def get(self, ipage): # ipage --> index_page
        ipage.doc = self.getdoc(ipage.props.url)
        ipage.bytes = self.getdoc(urljoin(ipage.props.url, 'page.jpg'), lxml=False)
        ipage.page = int(ipage.props.url.split('_')[-1].split('/')[0])

        for a in ipage.doc.cssselect('#Articles a'):
            page = HTMLDocument(date=ipage.props.date)
            page.coords = stoolkit.parse_coords(ipage.doc.cssselect('div.%s' % a.get('class')))
            page.props.url = urljoin(ipage.props.url, '%s_text.html' % a.get('class'))

            page.prepare(self)
            yield self.get_article(page)

            ipage.addchild(page)
        
        yield ipage

    def get_article(self, page):
        page.props.text = page.doc.cssselect('.column-left')[0]
        page.props.headline = page.doc.cssselect('h2')[0].text

        intro = page.doc.cssselect('p.intro')
        if intro:
            page.props.text.insert(0, intro[0])
           
        return page

if __name__ == '__main__':
    from amcat.tools.scraping.manager import main

    main(NRCHandelsbladScraper)
