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

from amcat.scraping.document import HTMLDocument
from amcat.scraping.scraper import HTTPScraper, DatedScraper
from amcat.tools.toolkit import readDate

class TTScraper(HTTPScraper, DatedScraper):
    medium_name = "Tiroler Tageszeitung"
    index_url="http://tt.com/tt/rss/tt.xml"

    def _get_units(self):
        index = self.getdoc(self.index_url)
        for item in index.cssselect("item"):
            url = item.cssselect("link")[0].tail
            section = url.split("/")[3]
            for word in url.split("/")[4:-1]:
                section += unicode(re.match('\D+', word) and " > " + word)
                externalid = re.match('[0-9]+\-[0-9]', word) and int(word.split("-")[0])
            article = HTMLDocument(
                url = url,
                headline = item.cssselect("title")[0].text,
                date = readDate(item.cssselect("pubDate")[0].text),
                section = section,
                externalid = externalid)
            if article.props.date.date() == self.options['date']:
                yield article
            elif article.props.date.date() < self.options['date']:
                break

    def _scrape_unit(self, article):
        article.doc = self.getdoc(article.props.url)
        article.props.text = article.doc.cssselect("#content div.text,div.BA_Grundtext")
        yield article

if __name__ == '__main__':
    from amcat.scripts.tools import cli
    from amcat.tools import amcatlogging
    amcatlogging.info_module("amcat.scraping")
    cli.run_cli(TTScraper)


