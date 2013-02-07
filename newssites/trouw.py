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
#from urlparse import urljoin
from amcat.tools.toolkit import readDate
#from amcat.scraping.tools import toolkit

from amcat.scraping.htmltools import create_cc_cookies


from urllib2 import HTTPError
import re

INDEX_URL = "http://www.trouw.nl/tr/nl/15/archief/integration/nmc/frameset/archive/archiveDay.dhtml?archiveDay={y:04d}{m:02d}{d:02d}"


from amcat.scraping.scraper import HTTPScraper,DatedScraper

class TrouwWebScraper(HTTPScraper, DatedScraper):
    medium_name = "Trouw.nl"
    def _set_cookies(self):
        for cookie in create_cc_cookies(".trouw.nl"):
            self.opener.cookiejar.set_cookie(cookie)


    def _get_units(self):
        self._set_cookies()
        index_dict = {
            'y' : self.options['date'].year,
            'm' : self.options['date'].month,
            'd' : self.options['date'].day
        }
        url = INDEX_URL.format(**index_dict)
        index = self.getdoc(url) 
        
        for unit in index.cssselect('div.articleOverview dd'):
            print("unit")
            href = unit.cssselect('a')[0].get('href')
            unit.cssselect('span')[0].drop_tree()
            title = unit.cssselect('a')[0].text_content()
            yield HTMLDocument(url=href, headline = title)
        


    def _scrape_unit(self, page): 
        page.prepare(self)
        if page.doc.cssselect("form#_caps_form"):
            return
        header = page.doc.cssselect("div.time_post")[0].text_content()

        
        pattern = re.compile(r'(Bewerkt door:)?([a-zA-Z0-9 ]+)?(\u2212)?\n((\d{2,2}/){2,2}\d{2,2}), \d{2,2}:\d{2,2}\n(\xa0\u2212\xa0bron: ([A-Za-z0-9 ,]+))?')

        try:
            groups = pattern.search(header).groups()
        except AttributeError: #rare error where regex fails
            page.props.date = readDate(header)
        else:
            page.props.date = readDate(groups[3])
            if groups[0] or (not groups[1]):
                page.props.author = groups[-1]
            elif groups[1]:
                page.props.author = groups[1]

        if not hasattr(page.props,"author") and page.doc.cssselect("span.author"):
            page.props.author = page.doc.cssselect("span.author")[0].text_content()

        if hasattr(page.props,"author"):
            if page.props.author:
                page.props.author = page.props.author[:98]

        page.props.text = page.doc.cssselect("#art_box2 p")
        try:
            page.props.section = page.doc.cssselect("#subnav_nieuws li span.nieuws")[0].text_content()
        except IndexError:
            if page.doc.cssselect("div.dos_default h2"):
                page.props.section = "dossier: {}".format(page.doc.cssselect("div.dos_default h2")[0].text)

        yield page





if __name__ == '__main__':
    from amcat.scripts.tools import cli
    from amcat.tools import amcatlogging
    amcatlogging.debug_module("amcat.scraping.scraper")
    amcatlogging.debug_module("amcat.scraping.document")
    cli.run_cli(TrouwWebScraper)


