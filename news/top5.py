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
from amcat.models.medium import get_or_create_medium

from urlparse import urljoin

class Top5Scraper(HTTPScraper):
    #       base url                        path to top5 links
    meta = [['http://www.nrc.nl/',          '.related dd a',                'NRC Handelsblad'],
            ['http://www.volkskrant.nl/',   '#top5 a',                      'De Volkskrant'],
            ['http://www.telegraaf.nl/',    '#rankingTelegraaf2338997 a',   'Telegraaf'],
            ['http://www.trouw.nl/',        '#top5 a',                      'Trouw'],
            ['http://www.nu.nl/',           '.top5 a',                      'Nu.nl']
           ]

    def _get_units(self):
        nrc_index = self.getdoc(self.meta[0][0])
        nrc_page = nrc_index.cssselect('.eerste a')[1].get('href')
        self.meta[0][0] = urljoin(self.meta[0][0], nrc_page)
        for index_url, path, medium in self.meta:
            if 'volkskrant.nl' in index_url:
                index_url = urljoin(index_url, 'vk/nl/2/Home/homepage/right.dhtml')
            elif 'trouw.nl' in index_url:
                index_url = urljoin(index_url, '/tr/nl/4492/Nederland/articleDetail/right.dhtml')
            index = self.getdoc(index_url)
            units = index.cssselect(path)[:5]
            rank = 0
            for article_unit in units:
                article_url = urljoin(index_url, article_unit.get('href'))
                if 'nrc.nl' in index_url or 'nu.nl' in index_url:
                    headline = article_unit.get('title')
                else:
                    headline = article_unit.text
                rank += 1
                site_medium = get_or_create_medium(medium)
                yield HTMLDocument(url=article_url, pagenr=rank, headline=headline, 
                        date=date.today(), medium=site_medium)

    def _scrape_unit(self, article):
        article.prepare(self)
        article.doc = self.getdoc(article.props.url)
        doc = article.doc
        url = article.props.url
        text = ''
        if   'nrc.nl' in url:
            if not article.doc.cssselect(".livebar"):
                article.props.author = doc.cssselect('.author a')[0].text.strip()
            else:
                article.props.author = ", ".join(list(set([a.get('data-author') for a in article.doc.cssselect(".bericht")]))) 
                #above line makes a list of distinct authors seperated by commas
            text = doc.cssselect('.article #broodtekst')[0]
        elif 'volkskrant.nl' in url or 'trouw.nl' in url:
            try:
                article.props.author = doc.cssselect('.author')[0].text.strip()
            except:
                article.props.author = 'ANP'
            
            art = doc.cssselect('#art_box2')[0]
            if "live_art" in art[0].get('class'):
                #find url to the content, because in a live article the content is not loaded on first request but by JS
                script_crap = [" ".join(crap.text) for crap in doc.cssselect("script")]
                start = script_crap.find("function loadAllHighlights()")
                end = script_crap.find(";",start)
                jsfunction = script_crap[start:end]
                start2 = jsfunction.find("url")+8
                end2 = jsfunction.find(";")-2
                href = urljoin(url,jsfunction[start2:end2])
                article.props.text = "\n".join([(li.text_content()) for li in self.getdoc(href).cssselect("ul li")])
            else:
                article.props.text = "\n".join([(p.text_content()) for p in art.cssselect("p")])
            print(article.props.text)
        elif 'telegraaf.nl' in url:
            try:
                article.props.author = doc.cssselect('.auteur')[0].text.strip()
            except:
                article.props.author = ''
            text = doc.cssselect('#artikelKolom')[0]
        elif 'nu.nl' in url:
            article.props.author = doc.cssselect('.smallprint')[0].text.strip()
            text = doc.cssselect('.content')[0]
        if not ('volkskrant.nl' in url or 'trouw.nl' in url):
            suikerhuis = text.cssselect('.kolomRelated') # gerelateerde linkjes
            suikerhuis.extend(text.cssselect('.broodtxt')) # reclame
            suikerhuis.extend(text.cssselect('script'))
            for snoeptrap in suikerhuis:
                snoeptrap.drop_tree()
            article.props.text = text.text_content().strip()
            print(article.props.pagenr)
        yield article

if __name__ == '__main__':
    from amcat.scripts.tools import cli
    from amcat.tools import amcatlogging
    amcatlogging.debug_module("amcat.scraping.scraper")
    amcatlogging.debug_module("amcat.scraping.document")
    cli.run_cli(Top5Scraper)
