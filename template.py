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

#possibly useful imports:

#from urllib import urlencode
#from urlparse import urljoin
#from amcat.tools.toolkit import readDate
#from amcat.scraping.tools import toolkit

INDEX_URL = "" #Add url which contains links to all pages
LOGIN_URL = "" #Add login url


from amcat.scraping.scraper import HTTPScraper,DBScraper,DatedScraper,Scraper
#HTTPScraper is for any website,
#Datedscraper is for a scraper with a certain date
#DBScraper requires username/password arguments with a login function
#Scraper is most basic.

class TemplateScraper(HTTPScraper, DBScraper): #change class name
    medium_name = "Template" #change medium name

    def __init__(self, *args, **kwargs):
        super(TemplateScraper, self).__init__(*args, **kwargs) #change 'TemplateScraper'


    def _login(self, username, password):
        
        #one of the following code blocks should be implemented and adjusted, not either.
        page = self.getdoc(LOGIN_URL)
        form = toolkit.parse_form(page)
        form['username'] = username
        form['password'] = password
        self.open(LOGIN_URL, urlencode(form))

        #if that didn't work, add form keys manually:
        POST_DATA = {
            'email' : username,
            'password' : password,
            #other keys/values should be added and former keys may be changed depending on website form
            }
        self.open(LOGIN_URL, URLENCODE(POST_DATA))

        


    def _get_units(self):
        # yield any unit, 
        # as long as it contains the info needed to scrape the unit in next function.
        # could be a dict, a url, a html document...
        index_dict = {
            'year' : self.options['date'].year,
            'month' : self.options['date'].month,
            'day' : self.options['date'].day,
            #more keys/values may be added depending on the web page URL
        }


        url = INDEX_URL.format(**index_dict)
        index = self.getdoc(url) 
        
        for unit in index.cssselect(''):
            href = unit.cssselect('')[0].get('href')
            yield urljoin(url, href)

        
    def _scrape_unit(self, url):
        # article properties: 
        # date, section, pagenr, headline, byline, length (autogenerated),
        # url (already present), text, parent, medium (auto), author

        for a in self.getdoc(url).cssselect(" "):
            
            href = a.get('href')
            url = urljoin(url, href)

            page = HTMLDocument(date = ipage.props.date,url=url)
            page.prepare(self)
            page.doc = self.getdoc(page.props.url)
            yield self.get_article(page)


    def get_article(self, page):
        #use mainly page.doc.cssselect() to fill the following lines
        page.props.author = 
        page.props.headline = 
        page.props.text = 
        return page




if __name__ == '__main__':
    from amcat.scripts.tools import cli
    from amcat.tools import amcatlogging
    amcatlogging.debug_module("amcat.scraping.scraper")
    amcatlogging.debug_module("amcat.scraping.document")
    cli.run_cli(TemplateScraper) #change 'TemplateScraper'


