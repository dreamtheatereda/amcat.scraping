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



#this document serves as a template to quickly create scrapers
#make sure to check all comment lines to adjust where needed,
#then remove those lines, along with this description
#when you're done, test the scraper for there will inevitably be
#a few errors to fix.



from amcat.scraping.scraper import DBScraper, HTTPScraper
from amcat.scraping.document import HTMLDocument, IndexDocument

from amcat.tools.toolkit import toolkit
from urlparse import urljoin

#add index url
INDEX_URL = "http://www.example.com/archive/"

#add other urls if needed
BASE_URL = "http://www.example.com/"
#etc...


#change class name
class TemplateScraper(HTTPScraper, DBScraper): 
    
    #aswell as medium name
    medium_name = "Template Scraper"


    def __init__(self, *args, **kwargs):
        
        #change 1st argument of super()
        super(TemplateScraper, self).__init__(*args, **kwargs)


    def _get_units(self):
        """get pages, ideally distinct by category"""
        
        index = self.getdoc(INDEX_URL)
        
        #change the next line to get a list of <a> tags linking to pages
        for some_link in index.cssselect("some css syntax pattern"):
            
            #change some_link to your own variable name for clarity
            href = some_link.get('href')
            
            #in fact, just check if all lines work in your case.
            url = urljoin(BASE_URL,href)
            
            #if you know some other props beforehand, add them as argument 
            yield IndexDocument(url=url,date=self.options['date'])
        
    def _scrape_unit(self, ipage):
        """gets articles from an index page"""
        ipage.prepare(self)
        
        #if the page contains a relevant picture, add it
        imgurl = 
        ipage.bytes = self.opener.opener.open(imgurl).read()

        ipage.doc = self.getdoc(ipage.props.url)
        
        #add page number if present
        ipage.page = 

        #add category if present
        ipage.props.category = ""

        #change the next line to get a list of html tags linking to sole articles
        for link_tag in ipage.doc.cssselect("some css syntax pattern"):

            #check if next line is correct in your case
            href = link_tag.get('href')

            #replace BASE_URL with where the articles are contained, if needed
            url = urljoin(BASE_URL,href)

            #now we're heading into the page which contains the article
            page = HTMLDocument(date = ipage.props.date,url=url)
            page.prepare(self)
            page.doc = self.getdoc(page.props.url)
            
            #use get_article() to add page properties
            yield self.get_article(page)

            #add article to index page
            ipage.addchild(page)

        yield ipage

    def get_article(self, page):
        #use mainly page.doc.cssselect() and regexp or string methods to fill the following lines

        #don't forget cssselect returns a list
        page.props.author = page.doc.cssselect("some css syntax pattern")[0].text
        #you can use text_content()
        page.props.headline = ""
        #you can also use drop_tree() to rid unwanted HTML
        page.props.text = ""
        #we aren't done yet, scroll further down
        return page




if __name__ == '__main__':
    from amcat.scripts.tools import cli
    from amcat.tools import amcatlogging
    amcatlogging.debug_module("amcat.scraping.scraper")
    amcatlogging.debug_module("amcat.scraping.document")
    #change argument
    cli.run_cli(TemplateScraper)


#thanks for contributing! If you're lucky, the whole thing works already, but there are likely a few errors you'll need to fix. this template is only meant to speed up the process.
#don't forget to remove print statements (those can cause encoding errors) 
#don't forget to remove these comments.
