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

"""A scraper for internet polls on websites of AD, Volkskrant, Telegraaf and Trouw"""

from urlparse import urljoin
from pprint import pformat
from datetime import date
import re

from amcat.scraping.document import HTMLDocument
from amcat.scraping.scraper import HTTPScraper, DatedScraper
from amcat.tools.toolkit import readDate
from amcat.models.medium import Medium


class Volkskrant(HTTPScraper):
    index_url = "http://www.volkskrant.nl/vk/nl/3184/opinie/index.dhtml"

    def __init__(self, *args, **kwargs):
        super(Volkskrant, self).__init__(*args, **kwargs)
        self.medium = "Volkskrant - website"

    def _get_units(self):
        index_doc = self.getdoc(self.index_url)
        poll_script = index_doc.cssselect("div.gen_poll")[0].text_content()
        result_href = re.search("openPollUrl\('ajax_poll[0-9]+', '([^']+)'", poll_script).group(1)
        result_url = urljoin(self.index_url, result_href)
        result_doc = self.getdoc(result_url)
        poll_url = urljoin(self.index_url,result_doc.cssselect("h2.head_de-gedachte a")[0].get('href'))
        poll = HTMLDocument(url = poll_url,
                            externalid = re.search("componentId=([0-9]+)&", result_url).group(1),
                            headline = [tag.text for tag in result_doc.cssselect("body")[0].getchildren()
                                        if not callable(tag.tag) and tag.tag.startswith("h") 
                                        and len(tag.tag) == 2][-1],
                            )
        yield (poll, result_doc)

    def _scrape_unit(self, data):
        poll, result_doc = data
        poll.props.results = {}
        #for each div which contains a div with class 'gen_poll_votes'
        for div in [d for d in result_doc.cssselect("dl div") if 'gen_poll_votes' in [c.get('class') for c in d.getchildren()]]:
            poll.props.results[div.text.strip()] = int(div.cssselect("div.gen_poll_votes strong")[0].text)
        poll.props.results["Totaal"] = int(result_doc.cssselect("dl div.gen_left strong")[0].text)
        poll.props.date = date.today()
        poll.prepare(self)
        #getting urls of related articles rather than articles themselves
        poll.props.related_articles = set([urljoin(poll.props.url, a.get('href')) for a in poll.doc.cssselect("ul.related_box li.v_media a")])
        poll.props.text = pformat(poll.props.results)
        for comment in self.get_comments(poll):
            comment.is_comment = True
            yield comment
        yield poll

    def get_comments(self, poll):
        comment_script = [s for s in poll.doc.cssselect("script") if "listContent" in s.text_content()][0]
        comment_href = re.search("getReactions\('([^']+)'", comment_script.text_content()).group(1)
        comment_doc = self.getdoc(urljoin(poll.props.url, comment_href))
        for div in comment_doc.cssselect("div.reac_box3,div.reac_box3_odd"):
            comment = HTMLDocument(
                parent = poll,
                url = poll.props.url,
                author = div.cssselect("b")[0].text,
                text = div.cssselect("p")[0].text,
                date = readDate(div.cssselect("div.gen_right")[0].text_content()))
            yield comment        


class AD(HTTPScraper):
    index_url = "http://ad.nl"

    def __init__(self, *args, **kwargs):
        super(AD, self).__init__(*args, **kwargs)
        self.medium = "Algemeen Dagblad - website"

    def _get_units(self):
        index_doc = self.getdoc(self.index_url)
        poll_script = index_doc.cssselect("section.poll")[0].text_content()
        results_url = urljoin(self.index_url, poll_script.split("openPollUrl")[1].split("'")[3])
        poll_url = urljoin(self.index_url, poll_script.split("openPollUrl")[2].split("'")[3])
        yield results_url, poll_url, index_doc

    def _scrape_unit(self, urls):
        results_url, poll_url, doc = urls
        result_html = self.getdoc(results_url)
        article = HTMLDocument(url = poll_url)
        article.props.headline = "Poll: " + doc.cssselect("section.poll h3")[0].text_content().strip()
        article.props.results = {}
        for li in result_html.cssselect("ul.poll_content li"):
            article.props.results[li.cssselect("h4")[0].text.strip()] = int(li.cssselect("span.poll_votes")[0].text.strip("()"))
        article.props.results["Total"] = int(result_html.cssselect("p")[0].text.split("Totaal ")[1])
        if doc.cssselect("ul.read_more"):
            article.props.related_articles = [urljoin(self.index_url, a.get('href')) for a in doc.cssselect("ul.read_more li a")]
        yield article

