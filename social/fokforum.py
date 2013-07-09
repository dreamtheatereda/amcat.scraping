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

from amcat.scraping.scraper import DatedScraper, HTTPScraper
from amcat.scraping.document import HTMLDocument, Document


from datetime import date
from urlparse import urljoin
from amcat.tools.toolkit import readDate
from amcat.models.article import Article
from lxml import html

CATEGORIES_TO_SCRAPE = [
    #('self-determined forum name','forum id as on website'),
    ('nieuws & achtergronden',4),
    ('Politiek',56)
    ]

INDEX_URL = "http://forum.fok.nl"

class FokForumScraper(HTTPScraper, DatedScraper):
    medium_name = "Fok Forum"

    def start(self, *args, **kwargs):
        """opens some urls to make sure all the right headers are in place, 
        don't do this at __init__ for errors may then crash the whole daily scraping process"""

        page = self.open(INDEX_URL)

        cookie_string = page.info()["Set-Cookie"]
        token = cookie_string.split(";")[0]
        self.opener.opener.addheaders.append(("Cookie",token+"; allowallcookies=1"))
        self.open(INDEX_URL)

    def _get_units(self):
        self.start()
        months_back = int((date.today() - self.options['date']).days / 30)

        for forum,forum_id in CATEGORIES_TO_SCRAPE:
            self.current_section = forum
            section_url = urljoin(INDEX_URL,"forum/{fid}".format(fid=forum_id))
            section_doc = self.getdoc(section_url)
            options = section_doc.cssselect("div.pagesholder select.hopforum option")[1:int(months_back / 2.5) + 3]
            for option in options:
                subsection_url = section_url + "/" + option.get('value')

                for topic_url in self.get_topics(subsection_url):
                    yield topic_url
                
    def get_topics(self, subforum):
        doc = self.getdoc(subforum)
        for div in doc.cssselect("div.mb2"):
            table = div.cssselect("table.topiclist_bot")[0]
            for tr in table.cssselect("tr.altcolor-post-1, tr.altcolor-post-2"):
                date = readDate(tr.cssselect("td.tLastreply a")[0].text).date()
                if date >= self.options['date']:
                    if tr.cssselect("td.tOnepage a"):
                        url = urljoin(INDEX_URL, tr.cssselect("td.tOnepage a")[0].get('href'))
                    else:
                        url = urljoin(INDEX_URL, tr.cssselect("td.tTitel a")[0].get('href')) + "/1/999"
                    yield url
                    
                elif date < self.options['date']:
                    break

    def _scrape_unit(self, topic_url):
        #navigate to last page, then navigate back until comments are no longer recent
        doc = self.getdoc(topic_url)
        headline = "".join(doc.cssselect("title")[0].text_content().split("-")[:-1])
        topic_date = readDate(doc.cssselect("span#pt1")[0].text_content().strip())
        try:
            parent = Article.objects.get(headline = headline, date = topic_date)
        except Article.MultipleObjectsReturned: #duplicate in 99.99% of the cases
            parents = Article.objects.filter(headline = headline, date = topic_date)
            min_id = min([parent.id for parent in parents]) #deduplicate usually keeps the lowest id
            parent = parents.get(pk = min_id)
        except Article.DoesNotExist:
            parent = HTMLDocument(url = topic_url)
            parent.props.headline = headline
            parent.props.date = topic_date
            parent.props.text = doc.cssselect("div.postmain_right")[0]
            parent.props.author = doc.cssselect("span.post_sub a.username")[0].text_content().strip()
            parent.props.section = self.current_section
        
        for post in self.get_posts(doc):
            post.props.parent = parent
            post.props.url = hasattr(parent, 'props') and parent.props.url or parent.url
            yield post

        if isinstance(parent, Document):
            yield parent

    def get_posts(self, doc):
        for div in reversed(doc.cssselect("div.post")[1:]):
            date = readDate(div.cssselect("span.post_time")[0].text_content())
            if date.date() == self.options['date']:
                post = HTMLDocument()
                post.props.date = date
                post.props.author = div.cssselect("span.post_sub a.username")[0].text_content()
                post.props.text = div.cssselect("div.postmain_right")[0]
                post.props.section = self.current_section
                yield post
            elif date.date() < self.options['date']:
                break
                                  
    def find_substr(self, start, end, text, include_arguments = True):
        if include_arguments:
            start = text.find(start); end = text.find(end, start) + len(end)
        else:
            start = text.find(start) + len(start); end = text.find(end, start)
        if start != -1 and end != -1:
            return text[start:end]
        else:
            return None


if __name__ == '__main__':
    from amcat.scripts.tools import cli
    from amcat.tools import amcatlogging
    amcatlogging.info_module("amcat.scraping")
    cli.run_cli(FokForumScraper) 



