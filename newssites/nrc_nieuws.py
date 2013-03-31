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

import re
from amcat.scraping.document import Document, HTMLDocument


from urlparse import urljoin
from urllib2 import HTTPError

INDEX_URL = "http://www.nrc.nl/nieuws/overzicht/{y:04d}/{m:02d}/{d:02d}/"
COMMENTS_URL = "http://nrcnl.disqus.com/thread.js?slug={t}&p={p}"

import json
from amcat.scraping.scraper import HTTPScraper,DatedScraper
from amcat.tools.toolkit import readDate

class WebNieuwsNRCScraper(HTTPScraper, DatedScraper):
    medium_name = "NRC website - nieuws"

    def __init__(self, *args, **kwargs):
        super(WebNieuwsNRCScraper, self).__init__(*args, **kwargs) 


    def _get_units(self):

        
        y = self.options['date'].year
        m = self.options['date'].month
        d = self.options['date'].day
        

        url = INDEX_URL.format(**locals())
        index = self.getdoc(url)
        index.cssselect("div.watskeburt section")[1].drop_tree()
        articles = index.cssselect('div.watskeburt article')+index.cssselect("div.watisnjouw_articles article")
        for unit in articles:
            try:
                href = unit.cssselect('h2 a')[0].get('href').lstrip("./")
            except IndexError:
                href = unit.cssselect('dd a')[0].get('href').lstrip("./")
            url = urljoin("http://www.nrc.nl/",href)
            yield HTMLDocument(url=url, date=self.options['date'])


        
    def _scrape_unit(self, page): 
        page.prepare(self)
                    
        page.doc = self.getdoc(page.props.url)
        try:
            page.props.author = page.doc.cssselect("div.author a")[0].text_content()
        except IndexError:
            page.props.author = "onbekend"
        page.props.headline = page.doc.cssselect("div.article h1")[0].text_content()
        page.props.section = re.search("nrc.nl/([a-z]+)/", page.props.url).group(1).capitalize()

        try:
            page.props.text = page.doc.cssselect("#broodtekst")[0]
        except IndexError: #next checkt
            page.props.text = page.doc.cssselect("div.article p")
            for comment in self.get_comments(page):
                comment.is_comment = True
                yield comment
        else:

            if page.doc.cssselect("#disqus_thread"):
                for comment in self.get_comments(page):
                    yield comment
                

        yield page


    def get_comments(self, page):
        title = page.props.url.split("/")[-2].replace("-","_")
        
        firsturl = COMMENTS_URL.format(t=title,p=1)
        txt = self.open(firsturl).read()
        nexturl = COMMENTS_URL.format(t=title,p=2)
        nxt = self.open(nexturl).read()

        i = 1

        comments = {}

        while txt != nxt:
            start = txt.find("jsonData = {")+11;end = txt.find("}}; ")+2
            _json = txt[start:end]
            data = json.loads(_json)
            for post in data['posts'].items():
                comment = Document()
                cid = post[0]
                post = post[1]
                comment.props.author = post['user_key']
                comment.props.text = post['raw_message']
                comment.props.date = readDate(post['real_date'])
                comment.parent = post['parent_post_id']
                comments[str(cid)] = comment
            nexturl = COMMENTS_URL.format(t=title,p=i+1)
            txt = nxt
            nxt = self.open(nexturl).read()
            
        for comment in comments.values():
            if comment.parent:
                comment.parent = comments[str(comment.parent)]
            else:
                comment.parent = page
            yield comment

            



if __name__ == '__main__':
    from amcat.scripts.tools import cli
    from amcat.tools import amcatlogging
    amcatlogging.debug_module("amcat.scraping.scraper")
    amcatlogging.debug_module("amcat.scraping.document")
    cli.run_cli(WebNieuwsNRCScraper)


