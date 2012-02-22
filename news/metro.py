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

INDEX_URL = "http://www.metronieuws.nl/"

from amcat.tools.scraping.processors import HTTPScraper, CommentScraper, Form
from amcat.tools.scraping.objects import HTMLDocument

from amcat.tools import toolkit
from amcat.models.medium import Medium

from urlparse import urljoin
import datetime

from pprint import pprint
from lxml import etree

class MetroForm(Form):
    #date = forms.DateField()
    pass

class MetroScraper(HTTPScraper, CommentScraper):
    """ Scrape the tweets from ikregeer.nl."""
    options_form = MetroForm
    try:
        medium = Medium.objects.get(name="Metro - news")
    except:
        medium = Medium(name="Metro - news", language_id=4) #lang=nl
        medium.save()

    def __init__(self, options):
        super(MetroScraper, self).__init__(options)

    def get_categories(self):
        """ Yields the urls to all the pages contianing the categories.
        """
        doc = self.getdoc(INDEX_URL)
        for link in doc.cssselect("ul.primary-nav.drop li a"):
            yield urljoin(INDEX_URL, link.get("href"))

    def init(self):
        for url in self.get_categories():
            doc = self.getdoc(url)
            for article in doc.cssselect("h4.title a"):
                yield HTMLDocument(url=urljoin(INDEX_URL, article.get("href")))

    def main(self, doc):
        if not doc.doc.cssselect("h1.title"):
            doc.props.headline = doc.doc.xpath("/html/head/title")[0].text
        else:
            doc.props.headline = doc.doc.cssselect("h1.title")[0].text
        doc.props.date = datetime.datetime.strptime(
            doc.doc.xpath("/html/head/meta[@name='date']")[0].get("content"),
            "%Y-%m-%d")
        doc.props.text = "".join([
            d.text_content() for d in doc.doc.cssselect("div.article-body")])
        yield doc

if __name__ == '__main__':
    from amcat.scripts.tools import cli
    cli.run_cli(MetroScraper)
