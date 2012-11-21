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

from amcat.scraping.scraper import DatedScraper, HTTPScraper
from amcat.scraping.document import HTMLDocument, IndexDocument


from datetime import date
from urlparse import urljoin
from amcat.tools.toolkit import readDate


CATEGORIES_TO_SCRAPE = [
    #('forum name','forum id'),
    ('nieuws & achtergronden',4)
    ]





INDEX_URL = "http://forum.fok.nl"

class FokForumScraper(HTTPScraper, DatedScraper):
    medium_name = "Fok Forum"

    def __init__(self, *args, **kwargs):
        super(FokForumScraper, self).__init__(*args, **kwargs) 

    def _login(self,username,password):
        """Not used for logging in, but to avoid the pop up screen about cookies, which ironically needs a cookie to avoid."""
        page = self.opener.opener.open(INDEX_URL)

        cookie_string = page.info()["Set-Cookie"]
        token = cookie_string.split(";")[0]
        self.opener.opener.addheaders.append(("Cookie",token+"; allowallcookies=1"))
        page = self.opener.opener.open(INDEX_URL)


    def _get_units(self):
        """get pages"""

        index = self.getdoc(INDEX_URL) 


        for forum,forum_id in CATEGORIES_TO_SCRAPE:
            href = urljoin(INDEX_URL,"forum/{fid}".format(fid=forum_id))
            yield IndexDocument(url=href, date=self.options['date'],category = forum)






        
    def _scrape_unit(self, ipage):
        """gets articles from a page"""
        ipage.prepare(self)



        ipage.bytes = ""


        ipage.doc = self.getdoc(ipage.props.url)
        ipage.page = ""
        for tr in ipage.doc.cssselect("tbody#foruminsert2 tr"):
            _date = tr.cssselect("td.tLastreply a")[0].text
            if str(date.today()) not in str(readDate(_date)): 
                pass
            else:
            
                href = tr.cssselect("td.tTitel a")[0].get('href')
                url = urljoin(INDEX_URL,href)
            
                page = HTMLDocument(date = ipage.props.date,url=url)
                page.prepare(self)
            
                page.doc = self.getdoc(page.props.url)
                _date = page.doc.cssselect("span.post_time a")[0].text
                if str(date.today()) in str(readDate(_date)):
                    yield self.get_article(page)
                    ipage.addchild(page)

        yield ipage

    def get_article(self, page):
        page.props.author = page.doc.cssselect("span.post_sub a.username")[0].text
        page.props.headline = page.doc.cssselect("div.fieldholder h1")[0].text_content()
        
        page.props.text = page.doc.cssselect("div.postmain_right")[0].text_content()
        page.coords=''
        return page




if __name__ == '__main__':
    from amcat.scripts.tools import cli
    from amcat.tools import amcatlogging
    amcatlogging.debug_module("amcat.scraping.scraper")
    amcatlogging.debug_module("amcat.scraping.document")
    cli.run_cli(FokForumScraper) 



