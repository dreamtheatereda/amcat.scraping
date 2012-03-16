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
from amcat.scraping.document import HTMLDocument
from amcat.scraping.phpbbscraper import PhpBBScraper
from amcat.scraping.scraper import DBScraper

MESSAGES_PER_THREAD = 15
THREADS_PER_BOARD= 20

class BorstkankerForumScraper(PhpBBScraper, DBScraper):
    index_url = "http://www.borstkankerforum.nl/forum/"
    
    def _scrape_unit(self, url=INDEX_URL, cat=None):
        """
        Recursively get all boards. For every board, call get_threads,
        to get all (forum!) threads.
        """
        index = self.getdoc(url)

        for td in index.cssselect('tr.windowbg2 td[align=left]'):
            a = td.cssselect('a')[0]
            
            
            ####cat=None
            _cat = a.text_content() if not cat else " > ".join([cat, a.text_content()])
            url = a.get('href')

            board = HTMLDocument(**{
                'category' : _cat,
                'url' : url
            })

            # Get all threads
            page = board.copy(); page.prepare(self)
            for thread in self.get_threads(page):
                yield thread

            for thread in self.init(url=url, cat=_cat):
                # Get sub-boards' threads
                yield thread
                break

    def _get_units(self, board):
        """This method gets all threads in a board."""
        try:
            pages = [board,]
            for url in self.parse_pagination(board.doc):
                page = board.copy()
                page.props.url = url

                # Download document..
                page.prepare(self, force=True)
                pages.append(page)

        except IndexError:
            # This probably the forum-index page
            pass
        else:
            for page in pages: 
                # First tr should be in <thread>
                for tr in page.doc.cssselect('table[class=bordercolor] tr')[1:]: 
                    # windowbg2 indicates a sub-board, not a thread.
                    if tr.get('class') == 'windowbg2': continue

                    tds = tr.cssselect('td')

                    # 3rd td contains link to thread / thread-name
                    # 4th td contains topic-starter's name
                    a = tds[2].cssselect('a')[0]
                    page.props.url = a.get('href')
                    page.props.headline = a.text_content()
                    page.props.author = tds[3].text_content()

                    yield page 

                    break

                break

    def parse_pagination(self, el):
        """
        Parse pagination displayed at the bottom of each thread / board.

        @param el: root html element
        @type el: lxml.html object

        @return: generator yielding urls (including non-displayed pages). This method
                 does not return the first page.
        """
        td = el.cssselect('td[class=catbg] td')[0] 
        aes = td.cssselect('a')
        if len(aes) > 1:
            last = aes[-2].get('href')

            # Determine wehther this is a board or thread
            ppp = THREADS_PER_BOARD if 'board' in last else MESSAGES_PER_THREAD
            pages = (int(last.split('.')[-1]) / ppp)
            base_url = ".".join(last.split('.')[:-1])

            for page in range(1, pages+1):
                yield "%s.%s" % (base_url, str(page*ppp))
        
if __name__ == '__main__':
    from amcat.scripts.tools import cli
    from amcat.tools import amcatlogging
    amcatlogging.debug_module("amcat.scraping.scraper")
    amcatlogging.debug_module("amcat.scraping.document")
    cli.run_cli(BorstkankerForumScraper)
