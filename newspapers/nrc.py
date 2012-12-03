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

from amcat.scraping.scraper import HTTPScraper, DBScraper
from amcat.scraping.document import HTMLDocument
from amcat.scraping import toolkit as stoolkit

LOGIN_URL = "https://login.nrc.nl/login"
INDEX_URL = "http://digitaleeditie.nrc.nl/digitaleeditie/%(version)s/%(year)d/%(month_minus)d/%(year)d%(month)02d%(day)02d___/1_01/"

from urlparse import urljoin
from urllib import urlencode

class NRCScraper(HTTPScraper, DBScraper):
    medium_name = "NRC Handelsblad"
    nrc_version = "NH"

    def _login(self, username, password):

        page = self.getdoc(LOGIN_URL)

        form = stoolkit.parse_form(page)
        form['username'] = username
        form['password'] = password
        self.opener.opener.open(LOGIN_URL, urlencode(form))

    def _get_units(self):
        """
        @type date: datetime.date, datetime.datetime
        @param date: date to scrape for.
        """
        date = self.options.get('date')

        index = INDEX_URL % {
            'year' : date.year,
            'month' : date.month,
            'day' : date.day,
            'month_minus' : date.month - 1,
            'version' : self.nrc_version
        }
        sections = self.getdoc(index).cssselect('#Sections a.thumbnail-link')
        for s in sections:
            url = urljoin(index, s.get('href'))
            yield url

    def _scrape_unit(self, url):
        doc = self.getdoc(url)
        for a in doc.cssselect('#Articles a'):
            page = HTMLDocument(date=self.options.get('date'))
            page.coords = stoolkit.parse_coords(doc.cssselect('div.%s' % a.get('class')))
            page.props.url = urljoin(url, '%s_text.html' % a.get('class'))

            page.prepare(self)
            yield self.get_article(page)


    def get_article(self, page):
        page.props.text = page.doc.cssselect('.column-left')[0]
        page.props.headline = page.doc.cssselect('h2')[0].text
        intro = page.doc.cssselect('p.intro')
        if intro:
            page.props.text.insert(0, intro[0])

        return page


if __name__ == '__main__':
    from amcat.scripts.tools import cli
    from amcat.tools import amcatlogging
    amcatlogging.debug_module("amcat.scraping.scraper")
    amcatlogging.debug_module("amcat.scraping.document")
    cli.run_cli(NRCScraper)
