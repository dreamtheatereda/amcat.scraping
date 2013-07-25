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

from urlparse import urljoin
import re

from amcat.scraping.document import HTMLDocument
from amcat.scraping.scraper import HTTPScraper, DatedScraper
from amcat.tools.toolkit import readDate

class Oe24Scraper(HTTPScraper, DatedScraper):
    medium_name = "oe24.at"
    index_url = "http://oe24.at/{category}"


    def _get_units(self):
        for category in ["oesterreich/politik","oesterreich/chronik","welt","umwelt"]:
            index_url = self.index_url.format(**locals()); index_doc = self.getdoc(index_url)
            article_pattern = "(http://[a-z]+.oe24.at/(([a-z]+/)+)[a-zA-Z0-9\-]+/([0-9]+)|http://www.xn--sterreich-z7a.at/nachrichten/[a-zA-Z0-9\-]+/([0-9]+))"
            for url in set([urljoin(index_url, a.get('href')) for a in index_doc.cssselect("a") if a.get('href')]):
                match = re.match(article_pattern.format(**locals()), url)
                if match:
                    section = " > ".join((match.group(2) or "").strip("/").split("/"))
                    yield HTMLDocument(url=url,
                                       externalid = match.group(4) or match.group(5),
                                       section = section
                                       )

    german_months = ["Januar","Februar","März","April","Mai","Juni","Juli","August","September","Oktober","November","Dezember"]


    def _scrape_unit(self, article):
        article.prepare(self)
        doc = (article.doc.cssselect("div.storyBox article") or article.doc.cssselect("div.storybox div.main"))[0]
        datestr = doc.cssselect("article span.date,div.date")[0].text
        for m in self.german_months:
            if m in datestr:
                month = self.german_months.index(m) + 1
                day, yt = [s.strip(" .") for s in datestr.split(m)]
                year, time = yt.split(" ")
        article.props.date = readDate("{year}-{month}-{day} {time}".format(**locals()))
        if article.props.date.date() != self.options['date']:
            return

        article.props.kicker = doc.cssselect("h2.preTitle")[0].text
        article.props.headline = doc.cssselect("h1.title,h1.texttitle")[0].text
        article.props.text = doc.cssselect("article p.leadText") + doc.cssselect("article div.bodyText p")

        yield article

if __name__ == '__main__':
    from amcat.scripts.tools import cli
    from amcat.tools import amcatlogging
    amcatlogging.info_module("amcat.scraping")
    cli.run_cli(Oe24Scraper)


