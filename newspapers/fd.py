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
from amcat.tools import toolkit
from amcat.scraping import toolkit

INDEX_URL = "http://digikrant.fd.nl/{y:04d}{m:02d}{d:02d}/public/pages/01001/FD-01-001-{y:04d}{m:02d}{d:02d}.html"
LOGIN_URL = "http://fd.nl/?service=unRegisteredLogin&target=http://fd.nl/digikrant"
PAGE_URL = "http://digikrant.fd.nl/{y}{m}{d}/public/pages/01{pagenum:03d}/FD-01-{pagenum:03d}-{y}{m}{d}.html"

class FDScraper(HTTPScraper, DBScraper):
    medium_name = "Financieel Dagblad"

    def __init__(self, *args, **kwargs):
        super(FDScraper, self).__init__(*args, **kwargs)


    def _login(self, username, password):
        page = self.getdoc(LOGIN_URL)
        form = toolkit.parse_form(page)
        form['remember_me']=True
        form['email']=username
        form['password']=password
        pg = self.opener.opener.open(LOGIN_URL+"#submitLogin_1",urlencode(form))
        self.cookies = pg.info()['set-cookie']


#NOTE: this scraper is under construction, for the login doesn't work yet. FD.nl has many cookies and redirects, perhaps saving cookies in the getdoc function is a step forward.
#Do this by adding 
#    self.opener.addheaders.append(('Cookie',response.info()['set-cookie']))
#at the getdoc function in amcat/scraping/htmltools.py just before the try-except statement.
# anything below these lines is not tested yet.


    def _get_units(self):
        """get pages"""
        index_dict = {
            'year' : self.options['date'].year,
            'month' : self.options['date'].month,
            'day' : self.options['date'].day
        }




        i_url = INDEX_URL.format(y = index_dict['year'],
                                 m = index_dict['month'],
                                 d = index_dict['day'])
        self.opener.opener.addheaders.append(("Cookie",self.cookies))
        index = self.getdoc(i_url)
        from lxml import etree
        units = index.cssselect('select#selectPage option')
        i = 0
        for page_unit in units:
            i = i + 1 #pages are nicely ordered
            href = PAGE_URL.format(index_dict,pagenum=i)
            print(href)
            yield IndexDocument(url=href, date=self.options['date'],page=i,category = page_unit.text.split("-")[1].lstrip())

        
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


