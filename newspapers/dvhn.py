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

from amcat.scraping.document import Document, HTMLDocument
from amcat.scraping import toolkit

from urllib import urlencode

from lxml import etree
from urlparse import urljoin
import re

INDEX_URL = "http://dvhn.x-cago.net/{y}{m:02d}{d:02d}/public/"
LOGIN_URL = "http://dvhn.x-cago.net/login.vm"
PAGE_URL = "http://dvhn.x-cago.net/{y:04d}{m:02d}{d:02d}/public/pages/DO01{p:03d}/DVHNDO-01-{p:03d}-{y:04d}{m:02d}{d:02d}.html"

from amcat.scraping.scraper import HTTPScraper,DBScraper

class DVHNScraper(HTTPScraper, DBScraper):
    medium_name = "Dagblad van het Noorden"

    def _login(self, username, password):
        
        page = self.getdoc(LOGIN_URL)
        form = toolkit.parse_form(page)
        form['email'] = username
        form['password'] = password
        res = self.getdoc(LOGIN_URL, urlencode(form))
        error = res.cssselect("td.error")
        if error:
            print("\n{error[0].text}\n".format(**locals()))


    def _get_units(self):
        index_dict = {
            'y' : self.options['date'].year,
            'm' : self.options['date'].month,
            'd' : self.options['date'].day
        }
        url = INDEX_URL.format(**index_dict)
        index = self.getdoc(url) 
        self.sections_pages(index)
        scripts = index.cssselect("script")
        pages = []
        for script in scripts:
            string = etree.tostring(script)
            if "document.write('&lt;option name=" in string:
                start = string.find("value=\"")+7;end = string.find("\"",start)
                pages.append(int(string[start:end]))
        for page in pages:
            url = PAGE_URL.format(p=page,**index_dict)
            yield (page,url)
        
    def sections_pages(self, doc):
        #map sections  to pages
        self.section_dict = {}
        for option in doc.cssselect("#pageSelect option"):
            if option.get('class') == "opttitle":
                cur_section = option.text
            else:
                self.section_dict[int(option.get('value'))] = cur_section
        
    def _scrape_unit(self, p_u):
        (pagenr, url) = p_u
        doc = self.getdoc(url)

        articles = set([])
        for table in doc.cssselect('table'):
            if table.get('onclick'):
                onclick = table.get('onclick')
                start = onclick.find("(");end = onclick.find(")",start)
                args = [a.strip(";)(")for a in onclick[start:end].split(",")]
                
                href = "/".join(args[0].split("/")[4:])
                url = urljoin("http://dvhn.x-cago.net",href)
                
                articles.add(HTMLDocument(url=url[:-6]+"_text.html", pagenr = pagenr))

        for article in articles:
            article.props.section = self.sections_dict[article.props.pagenr]
            no_text = "Er is geen tekst weergave beschikbaar voor dit artikel."
            article = self.get_article(article)
            if not no_text in article.props.text:
                yield article


    def get_article(self, page):
        page.prepare(self)
        try:
            page.props.author = page.doc.cssselect("td.artauthor")[0].text
        except IndexError:
            pass
        page.props.headline = page.doc.cssselect("td.artheader")[0].text
        page.props.text = page.doc.cssselect("table.body")[0]
        page.props.date = self.options['date']
        return page
    
if __name__ == '__main__':
    from amcat.scripts.tools import cli
    from amcat.tools import amcatlogging
    amcatlogging.debug_module("amcat.scraping.scraper")
    amcatlogging.debug_module("amcat.scraping.document")
    cli.run_cli(DVHNScraper)


