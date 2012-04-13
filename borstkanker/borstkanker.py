#!/usr/bin/python

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

from amcat.scraping.scraper import HTTPScraper
from amcat.scraping.document import HTMLDocument

from urlparse import urljoin, urlunsplit, parse_qs, urlsplit
from urllib import urlencode

from amcat.tools import toolkit

INDEX_URL = "http://borstkanker.nl/forum/index.php"

class BorstkankerNLScraper(HTTPScraper):
    medium_name = "Borstkanker.nl - forum"
    
    def _get_units(self):
        
        index = self.getdoc(INDEX_URL)
        cats = set()
        for a in index.cssselect('a'):
            if 'viewforum.php' in a.get('href'):
                cats.add(urljoin(INDEX_URL, a.get('href')))

        for index in (self.getdoc(url) for url in cats):
            cat = index.cssselect('#forumCrumb b')[0].text
            for thread in self.get_pages(index):
                for a in thread.cssselect('table.forumIndex td > a'):
                    url = urljoin(INDEX_URL, a.get('href'))
                    if not 'viewtopic.php' in url or not a.text:
                        continue
                    
                    yield HTMLDocument(category=cat, url=url, headline=a.text)
       
    def get_pages(self, page):
        if(page.cssselect('div.topNav')):
            yield page
            nav = page.cssselect('div.topNav')[0]
            if len(nav.cssselect('a')) > 1:
                # Pagination available
                try:
                    pages = int(nav.cssselect('a')[-2].text)
                except ValueError:
                    pages = int(nav.cssselect('a')[-1].text)

                spage = nav.cssselect('a')[1].get('href')

                url = list(urlsplit(spage))
                query = dict([(k, v[-1]) for k,v in parse_qs(url[3]).items()])
                ppp = int(query['start'])

                for pag in range(1, pages):
                    query['start'] = pag*ppp
                    url[3] = urlencode(query)

                    yield self.getdoc(urljoin(INDEX_URL, urlunsplit(url)))

    def _scrape_unit(self, thread):
        fipo = True
        thread.doc = self.getdoc(thread.props.url)      
        for page in self.get_pages(thread.doc):
            for post in page.cssselect('table.forumIndex > tr')[1:]:

                ca = thread if fipo else thread.copy(parent=thread)
                ca.props.date = toolkit.readDate(post.cssselect('span.bijSchrift')[0].text)
                ca.props.author = post.cssselect('td.auteur h2')[0].text
                if fipo:
                    row = '1'
                else:
                    row = '2'
                ca.props.title = post.cssselect('td.row'+row+' h2')[0].text

                texttd = post.cssselect('td')[0]
                texttd.cssselect('h2')[0].drop_tree()
                texttd.cssselect('.editImg')[0].drop_tree()
                texttd.cssselect('.bijSchrift')[0].drop_tree()

                ca.props.text = texttd

                yield ca

                fipo = False
        
'''
if __name__ == '__main__':
    from amcat.tools.scraping.manager import main
    main(BorstkankerNLScraper)'''
    
if __name__ == '__main__':
    from amcat.scripts.tools import cli
    from amcat.tools import amcatlogging
    amcatlogging.debug_module("amcat.scraping.scraper")
    amcatlogging.debug_module("amcat.scraping.document")
    cli.run_cli(BorstkankerNLScraper)
