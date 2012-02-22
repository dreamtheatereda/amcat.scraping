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

INDEX_URL = "http://telegraaf-i.telegraaf.nl/telegraaf/_main_/%(year)d/%(month)02d/%(day)02d/001"
LOGIN_URL = "http://telegraaf-i.telegraaf.nl/tmg/login.php"

try:
    from urllib import urlencode
    from urlparse import urljoin
except ImportError:
    from urllib.parse import urlencode, urljoin


class TelegraafScraper(PCMScraper):
    def __init__(self, exporter, max_threads=None):
        s = Scraper.objects.get(class_name=TelegraafScraper.__name__)

        self.login_url = LOGIN_URL
        self.login_data = {"sso:field:username" : s.email,
                           "sso:field:password" : s.password}

        super(TelegraafScraper, self).__init__(exporter, max_threads)

    def init(self, date):
        """
        @type date: datetime.date, datetime.datetime
        @param date: date to scrape for.
        """
        index = INDEX_URL % dict(year=date.year, month=date.month, day=date.day)

        doc = self.getdoc(index)
        for td in doc.cssselect('td.select_page option'):
            url = urljoin(index, td.get('value'))
            page = int(td.get('value'))

            yield IndexDocument(url=url, page=page, date=date)
        

    def get(self, ipage):
        from lxml.html import tostring
        print(tostring(ipage.doc))

        ipage.props.section = ipage.doc.cssselect('#rubrieken td[class=selected]')[0].text

        print(ipage.props.section)

        return []

    def get_article(self, page):
        pass

if __name__ == '__main__':
    from amcat.tools.scraping.manager import main
    
    main(TelegraafScraper)
