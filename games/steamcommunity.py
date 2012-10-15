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

from amcat.scraping.document import Document, HTMLDocument, IndexDocument

#possibly useful imports:

#from urllib import urlencode
from urlparse import urljoin
#from amcat.tools.toolkit import readDate
import json
import math
from lxml import etree
import re
from lxml.html.soupparser import fromstring


INDEX_URL = "http://steamcommunity.com/apps"
FORUM_URL = "http://steamcommunity.com/forum/{f_id}/General/render/0/?start={start}&count=15"

from amcat.scraping.scraper import HTTPScraper,DBScraper,DatedScraper,Scraper

class SteamScraper(HTTPScraper):
    medium_name = "steamcommunity.com"

    def __init__(self, *args, **kwargs):
        super(SteamScraper, self).__init__(*args, **kwargs)

    def _get_units(self):
        index = self.getdoc(INDEX_URL) 
        for unit in index.cssselect('#popular1 a'):
            href = unit.get('href')
            app = self.getdoc(href+"/discussions")
            for html in self.get_pages(app):
                for topic in html.cssselect("div.forum_topic"):
                    a = topic.cssselect("a")[0]
                    title = a.text
                    href = a.get('href')
                    yield HTMLDocument(url=href,headline=title)

    def get_pages(self,first):
        forum_id = first.cssselect("#AppHubContent div.leftcol div.forum_area")[0].get('id').split("_")[2]
        total_topics = int(re.sub(",","",first.cssselect("#forum_General_{}_pagetotal".format(forum_id))[0].text.strip()))
        for x in range(int(math.floor(total_topics/15)+1)):
            page_request = self.open(FORUM_URL.format(f_id=forum_id,start=x*15))
            print(FORUM_URL.format(f_id=forum_id,start=x*15))
            html = fromstring(json.loads(page_request.read())['topics_html'])
            yield html
            
        
    def _scrape_unit(self, topic): 
        topic.doc = self.getdoc(topic.props.url)
        topic.props.text = topic.doc.cssselect("div.forum_op div.content")[0]


if __name__ == '__main__':
    from amcat.scripts.tools import cli
    from amcat.tools import amcatlogging
    amcatlogging.debug_module("amcat.scraping.scraper")
    amcatlogging.debug_module("amcat.scraping.document")
    cli.run_cli(SteamScraper)


