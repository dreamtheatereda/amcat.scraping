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

#this piece makes it possible to quickly create a new scraper. As there are thousands of papers and other mediums out on the web, we can never have enough scrapers.

from amcat.scraping.scraper import DBScraper, HTTPScraper
from amcat.scraping.document import HTMLDocument, IndexDocument
from amcat.scraping import toolkit as stoolkit #remove this line if not used

#possibly useful imports:

#from urllib import urlencode
#from urlparse import urljoin

INDEX_URL = "" #Add url which contains links to all index pages
LOGIN_URL = "" #Add login url

class TemplateScraper(HTTPScraper, DBScraper): #change class name
    medium_name = "Template" #change medium name

    def __init__(self, *args, **kwargs):
        
        super(TemplateScraper, self).__init__(*args, **kwargs)
        #some scrapers don't even have __init__ methods, 
        #in some cases adding code may be useful though. 


    def _login(self, username, password):
        """log in on the web page
        @param username: username to log in with
        @param password: password 
        """





        #one of the following code blocks should be implemented and adjusted, not either.

        try: 
            page = self.getdoc(LOGIN_URL)
            form = stoolkit.parse_form(page)
            form['username'] = username
            form['password'] = password
            self.opener.opener.open(LOGIN_URL, urlencode(form))



        #if that didn't work, add form keys manually:
        except: 
            POST_DATA = {
                'email' : username,
                'password' : password,
                #other keys/values should be added and former keys may be changed depending on website form
            }
            self.opener.opener.open(LOGIN_URL, URLENCODE(POST_DATA))

        








    def _get_units(self):
        """papers are often organised in blocks (pages) of articles, this method gets the blocks, articles are to be gotten later"""



        index_dict = {
            'year' : self.options['date'].year,
            'month' : self.options['date'].month,
            'day' : self.options['date'].day,
            #more keys/values may be added depending on the web page URL
        }




        INDEX_URL = INDEX_URL % index_dict
        index = self.getdoc(INDEX_URL) 
        #this is the index of units, the page that contains a list of index pages,
        #pages which contain lists of articles.



        #add html tags with the links to the ipages in the next line
        units = index.cssselect(''):
        for article_unit in units:
            #add 'a' tag in next line
            href = article_unit.cssselect('').get('href')
            yield IndexDocument(url=href, date=self.options['date'])






        
    def _scrape_unit(self, ipage): # 'ipage' means index_page
        """gets articles from an index page"""
        ipage.prepare(self)



        ipage.bytes = "?" #whats this?


        ipage.doc = self.getdoc(ipage.props.url)
        ipage.page = "" #add paper page number
        ipage.props.category = "" #add ipage category if present

        #add html tag which contains link to article
        for a in ipage.doc.cssselect(" "):
            #make sure the following line works in your case
            url = a.get('href')
            
            #now we're heading into the page which contains the article!
            page = HTMLDocument(date = ipage.props.date,url=url)
            page.prepare(self)
            # Get article
            page.doc = self.getdoc(page.props.url)
            yield self.get_article(page)

            # Add article to index page
            ipage.addchild(page)

        yield ipage

    def get_article(self, page):
        #use mainly page.doc.cssselect() to fill the following lines
        page.props.author = ""
        page.props.headline = ""
        page.props.text = ""
        return page




if __name__ == '__main__':
    from amcat.scripts.tools import cli
    from amcat.tools import amcatlogging
    amcatlogging.debug_module("amcat.scraping.scraper")
    amcatlogging.debug_module("amcat.scraping.document")
    cli.run_cli(TemplateScraper)


#thanks for contributing!
