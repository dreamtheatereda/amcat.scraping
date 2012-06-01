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

from amcat.scraping.scraper import HTTPScraper
from amcat.scraping.document import HTMLDocument 
from datetime import date

from urlparse import urljoin

class Top5Scraper(HTTPScraper):
    medium_name = "Top5Scraper"
    #       base url                        path to top5 links
    meta = [['http://www.nrc.nl/',          '.related dd a'],
            ['http://www.volkskrant.nl/',   '#top5 a'],
            ['http://www.telegraaf.nl/',    '#rankingTelegraaf2338997 a'],
            ['http://www.trouw.nl/',        '#top5 a'],
            ['http://www.nu.nl/',           '.top5 a']
           ]

    def _get_units(self):
        nrc_index = self.getdoc(self.meta[0][0])
        nrc_page = nrc_index.cssselect('.eerste a')[1].get('href')
        self.meta[0][0] = urljoin(self.meta[0][0], nrc_page)
        for index_url, path in self.meta:
            if 'volkskrant.nl' in index_url:
                index_url = urljoin(index_url, 'vk/nl/2/Home/homepage/right.dhtml')
            elif 'trouw.nl' in index_url:
                index_url = urljoin(index_url, '/tr/nl/4492/Nederland/articleDetail/right.dhtml')
            index = self.getdoc(index_url)
            units = index.cssselect(path)[:5]
            for article_unit in units:
                article_url = urljoin(index_url, article_unit.get('href'))
                print(article_url)
                yield HTMLDocument(url=article_url, headline=article_unit.text, date=date.today())

    def _scrape_unit(self, article):
        """gets articles from an index page"""
        article.prepare(self)
        article.doc = self.getdoc(article.props.url)
        doc = article.doc
        #print( 'url      :' + article.props.url )
        if   'nrc.nl' in article.props.url:
            article.author = doc.cssselect('.author a')[0].text.strip()
            article.text = doc.cssselect('.article #broodtekst')[0].text_content().strip()
        elif 'volkskrant.nl' in article.props.url or 'trouw.nl' in article.props.url:
            article.author = doc.cssselect('.author')[0].text.strip()
            ps = doc.cssselect('.art_box2 p')
            article.text = ps[0].text_content()+ps[1].text_content().strip()
        elif 'telegraaf.nl' in article.props.url:
            try:
                article.author = doc.cssselect('.auteur')[0].text.strip()
            except:
                article.author = ''
            article.text = doc.cssselect('#artikelKolom')[0].text_content().strip()
        elif 'nu.nl' in article.props.url:
            article.author = doc.cssselect('.smallprint')[0].text.strip()
            article.text = doc.cssselect('.content')[0].text_content().strip()
        #print( 'text     :' + repr(article.text[:50] ))
        #print( 'author   :' + repr(article.author))
        yield article

if __name__ == '__main__':
    from amcat.scripts.tools import cli
    from amcat.tools import amcatlogging
    amcatlogging.debug_module("amcat.scraping.scraper")
    amcatlogging.debug_module("amcat.scraping.document")
    cli.run_cli(Top5Scraper)
