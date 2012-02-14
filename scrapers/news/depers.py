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

INDEX_URL = "http://www.depers.nl/"

from amcat.tools.scraping.processors import HTTPScraper, CommentScraper, Form
from amcat.tools.scraping.objects import HTMLDocument

from amcat.tools import toolkit
from amcat.models.medium import Medium

from django import forms

from urlparse import urljoin
import datetime

from pprint import pprint
from lxml import etree

class DePersForm(Form):
    date = forms.DateField()

class DePersScraper(HTTPScraper, CommentScraper):
    """ Scrape the news from depers.nl."""
    options_form = DePersForm
    try:
        medium = Medium.objects.get(name="De Pers - news")
    except:
        medium = Medium(name="De Pers - news", language_id=4) #lang=nl
        medium.save()

    def __init__(self, options):
        super(DePersScraper, self).__init__(options)

    def get_categories(self):
        """ Yields the urls to all the pages contianing the categories.
        """
        doc = self.getdoc(INDEX_URL)
        for link in doc.cssselect("div.subtabs ul li a"):
            yield urljoin(INDEX_URL, link.get("href"))

    def init(self):
        for url in self.get_categories():
            day_url = urljoin(url, "%04d%02d%02d.html" % (
                self.options['date'].year,
                self.options['date'].month,
                self.options['date'].day
            ))
            doc = self.getdoc(day_url)
            for article in doc.cssselect("div.1box500 h2 a"):
                yield HTMLDocument(
                    url = urljoin(day_url, article.get("href"),
                    headline = article.text,
                    date = self.options['date']
                ))

    def main(self, doc):
        if doc.doc.cssselect("div.1box440"):
            doc.props.text = doc.doc.cssselect("div.1box440")[0].text_content()
        else:
            doc.props.text = ""
        yield doc

if __name__ == '__main__':
    from amcat.scripts.tools import cli
    cli.run_cli(DePersScraper)
