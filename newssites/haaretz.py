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
from amcat.scraping.scraper import HTTPScraper, DBScraper
from amcat.tools.toolkit import readDate

#from urllib import urlencode
#from urlparse import urljoin
#from amcat.scraping.tools import toolkit

from urllib import quote_plus


class HaaretzScraper(HTTPScraper, DBScraper):
    medium_name = "Haaretz"
    login_url = "https://sso.haaretz.com/sso/sso/signIn?cb=parseEngReply&newsso=true&fromlogin=true&layer=eng_login&userName={username}&password={password}"
    search_url = "http://www.haaretz.com/misc/search-results?startDate={date.day:02d}%2F{date.month:02d}%2F{date.year:04d}&author=&page={pagenr}&q=&submitBtn=textSearch&endDate={date.day:02d}%2F{date.month:02d}%2F{date.year:04d}&view=results&search_type=site"

    def _login(self, username, password):
        username = quote_plus(username)
        password = quote_plus(password)
        res = self.open(self.login_url.format(**locals())).read()
        next_url = res.split('":"')[1].split("\"}'")[0]
        self.open(next_url)
        if not 'success' in res:
            print(res)
            raise Exception("Login failed")
        
    def _get_units(self):
        for page in self.get_pages():
            for post in page.cssselect("div.post"):
                article = HTMLDocument(
                    url = post.cssselect("span.h3 a")[0].get('href'),
                    headline = post.cssselect("span.h3")[0].text_content().strip(),
                    date = readDate(post.cssselect("span.comments span")[0].text.replace(".","-").split(" ")[1]))
                yield article

    def get_pages(self):
        date = self.options['date']
        pagenr = 0
        index = self.getdoc(self.search_url.format(**locals()))
        paging = index.cssselect("div.paging li")
        if paging:
            max_page = int(paging[-2].text_content())
        elif "Your search did not match any articles." in index.cssselect("div.search_results")[0].text_content():
            print("\n\"Your search did not match any articles.\"\n")
            return
        else:
            yield index
            return
        yield index
        for pagenr in range(1, max_page+1):
            yield self.getdoc(self.search_url.format(**locals()))
        
    def _scrape_unit(self, article):
        article.prepare(self)
        try:
            article.props.byline = article.doc.cssselect("div.main-news h2")[0]
        except IndexError:
            pass
        article.props.text = article.doc.cssselect("#articleContentAndWidgetsContainer p")
        if article.doc.cssselect("div.writer"):
            article.props.author = article.doc.cssselect("div.writer")[0].text_content()
        if article.doc.cssselect("ul.breadcrumbs"):
            article.props.section = " > ".join([li.text_content() for li in article.doc.cssselect("ul.breadcrumbs")])            
        yield article
        for comment in self.scrape_comments(article):
            comment.is_comment = True
            yield comment

    def scrape_comments(self, article):
        for item in article.doc.cssselect("#commentsTab li.mainComment"):
            mcomment = self.scrape_comment(item, article)        
            yield mcomment
            for li in item.cssselect("ul.answers li.commentItem"):
                yield self.scrape_comment(li, mcomment)                    

    def scrape_comment(self, html, parent):
        c = HTMLDocument(
            text = html.cssselect("div.text-holder"),
            headline = html.cssselect("a.commentTitle")[0].text_content().strip(),
            section = parent.props.section,
            date = readDate(" ".join([t.text for t in html.cssselect("ul.meta li.createdate, li.createtime")])),
            author = html.cssselect("ul.meta li.by")[0].text.strip().lstrip("By").strip(),
            url = parent.props.url + "#{}".format(html.cssselect("a.commentTitle")[0].get('id')))
        c.props._parent = "{p.props.headline}, {p.props.date}".format(p = parent)
        return c


if __name__ == '__main__':
    from amcat.scripts.tools import cli
    from amcat.tools import amcatlogging
    amcatlogging.debug_module("amcat.scraping.scraper")
    amcatlogging.debug_module("amcat.scraping.document")
    cli.run_cli(HaaretzScraper)


