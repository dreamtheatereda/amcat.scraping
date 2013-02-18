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
from amcat.scraping.document import HTMLDocument, Document


from datetime import date
from urlparse import urljoin
from amcat.tools.toolkit import readDate


CATEGORIES_TO_SCRAPE = [
    #('forum name','forum id'),
    ('klaagbaak',5),
    ('politiek',56),
    ('Nieuws & Achtergronden',4)
    ]

SEARCHTERMS = ["huisarts","spreekuur","dokter","wachtrijen","praktijk","zorgkosten","arts"] #only pages whose text_content() contain one of the search terms are scraped

FROMDATE = date(year=2012,month=05,day=01)


INDEX_URL = "http://forum.fok.nl"

class FokForumScraper(HTTPScraper):
    medium_name = "Fok Forum"

    def __init__(self, *args, **kwargs):
        super(FokForumScraper, self).__init__(*args, **kwargs) 


    def _get_units(self):
        """get pages"""

        
        page = self.opener.opener.open(INDEX_URL)

        cookie_string = page.info()["Set-Cookie"]
        token = cookie_string.split(";")[0]
        self.opener.opener.addheaders.append(("Cookie",token+"; allowallcookies=1"))
        page = self.opener.opener.open(INDEX_URL)



        index = self.getdoc(INDEX_URL) 


        for forum,forum_id in CATEGORIES_TO_SCRAPE:
            href = urljoin(INDEX_URL,"forum/{}/".format(forum_id))
            doc = self.getdoc(href)
            for option in doc.cssselect("select.hopforum option"):
                link = option.get('value')
                newhref = urljoin(href,link)
                newdoc = self.getdoc(newhref)
                br = False
                for div in newdoc.cssselect("div.mb2")[1:]:
                    for tr in div.cssselect("tbody tr"):
                        from lxml import etree
                        if readDate(tr.cssselect("td.tLastreply a")[0].text).date() > FROMDATE:
                            yield tr
                        else:
                            br = True
                            break
                    if br == True:
                        break
                if br == True:
                    break

        
    def _scrape_unit(self, tr):
        """gets articles from a page"""
        url = urljoin("http://forum.fok.nl",tr.cssselect("td.tTitel a")[0].get('href'))
        topic = HTMLDocument(url=url,
                             section=tr.cssselect("td.tFolder")[0].text_content())
        
        topic.prepare(self)
        content = topic.doc.text_content()
        if any([(s in content) for s in SEARCHTERMS]):
            for comment in self.get_comments(topic):
                yield comment
            yield self.get_article(topic)



    def get_article(self, page):
        page.props.date = readDate(page.doc.cssselect("#pt1")[0].text_content())
        page.props.author = page.doc.cssselect("span.post_sub a.username")[0].text
        page.props.headline = page.doc.cssselect("div.fieldholder h1")[0].text_content()
        
        page.props.text = page.doc.cssselect("div.postmain_right")[0]
        page.coords=''
        return page

    def get_comments(self, topic):
        first = True
        for page in self.get_pages(topic.doc):
            if first == True:
                comments = page.cssselect("div.post")[1:]
                first = False
            else:
                comments = page.cssselect("div.post")
            for div in comments:
                comment = HTMLDocument()
                comment.parent = topic
                comment.props.author = div.cssselect("div.postholder_top a.username")[0]
                comment.props.date = readDate(div.cssselect("div.postholder_top span.post_time")[0].text_content())
                comment.props.text = div.cssselect("div.postholder_bot div.contents")[0]
                yield comment
                

    def get_pages(self,doc):
        yield doc
        for a in doc.cssselect("nav div.pagesholder a"):
            url = urljoin("http://forum.fok.nl",a.get('href'))
            yield self.getdoc(url)

if __name__ == '__main__':
    from amcat.scripts.tools import cli
    from amcat.tools import amcatlogging
    amcatlogging.debug_module("amcat.scraping.scraper")
    amcatlogging.debug_module("amcat.scraping.document")
    cli.run_cli(FokForumScraper) 



