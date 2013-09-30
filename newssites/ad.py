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
from urlparse import urljoin
from urllib2 import HTTPError
from lxml import etree

from amcat.tools.toolkit import readDate
from amcat.scraping.document import Document, HTMLDocument
from amcat.scraping.htmltools import create_cc_cookies
from amcat.scraping.scraper import HTTPScraper,DatedScraper

class WebADScraper(HTTPScraper, DatedScraper):
    medium_name = "AD website"
    index_url = "http://www.ad.nl/ad/nl/1401/archief/integration/nmc/frameset/archive/archiveDay.dhtml?archiveDay={self.options[date].year:04d}{self.options[date].month:02d}{self.options[date].day:02d}"

    def _set_cookies(self):
        for cookie in create_cc_cookies(".ad.nl"):
            self.opener.cookiejar.set_cookie(cookie)

    def _get_units(self):
        self._set_cookies()        
        index = self.getdoc(self.index_url.format(**locals()))
        for tag in index.cssselect('div.articleOverview h2, div.articleOverview dl dd'):
            if tag.tag == "h2":
                self.cur_section = tag.text_content().strip()
            else:
                href = tag.cssselect('a')[0].get('href')
                yield HTMLDocument(url = urljoin(index.base_url, href), 
                                   date = self.options['date'])
        
    def _scrape_unit(self, article): 
        article.prepare(self)
        article = self.get_article(article)
        yield article
        for comment in self.get_comments(article):
            comment.is_comment = True
            comment.parent = article
            yield comment

    def get_article(self, article):
        author_date = article.doc.cssselect('span.author')[0].text_content().strip()
        pattern = re.compile("^(Door: ([a-zA-Z0-9 ]+))?(\n\n([0-9]+\-[0-9]+\-[0-9]+))?")
        match = pattern.match(author_date)
        article.props.author = match.group(2)
        article.props.date = readDate(match.group(4))
        try:
            article.props.source = author_date.split("bron:")[1].strip()
        except IndexError:
            pass
        article.props.text = article.doc.cssselect("#detail_content p.intro,#detail_content section.clear > p")
        article.props.headline = article.doc.cssselect("h1")[0].text
        article.props.section = self.cur_section
        return article

    comment_url = "http://www.ad.nl/ad/reaction/listContent.do?componentId={cid}&navigationItemId={nid}&language=nl&pageType=articleDetail&reactionLayout=small&page={page}"

    def get_comments(self,page):
        for doc in self.get_comment_pages(page):
            for li in doc.cssselect("ul li"):
                comment = HTMLDocument()
                comment.props.author = li.cssselect("cite")[0].text.strip()
                comment.props.text = li.cssselect("blockquote")[0]
                comment.props.date = readDate(li.cssselect("span.time")[0].text)
                yield comment

    def get_comment_pages(self,page):
        if not page.doc.cssselect("#reaction"):
            return
        n_id, c_id = page.props.url.split("/")[4::4] #5 and #9
        doc = self.getdoc(self.comment_url.format(page=0,cid=c_id,nid=n_id))
        try:
            total = int(doc.cssselect("div.pagenav")[0].text.split(" van ")[1])
        except IndexError:
            yield doc;return
        except AttributeError:
            return
        for x in range(total-1):
            for a in doc.cssselect("div.pagenav a"):
                if "volgende" in a.text:
                    onclick = a.get('onclick')
            start = onclick.find("getReactions(")+13; end = onclick.find(")",start)
            href = [arg.strip("\"';() ") for arg in onclick[start:end].split(",")][0]
            yield self.getdoc(urljoin(doc.base_url,href))


if __name__ == '__main__':
    from amcat.scripts.tools import cli
    from amcat.tools import amcatlogging
    amcatlogging.debug_module("amcat.scraping.scraper")
    amcatlogging.debug_module("amcat.scraping.document")
    cli.run_cli(WebADScraper)


