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

from amcat.scraping.crawler import Crawler
from amcat.scraping.document import HTMLDocument
from amcat.tools.toolkit import readDate
from scraping.newssites.telegraaf import scrape_unit
from datetime import date
import re

class RTLCrawler(Crawler):
    medium_name = "rtl.nl"
    initial_url = "http://www.rtl.nl/actueel/rtlnieuws/home/"
    include_patterns = [
        re.compile("http://www.rtl.nl/actueel/"),
        re.compile("http://www.rtl.nl/components/actueel/")
        ]
    deny_patterns = [
        re.compile("#comments"),
        re.compile("http://www.rtl.nl/components/actueel/rtlnieuws/services/")
        ]

    def article_url(self, url):
        pattern = re.compile("/components/actueel/rtlnieuws/")
        if pattern.search(url):
            return True
        else:
            return False

    def _scrape_unit(self, urldoc):
        article = HTMLDocument(url = urldoc[0])
        article.doc = urldoc[1]
        _date = [
            int(urldoc[0].split("/")[6]),
            int(urldoc[0].split("/")[7].split("_")[0]),
            int(urldoc[0].split("/")[8])]
        article.props.date = date(*_date)
        article.props.section = urldoc[0].split("/")[9]
        article.props.author = article.doc.cssselect("div.fullarticle_tagline")[0].text.split("|")[0]
        article.props.headline = article.doc.cssselect("h1.title")[0].text
        article.props.text = article.doc.cssselect("article")[0]
        yield article

if __name__ == '__main__':
    from amcat.scripts.tools import cli
    from amcat.tools import amcatlogging
    amcatlogging.debug_module("amcat.scraping")
    cli.run_cli(RTLCrawler)


        
