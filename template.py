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

#useful imports
from urllib import urlencode
from urlparse import urljoin

from amcat.scraping.document import Document, HTMLDocument
from amcat.scraping.scraper import HTTPScraper
from amcat.scraping.scraper import DBScraper, DatedScraper #choose one
from amcat.scraping.toolkit import parse_form
from amcat.tools.toolkit import readDate

class TemplateScraper(HTTPScraper, DBScraper):
    medium_name = "scraping template"
    index_url = "http://example.com"
    login_url = "http://example.com/handle_login"

    def _login(self, username, password):
        """login method for DBScraper
        @param username: self.options['username']
        @param password: self.options['password']"""

        #get initial cookies like sesid
        self.open(self.index_url)

        #get login params (whether or not from the website), encode into POST request
        login_form = self.getdoc(self.login_url).cssselect("form")[0]
        form = parse_form(login_form)
        form['email'] = username
        form['password'] = password
        response_json = self.open(self.login_url, urlencode(form))

        #if possible check response, saves future trouble
        response = json.loads(response_json)
        if response['status'] != "ok":
            raise ValueError("login status returned not OK but {}".format(response))

    def _get_units(self):
        #yield any kind of unit. Could be links to indexes of categories, could be links to articles
        for li in self.getdoc(self.index_url).cssselect("#articles li"):
            href = li.cssselect("a")[0].get('href')
            url = urljoin(self.index_url, href)
            yield url

    def _scrape_unit(self, unit):
        article = HTMLDocument(url = unit)
        article.prepare(self) #gets html document and assigns it to article.doc

        article.props.text = article.doc.cssselect("#main div.text p")
        #article properties:
        #date, section, pagenr, headline, byline
        #url, externalid, text, parent, author
        #meta: dateline, kicker, tags
        #include any possibly relevant information

        for comment in self.get_comments(article):
            comment.is_comment = True #don't forget this
            comment.props.parent = article
            yield comment
        yield article

    def get_comments(self, article):
        for div in article.doc.cssselect("#comments div.comment"):
            comment = HTMLDocument()
            comment.props.text = div.cssselect("div.content div.text")
            yield comment
            

if __name__ == '__main__':
    from amcat.scripts.tools import cli
    from amcat.tools import amcatlogging
    amcatlogging.info_module("amcat.scraping")
    cli.run_cli(TemplateScraper)


