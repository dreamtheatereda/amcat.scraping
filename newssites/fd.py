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
from amcat.scraping.scraper import DBScraper, HTTPScraper
from amcat.tools.toolkit import readDate

from urllib import urlencode
import json
import re
from datetime import timedelta

class WebFDScraper(HTTPScraper, DBScraper):
    medium_name = "Het Financieele Dagblad - website"
    initial_url = "http://www.fd.nl"

    login_url = "http://fd.nl/handle_login?{params}" #POST doesn't seem to work

    def _login(self, username, password):
        self.open(self.initial_url)
        login_parameters = {
            'email' : username,
            'password' : password
            }
        params = urlencode(login_parameters)
        response_json = self.open(self.login_url.format(**locals())).read()
        response = json.loads(response_json)
        if response['status'] != "ok":
            raise ValueError("login status returned not OK but {}".format(response))


    

    def _get_units(self):

        class Unit(object):
            def __init__(self, row):
                self.row = row
            def __unicode__(self):
                return unicode(self.row['id'])

        start = 0
        result = self.search_result(start)
        while result['response']['numFound'] > result['response']['start']:
            for row in result['response']['docs']:
                yield Unit(row)
                
            start += 10
            result = self.search_result(start)

            
        
    def search_result(self, start):
        search_url = "http://fd.nl/solr/select/"

        today = self.options['date']
        tomorrow = today + timedelta(days = 1)
        query_parameters = {
            'd' : today.day,
            'm' : today.month,
            'y' : today.year,
            'nd' : tomorrow.day,
            'nm' : tomorrow.month,
            'ny' : tomorrow.year
            }
            
        request_parameters = {
            'wt' : 'json',
            'q' : 'publication:fd publishdate:[{y:04d}-{m:02d}-{d:02d}T00:00:00.000Z TO {ny:04d}-{nm:02d}-{nd:02d}T00:00:00.000Z]'.format(**query_parameters),
            'start' : start,
            'fq' : 'contenttype:article',
            }
        result_json = self.open(search_url, urlencode(request_parameters)).read()
        return json.loads(result_json)
        
    def _scrape_unit(self, unit):
        row = unit.row
        article = HTMLDocument()
        article.props.headline = row['title']
        article.props.section = row['home_section_name']
        article.props.author = row['creator']
        article.props.date = readDate(row['publishdate'])
        if 'tag' in row.keys():
            article.props.tags = ", ".join(row['tag'])

        article.props.url = self.get_article_url(row['objectid'])
        article.doc = self.getdoc(article.props.url)
        article.props.text = article.doc.cssselect("div.left span.article")[0]
        p = "[A-Za-z]+( [A-Za-z]+)+\n\n([A-Z][a-z]+( [A-Za-z]+){0,2})\n\n"
        match = re.search(p, article.props.text.text_content())
        if match:
            article.props.dateline = match.group(2)
        for comment in self.get_comments(article.doc):
            comment.is_comment = True
            comment.props.parent = article
            yield comment

        yield article
             


    redirect_url = "http://fd.nl/?service=searchRedirect&id={artid}"

    def get_article_url(self, artid):
        script = self.open(self.redirect_url.format(**locals())).read()
        start = script.find("location.href='") + 15; end = script.find("'", start)
        return script[start:end]

    def get_comments(self, doc):
        for div in doc.cssselect("#commentsList div.topDivider"):
            comment = HTMLDocument()
            comment.props.text = div.cssselect("div.wordBreak")[0]
            spans = div.cssselect("div.fBold span")
            try:
                comment.props.date = readDate(spans[1].text_content().split(" ")[1])
            except ValueError:
                comment.props.date = readDate(spans[1].text_content())
            comment.props.author = spans[0].text_content().strip()
            yield comment
            

if __name__ == '__main__':
    from amcat.scripts.tools import cli
    from amcat.tools import amcatlogging
    amcatlogging.debug_module("amcat.scraping.scraper")
    amcatlogging.debug_module("amcat.scraping.document")
    cli.run_cli(WebFDScraper)


