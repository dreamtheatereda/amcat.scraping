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

from amcat.scraping.document import HTMLDocument
from amcat.scraping.scraper import HTTPScraper, DatedScraper
from amcat.tools.toolkit import readDate

class KleineZeitungScraper(HTTPScraper, DatedScraper):
    medium_name = "kleinezeitung.at"
    index_url = "http://kleinezeitung.at/allgemein/sitemap/index.do?date={d.year:04d}{d.month:02d}{d.day:02d}"

    def _get_units(self):
        d = self.options['date']
        for li in self.getdoc(self.index_url.format(**locals())).cssselect("div.su_artikel li"):
            a = li.cssselect("h3 a")[0]
            url = a.get('href')
            urlsplit = url.split("/")[3:-1]
            section = urlsplit[0]
            for word in urlsplit[1:]:
                if re.match('[a-zA-Z]', word):
                    section += " > " + word
                else:
                    externalid = word
            yield HTMLDocument(url = a.get('href'),
                               headline = a.text, 
                               date = readDate(li.cssselect("h3 span")[0].text.split(",")[1].strip(")")),
                               section = section,
                               externalid = externalid)
                               

    def _scrape_unit(self, article):
        article.prepare(self)
        body = article.doc.cssselect("div.article_body")[0]

        [div.drop_tree for div in body.cssselect("div") if div.get('class') and (not div.get('class').startswith("art_foto"))]
        [script.drop_tree() for script in body.cssselect("script")]
        body.cssselect("h1")[0].drop_tree()
        article.props.text = body

        if body.cssselect("em"):
            for em in body.cssselect("em"):
                article.props.author = em.text.startswith("Von ") and em.text.split("Von ")[1]
        if not hasattr(article.props, 'author'):
            article.props.author = body.cssselect("div.author") and body.cssselect("div.author")[0].text
        
        yield article
        
if __name__ == '__main__':
    from amcat.scripts.tools import cli
    from amcat.tools import amcatlogging
    amcatlogging.info_module("amcat.scraping")
    cli.run_cli(KleineZeitungScraper)


