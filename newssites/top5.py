
# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
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
from amcat.scraping.htmltools import create_cc_cookies
from datetime import date
from amcat.models.medium import Medium

from urlparse import urljoin
from amcat.tools.toolkit import readDate
import re


class NRC(HTTPScraper):
    index_url = "http://www.nrc.nl"
    source = 'NRC - website'

    def __init__(self, *args, **kwargs):
        super(NRC, self).__init__(*args, **kwargs)
        self.index_url = urljoin(self.index_url, self.getdoc(self.index_url).cssselect("div.watskeburt h2 a")[0].get('href'))
        
    def _get_units(self):
        doc = self.getdoc(self.index_url)
        div = doc.cssselect("div.related")[0]
        if div.cssselect("div.retentie"):
            div.cssselect("div.retentie")[0].drop_tree()
        for dl in div.cssselect("dl"):
            article = HTMLDocument()
            article.props.url = urljoin(self.index_url, dl.cssselect("a")[0].get('href'))
            article.props.headline = dl.cssselect("span.title-words")[0].text_content().strip()
            article.props.date = readDate(dl.cssselect("dt.tijd time")[0].get('datetime'))
            yield article

    def _scrape_unit(self, article):
        article.prepare(self)
        if article.doc.cssselect("div.author"):
            article.props.author = article.doc.cssselect("div.author")[0].text_content().lstrip("dor")
        article.props.text = article.doc.cssselect("#broodtekst")[0]
        yield article


class Volkskrant(HTTPScraper):
    index_url = "http://www.volkskrant.nl/vk/nl/2/Home/homepage/right.dhtml"
    cookie_url = "http://www.volkskrant.nl/?utm_source=scherm1&utm_medium=button&utm_campaign=Cookiecheck"
    source = 'Volkskrant - website'
    domain = '.volkskrant.nl'

    def _set_cookies(self):
        for cookie in create_cc_cookies(self.domain):
            self.opener.cookiejar.set_cookie(cookie)

    def _get_units(self):
        self._set_cookies()

        doc = self.getdoc(self.index_url)
        for a in doc.cssselect("#top5 li a"):
            url = urljoin(self.cookie_url, a.get('href'))
            yield url

    def _scrape_unit(self, url):
        article = HTMLDocument(url = url)
        article.prepare(self)
        article.props.headline = article.doc.cssselect("#articleDetailTitle")[0].text_content()
        time_post = article.doc.cssselect("div.time_post")[0]
        if time_post.cssselect("span.author"):
            article.props.author = time_post.cssselect("span.author")[0].text_content().lstrip("Dor:")
            time_post.cssselect("span.author")[0].drop_tree()
        article.props.date = readDate(time_post.text_content())
        article.props.text = article.doc.cssselect("#art_box2")[0]
        yield article

class Trouw(Volkskrant):
    source = 'Trouw - website'
    cookie_url = 'http://www.trouw.nl/?utm_source=scherm1&utm_medium=button&utm_campaign=Cookiecheck'
    index_url = "http://www.trouw.nl/tr/nl/15/Home/homepage/right.dhtml"
    domain = '.trouw.nl'


class Telegraaf(HTTPScraper):
    index_url = "http://www.telegraaf.nl/"
    source = 'Telegraaf - website'
    def _get_units(self):
        doc = self.getdoc(self.index_url)
        for a in doc.cssselect("div.meestgelezenwidget div.pad5")[0].cssselect("div.item a"):
            yield a.get('href')

    def _scrape_unit(self, url):
        article = HTMLDocument(url = url)
        article.prepare(self)
        article.props.date = readDate(article.doc.cssselect("#artikel span.datum")[0].text_content())
        article.props.headline = article.doc.cssselect("#artikel h1")[0].text_content()
        author = article.doc.cssselect("#artikel span.auteur")
        if author:
            article.props.author = author[0].text_content()
        [s.drop_tree() for s in article.doc.cssselect("#artikelKolom script")]
        article.props.text = article.doc.cssselect("#artikelKolom")[0]
        yield article
    

class Nu(HTTPScraper):
    source = 'nu.nl - website'
    index_url = 'http://www.nu.nl'
    
    def _get_units(self):
        for a in self.getdoc(self.index_url).cssselect(".top5 a")[:5]:
            yield urljoin(self.index_url, a.get('href'))

    def _scrape_unit(self, url):
        article = HTMLDocument(url = url)
        article.prepare(self)
        article.props.date = readDate(article.doc.cssselect("div.dateplace-data")[0].text)
        article.props.headline = article.doc.cssselect("h1")[0].text_content().strip()
        [s.drop_tree() for s in article.doc.cssselect("script")]
        article.props.text = article.doc.cssselect("#leadarticle div.content")[0]
        author = article.doc.cssselect("#leadarticle span.smallprint")
        if author:
            article.props.author = author[0].text.strip("| ")
        yield article

class AD(HTTPScraper):
    source = 'Algemeen Dagblad - website'
    index_url = 'http://www.ad.nl'

    def _get_units(self):
        doc = self.getdoc(self.index_url)
        for a in doc.cssselect('#hdr_hvdn_top_list a'):
            href = a.get('href')
            yield urljoin(self.index_url, href)

    def _scrape_unit(self, url):
        article = HTMLDocument(url=url)
        article.prepare(self)
        authordate = article.doc.cssselect('span.author')[0].text_content()
        
        p = "((Bewerkt door)|(Door)):?( |\n)([A-Za-z0-9 ]+)\n\n(([0-9]{1,2}\-){2}[0-9]{1,2})"
        pattern = re.compile(p)
        match = pattern.search(authordate.strip())
        article.props.author = match.group(5)
        article.props.date = readDate(match.group(6))
        try:
            article.props.source = authordate.split("bron:")[1].strip()
        except IndexError:
            pass
        article.props.text = article.doc.cssselect("section#detail_content p.intro,section.clear")
        article.props.headline = article.doc.cssselect("h1")[0].text

        yield article
            

class Top5Scraper(HTTPScraper):
    

    def _get_units(self):
        self.open("http://www.volkskrant.nl")
        self.scrapers = [
                Telegraaf,
                Volkskrant,
                Nu,
                Trouw,
                NRC,
                AD
            ]

        for scraper in self.scrapers:
            scraper = scraper(
                project = self.options['project'].id,
                articleset = self.options['articleset'].id
                )
            rank = 0
            for unit in scraper._get_units():
                rank += 1
                yield (scraper, unit, rank)

    def _scrape_unit(self, unit):
        (scraper, unit, rank) = unit
        for article in scraper._scrape_unit(unit):
            article.props.medium = Medium.get_or_create(scraper.source)
            article.props.rank = rank
            for attr in ['headline', 'author', 'text']:
                if hasattr(article.props, attr):

                    value = getattr(article.props, attr)
                    if isinstance(value, str) or isinstance(value, unicode):
                        value = value.strip()
                    setattr(article.props, attr, value)
            yield article

if __name__ == '__main__':
    from amcat.scripts.tools import cli
    from amcat.tools import amcatlogging
    amcatlogging.debug_module("amcat.scraping.scraper")
    amcatlogging.debug_module("amcat.scraping.document")
    cli.run_cli(Top5Scraper)


