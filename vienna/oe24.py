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
from datetime import datetime

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
                if match and not ("/video/" in url or "/slideshow" in url):
                    section = " > ".join((match.group(2) or "").strip("/").split("/"))
                    yield HTMLDocument(url=url,
                                       externalid = match.group(4) or match.group(5),
                                       section = section
                                       )

    def _scrape_unit(self, article):
        article.prepare(self)
        articletype = 0
        if "xn--sterreich-z7a.at" in article.props.url:
            articletype = 2
        elif "oe24.at" in article.props.url:
            articletype = 1
        
        if articletype == 1:
            datestr = article.doc.cssselect("#storymain div.date")[0].text
            article.props.date = self.extract_date(datestr)
            article.props.headline = article.doc.cssselect("#storymain div.main h1.texttitle")[0].text
            article.props.kicker = article.doc.cssselect("#storymain div.main h2.preTitle")[0].text.strip()
            article.props.byline = article.doc.cssselect("#storymain h3.leadText")[0].text
            article.props.text = [p for p in article.doc.cssselect("#storymain div.bodyText > p") 
                                  if p.text_content().strip()]
        elif articletype == 2:
            datestr = article.doc.cssselect("#page,#Page article span.date")[0].text
            article.props.date = self.extract_date(datestr)
            article.props.headline = article.doc.cssselect("#page,#Page article h1.title")[0].text
            article.props.kicker = article.doc.cssselect("#page,#Page article h2.preTitle")[0].text
            article.props.byline = article.doc.cssselect("#page,#Page article p.leadText")[0].text
            article.props.text = [p for p in article.doc.cssselect("#page,#Page article div.bodyText > p")
                                  if p.text_content().strip()]
        print(article.props.text)
        yield article

    german_months = ["Januar","Februar","März","April","Mai","Juni","Juli","August","September","Oktober","November","Dezember"]
        
    def extract_date(self, datestr):
        for m in self.german_months:
            if m.lower() in datestr.lower():
                month = self.german_months.index(m)
                break
        day = int(datestr.split(".")[0])
        year,time = datestr.lower().split(m.lower())[1].strip().split()
        return datetime(int(year), month+1, day,
                    int(time.split(":")[0]), int(time.split(":")[1]))


if __name__ == '__main__':
    from amcat.scripts.tools import cli
    from amcat.tools import amcatlogging
    amcatlogging.info_module("amcat.scraping")
    cli.run_cli(Oe24Scraper)


