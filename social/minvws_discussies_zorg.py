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

from amcat.scraping.scraper import HTTPScraper,DatedScraper
from amcat.scraping.document import Document

from urlparse import urljoin
from amcat.tools.toolkit import readDate

INDEX_URL = "http://minvws.thevalleyfacebookcampagnes.nl/discussies/archief"

class ZorgScraper(HTTPScraper,DatedScraper):
    medium_name = "Discussies over zorg (ministerie VWS) (Facebook)"

    def __init__(self, *args, **kwargs):
        super(ZorgScraper, self).__init__(*args, **kwargs)



    def _get_units(self):
        """get pages"""
        ipage = self.getdoc(INDEX_URL)
        for a in ipage.cssselect("ul#archive a"):
            url = urljoin("http://minvws.thevalleyfacebookcampagnes.nl/",
                          a.get('href'))
            yield url

        
    def _scrape_unit(self, url):
        doc = self.getdoc(url)

        for li in doc.cssselect("ul#posts li"):
            page = HTMLDocument(date = ipage.props.date,url=ipage.props.url)
            page.prepare(self)

            for li2 in li.cssselect("ul li"):
                page2 = HTMLDocument(date = self.options['date'], url = url)
                page2.prepare(self)
                
                yield self.getarticle(page2, li2, reply=page)

            yield self.getarticle(page,li)  

    def getarticle(self, page, htmlelement, reply = False):
        page.props.author = htmlelement.cssselect(".user .details .name")[0]
        page.props.author_info = htmlelement.cssselect(".user .details span")[0].text_content()
        page.coords = ""
        page.props.text = htmlelement.cssselect(".post")[0]
        page.props.date = readDate(htmlelement.cssselect(".date")[0].text.split("om")[0]+str(self.options['date'].year))
        if reply:
            page.parent = reply
        return page
            
        

if __name__ == '__main__':
    from amcat.scripts.tools import cli
    from amcat.tools import amcatlogging
    amcatlogging.debug_module("amcat.scraping.scraper")
    amcatlogging.debug_module("amcat.scraping.document")
    cli.run_cli(ZorgScraper)
