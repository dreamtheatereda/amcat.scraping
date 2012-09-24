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

from amcat.scraping.scraper import DBScraper, HTTPScraper
from amcat.scraping.document import HTMLDocument, IndexDocument


from urllib import urlencode
#from urlparse import urljoin
#from amcat.tools.toolkit import readDate

INDEX_URL = "http://digikrant.fd.nl/{y:04d}{m:02d}{d:02d}/public/pages/01001/FD-01-001-{y:04d}{m:02d}{d:02d}.html"
LOGIN_URL = "http://fd.nl/handle_login"
PAGE_URL = "http://digikrant.fd.nl/{y}{m}{d}/public/pages/01{pagenum:03d}/FD-01-{pagenum:03d}-{y}{m}{d}.html"

class FDScraper(HTTPScraper, DBScraper):
    medium_name = "Financieel Dagblad"

    def __init__(self, *args, **kwargs):
        super(FDScraper, self).__init__(*args, **kwargs)


    def _login(self, username, password):

        initial = self.opener.opener.open("http://digikrant.fd.nl")
        form = {
            'email' : username,
            'password' : password
            }
        pg = self.opener.opener.open(LOGIN_URL,urlencode(form))
        
        

    def _get_units(self):
        """get pages"""

            
        y = self.options['date'].year
        m = self.options['date'].month
        d = self.options['date'].day
        _url = INDEX_URL.format(**locals())
        index = self.getdoc("http://digikrant.fd.nl")
        from lxml import etree
        print(etree.tostring(index))


        
    def _scrape_unit(self, ipage):
        """gets articles from a page"""
        ipage.prepare(self)
        ipage.bytes = ""
        ipage.doc = self.getdoc(ipage.props.url)
        ipage.props.category = ""
        for a in ipage.doc.cssselect("body#framepage table td")[2].cssselect("tr")[7].cssselect("table"): #has inline style so no class/id
            onclick = a.get('onclick')
            link = onclick[onclick.find("http"):onclick.find(";")]
            pg = self.opener.opener.open(link)
            page = HTMLDocument(date = ipage.props.date,url=link)
            page.prepare(self)
            
            page.doc = self.getdoc(page.props.url)
            yield self.get_article(page)

            ipage.addchild(page)

        yield ipage

    def get_article(self, page):
        page.props.author = ""
        page.props.headline = ""
        page.props.text = ""
        return page




if __name__ == '__main__':
    from amcat.scripts.tools import cli
    from amcat.tools import amcatlogging
    amcatlogging.debug_module("amcat.scraping.scraper")
    amcatlogging.debug_module("amcat.scraping.document")
    cli.run_cli(FDScraper)