class Telegraaf(HTTPScraper):
    index_url = "http://www.telegraaf.nl/watuzegt/wuz_stelling/"

    def __init__(self, *args, **kwargs):
        super(Telegraaf, self).__init__(*args, **kwargs)
        self.medium = "Telegraaf - website"

    def _get_units(self):
        index = self.getdoc(self.index_url)
        for a in index.cssselect("#element ul.snelnieuws_list li.item a"):
            doc = self.getdoc(a.get('href'))
            date = readDate(doc.cssselect("span.datum")[0].text)
            if date.date() < date.today().date():
                break
            elif date.date() == date.today().date():
                yield a.get('href'), doc

    def _scrape_unit(self, urldoc):
        url, doc = urldoc
        article = HTMLDocument(url = url)
        article.doc = doc
        article.props.images = [self.open(img.get('src')).read() for img in article.doc.cssselect("div.broodMediaBox div.image img")]
        article.props.headline = "Poll:" + doc.cssselect("#artikel h1")[0].text_content().split(":")[1]
        article.props.byline = doc.cssselect("#artikel span.auteur")[0].text
        article.props.date = readDate(doc.cssselect("#artikel span.datum")[0].text)
        article.props.externalid = article.props.url.split("/")[-2]
        article.props.text = doc.cssselect("#artikelKolom div.zaktxt,p")
        article.props.dateline = doc.cssselect("#artikelKolom span.location")[0]
        for comment in self.get_comments(article):
            comment.is_comment = True
            yield comment
        yield article

    def get_comments(self, article):
        from lxml import html
        for div in article.doc.cssselect("#comments div.comment"): 
            comment = HTMLDocument(
                url = article.props.url,
                date = readDate(div.cssselect("div.date")[0].text),
                externalid = int(div.cssselect("div.rate-widget")[0].get('id').split("-")[2]),
                text = div.cssselect("div.wrapper div.username")[0].tail,
                parent = article,
                author = div.cssselect("div.wrapper div.username")[0].text.strip())
            comment.props.thumbsup = int(div.cssselect("div.rate-widget li.thumb-up div.percent")[0].text)
            comment.props.thumbsdown = int(div.cssselect("div.rate-widget li.thumb-down div.percent")[0].text)
            yield comment

class Trouw(Volkskrant):
    index_url = "http://trouw.nl"

    def __init__(self, *args, **kwargs):
        super(Volkskrant, self).__init__(*args, **kwargs)
        self.medium = "Trouw - website"


class PollScraper(HTTPScraper, DatedScraper):
    def _get_units(self):
        scrapers = [
            AD,
            Volkskrant,
            Telegraaf,
            Trouw
            ]
        for s in scrapers:
            s = s(
                project = self.options['project'].id,
                articleset = self.options['articleset'].id
                )
            for unit in s._get_units():
                yield (s, unit)

    def _scrape_unit(self, unit):
        (scraper, unit) = unit
        self.medium_name = scraper.medium
        for article in scraper._scrape_unit(unit):
            if not article.is_comment:
                article.props.medium = Medium.get_or_create(scraper.medium)
            else:
                article.props.medium = Medium.get_or_create(scraper.medium + " - Comments")
            if not hasattr(article.props, 'text'):
                article.props.text = pformat(article.props.results)
            yield article

if __name__ == '__main__':
    from amcat.scripts.tools import cli
    from amcat.tools import amcatlogging
    amcatlogging.info_module("amcat.scraping")
    cli.run_cli(PollScraper)


