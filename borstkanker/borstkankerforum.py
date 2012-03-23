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

#from amcat.scraping.scraper import urlencode
from amcat.scraping.scraper import HTTPScraper, DBScraper
from amcat.scraping.document import HTMLDocument

from urlparse import urljoin, urlunsplit, parse_qs, urlsplit
from urllib import urlencode

from amcat.tools import toolkit

class BorstkankerForumScraper(HTTPScraper, DBScraper):
    index_url = "http://www.borstkankerforum.nl/forum/"
    medium_name = "Borstkankerforum.nl - forum"

    def _login(self, username, password):
        form = self.getdoc(self.index_url).cssselect('form')[0]

        self.opener.opener.open(form.get('action'), urlencode({
            'user' : username,
            'passwrd' : password,
            'cookielength' : '-1'
        })).read()
            
    def _get_units(self):
        index = self.getdoc(self.index_url)

        for cat_title, cat_doc in self.get_categories(index):
            for page in self.get_pages(cat_doc):
                for fbg in page.cssselect('tr')[1:]:
                    for a in fbg.cssselect('.windowbg a'):
                        url = urljoin(self.index_url, a.get('href'))
                        if not a.find("img") is None:
                            continue
                        yield HTMLDocument(headline=a.text, url=url, category=cat_title)
    
    def get_categories(self, index):
        """
        @yield: (category_name, lxml_doc)
        """
        hrefs = index.cssselect('.windowbg2 td[align=left] a')

        for href in hrefs:
            url = urljoin(self.index_url, href.get('href'))
            yield href.text, self.getdoc(url) 
    
    def _scrape_unit(self, thread):
        fipo = True # First post
        thread.doc = self.getdoc(thread.props.url)
        for page in self.get_pages(thread.doc):
            for post in page.cssselect('.windowbg'):
                ca = thread if fipo else thread.copy(parent=thread)
                #print('!!!!!!!!!!!!!!!!!!!!!!')
                #print( post.cssselect('.smalltext')[1].text_content().split('op:')[1][14:-2] )
                ca.props.date = toolkit.readDate(post.cssselect('.smalltext')[1].text_content()[14:-2])
                
                divs = post.cssselect('div')
                if len(divs) < 4: # guest
                    title = post.cssselect('a')[2].text
                    ca.props.text = divs[2]
                    ca.props.author = post.cssselect('b')[0].text
                else:    
                    if post.cssselect('a')[5].find("img") is None:
                        title = post.cssselect('a')[5].text
                    else:
                        title = post.cssselect('a')[6].text
                    ca.props.text = divs[3]
                    ca.props.author = post.cssselect('a')[0].text
                    
                if fipo:
                    optitle = title
                if title:
                    ca.props.headline = title
                else:
                    ca.props.headline = 're: {}'.format( optitle )

                

                yield ca

                fipo = False

    def get_pages(self, page):
        """Get each page specified in pagination division."""
        
        yield page # First page, is always available
        
        nav = page.cssselect('.catbg')[0]
        nava = nav.cssselect('a')[:-5]
        if len(nava) > 1:
            # Pagination available    

            pages = int(nava[-1].text)
            spage = nava[0].get('href')
            
            url = list(urlsplit(spage))
            query = dict([(k, v[-1]) for k,v in parse_qs(url[3]).items()])
            
            ppp = query['topic'].split('.')
            if len(ppp) == 1:
                ppp.append(0)
            for pag in range(1, pages):
                query['topic'] = ppp[0]+'.'+pag*ppp[1]
                url[3] = urlencode(query)
                
                yield self.getdoc(urljoin(self.index_url, urlunsplit(url)))

if __name__ == '__main__':
    from amcat.scripts.tools import cli
    from amcat.tools import amcatlogging
    amcatlogging.debug_module("amcat.scraping.scraper")
    amcatlogging.debug_module("amcat.scraping.document")
    cli.run_cli(BorstkankerForumScraper)
