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
from amcat.scraping.document import HTMLDocument


from urllib import urlencode
#from urlparse import urljoin
#from amcat.tools.toolkit import readDate

INDEX_URL = "http://digikrant-archief.fd.nl/vw/page.do?id=FD-01-001-{y:04d}{m:02d}{d:02d}&pagedisplay=true&ed=00&date={y:04d}{m:02d}{d:02d}"

LOGIN_URL = "http://fd.nl/handle_login"
PAGE_URL = "http://digikrant-archief.fd.nl/vw/page.do?id={page_id}&pagedisplay=true&ed=00&date={y:04d}{m:02d}{d:02d}"
ARTICLE_URL = "http://digikrant-archief.fd.nl/vw/txt.do?id={art_id}"


class FDScraper(HTTPScraper, DBScraper):
    medium_name = "Financieel Dagblad"

    def __init__(self, *args, **kwargs):
        super(FDScraper, self).__init__(*args, **kwargs)


    def _login(self, username, password):

        data = {
            'y':self.options['date'].year,
            'm':self.options['date'].month,
            'd':self.options['date'].day
            }

        initial = self.opener.opener.open("http://digikrant.fd.nl")
        form = {
            'email' : username,
            'password' : password
            }
        pg = self.opener.opener.open(LOGIN_URL,urlencode(form))


        

        # only god knows why opening this particular url twice works, but its the only thing that works..
        url = "http://digikrant.fd.nl/go?url=digikrant-archief.fd.nl/vw/edition.do?forward=true%26dp=FD%26altd=true%26date={y:04d}{m:02d}{d:02d}%26uid=2570808%26oid=%26abo=DIGITAAL2011%26ed=00".format(**data)
        self.open(url)
        self.open(url)
            

    def _get_units(self):
        """get pages"""
            
        y = self.options['date'].year
        m = self.options['date'].month
        d = self.options['date'].day
        _url = INDEX_URL.format(**locals())
        index = self.getdoc(_url)
        for option in index.cssselect("#selectPage option"):
            page_id = option.get('value')
            page_category = option.text.split("-")[1].strip()
            page_num = option.text.split("-")[0].strip().lstrip('p')
            yield {'id':page_id,'category':page_category,'page':page_num}

        
    def _scrape_unit(self, p):
        """gets articles from a page"""

        p_url = PAGE_URL.format(page_id=p['id'],y=self.options['date'].year,m=self.options['date'].month,d=self.options['date'].day)
        doc = self.getdoc(p_url)
        for a in doc.cssselect("td.arthref2 a"):
            

            art_id = a.get('href').split("('")[1].rstrip("');")
            art_url = ARTICLE_URL.format(art_id=art_id)
            page = HTMLDocument(date = self.options['date'],url=art_url)
            page.prepare(self)
            page.doc = self.getdoc(page.props.url)
            if "Er is geen tekst weergave beschikbaar" in page.doc.cssselect("table.body")[0].text_content():
                continue

            yield self.get_article(page)
                

    def get_article(self, page):
        try:
            page.props.author = page.doc.cssselect("td.artauthor")[0].text_content().split(":")[1].strip()
        except IndexError:
            page.props.author = ""
        
        page.props.headline = page.doc.cssselect("td.artheader")[0].text_content()
        page.props.text = page.doc.cssselect("table.body")[0].text_content()
        page.coords = ""
        return page




if __name__ == '__main__':
    from amcat.scripts.tools import cli
    from amcat.tools import amcatlogging
    amcatlogging.debug_module("amcat.scraping.scraper")
    amcatlogging.debug_module("amcat.scraping.document")
    cli.run_cli(FDScraper)


