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
from amcat.scraping import toolkit as stoolkit
import time
from urllib import urlencode
from lxml import html
from urlparse import urljoin


class LimburgerScraper(HTTPScraper, DBScraper):
    medium_name = "De Limburger"
    login_url = "http://mgl.x-cago.net/login.do?pub=ddl&auto=false"
    index_url = "http://digitaal.ddl.x-cago.net/DDL/{y:04d}{m:02d}{d:02d}/public/index.html"
    page_url = "http://digitaal.ddl.x-cago.net/DDL/{y:04d}{m:02d}{d:02d}/public{pagelink}.html"

    def _login(self, username, password):
        """log in on the web page
        @param username: username to log in with
        @param password: password 
        """

        page = self.getdoc(self.login_url)
        form = stoolkit.parse_form(page)
        form['email'] = username
        form['password'] = password
        page = self.getdoc(self.login_url, urlencode(form))
        if "<b>Sessie overschrijven</b>" in html.tostring(page):
            form = stoolkit.parse_form(page)
            form['overwrite'] = 'on'
            self.open("http://mgl.x-cago.net/session.do", urlencode(form))

    def _get_units(self):

        y = self.options['date'].year
        m = self.options['date'].month
        d = self.options['date'].day

        index_url = self.index_url.format(**locals())
        index = self.open(index_url)
        pages = []
        for line in index.readlines():
            if "pageTable.add" in line:
                start = line.find("new Array");end = line.find(");", start)
                args = line[start:end].split(",")
                pagelink = args[2].strip("\" ")
                self.section = args[6].strip('" )')
                yield self.page_url.format(**locals())
                
        
    def _scrape_unit(self, url):
        page = self.getdoc(url)
        correcttable = False
        for table in page.cssselect("table"):
            if correcttable:
                for td in table.cssselect("td.artitem"):
                    link = td.get('onclick').split(",")[0].lstrip("showDetails('").rstrip("'")
                    arturl = urljoin(url, link)
                    yield self.get_article(arturl)
                correcttable = False
                                                               
            if "Artikelen op deze pagina" in table.text_content():
                correcttable = True

    def get_article(self, url):
        url = "{}_body.html".format(url[:-5])
        pagenum = url.split("/")[7][0:5]
        article = HTMLDocument(url = url, pagenr = int(pagenum))
        article.doc = self.getdoc(url)
        article.props.headline = article.doc.cssselect("td.artheader")[0].text_content().strip()
        article.props.text = article.doc.cssselect("table.body")[0]
        if article.doc.cssselect("td.artauthor"):
            article.props.author = article.doc.cssselect("td.artauthor")[0].text_content().lstrip("dor")
        else:
            article.props.author = "-"
        article.props.date = self.options['date']
        article.props.section = self.section
        return article
        


if __name__ == '__main__':
    from amcat.scripts.tools import cli
    from amcat.tools import amcatlogging
    amcatlogging.debug_module("amcat.scraping.scraper")
    amcatlogging.debug_module("amcat.scraping.document")
    cli.run_cli(LimburgerScraper)


