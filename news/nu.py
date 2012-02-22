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

from amcat.tools.scraping.processors import GoogleScraper, Form
from amcat.tools.scraping.objects import HTMLDocument
from amcat.tools.scraping import toolkit as stoolkit

from amcat.tools import toolkit
from amcat.models.medium import Medium

from django import forms

import urllib2
import logging
log = logging.getLogger(__name__)

BASE_URL = "http://www.nu.nl/"
INDEX_URL = BASE_URL + "%(cat)s/%(id)s"

ILLEGAL_URLS = ["http://mobiel.nu.nl/",
                "http://www.nu.nl/tvgids/",
                "http://iphone.nu.nl/",
                "http://www.mobiel.nu.nl",
                "http://mobi.nu.nl/",
                "http://m.nu.nl/"]

MONTHS = [
    'januari',
    'februari',
    'maart',
    'april',
    'mei',
    'juni',
    'juli',
    'augustus',
    'september',
    'oktober',
    'novembter',
    'december'
]

COMMENTS_PER_NUJIJ_PAGE = 200

class NuForm(Form):
    date = forms.DateField()

class NuScraper(GoogleScraper):
    options_form = NuForm
    medium = Medium.objects.get(name="nu.nl - website")

    def __init__(self, options):
        super(NuScraper, self).__init__(options, domain='nu.nl')

    def formatterm(self, date):
        return "%(day)s %(month)s %(year)s" % dict(
            day=date.day, month=MONTHS[date.month-1],
            year=date.year)

    def get(self, art):
        # Also get comments. Not using CommentScraper because of
        # GoogleScraper (both alter init).
        for a in self._get(art):
            yield a

            comm = art.copy(parent=art)
            for b in self.comments(comm):
                yield b 

    def _get(self, art):
        if not art.props.url.startswith(BASE_URL):
            return []

        for url in ILLEGAL_URLS:
            if art.props.url.startswith(url):
                # URL not allowed
                return []

        datetime = art.doc.cssselect('a.infolink')[0].get('title')
        datetime = toolkit.readDate(datetime)

        if datetime.date() != self.options['date']:
            # Google api can return false positives
            return []

        # Delete elements not relevant to content
        for el in ('#photo', '.diablockv1', '.articlebodyad'):
            try:
                art.doc.cssselect(el)[0].drop_tree()
            except:
                pass

        # Add properties
        art.props.date = datetime
        art.props.headline = art.doc.cssselect('.header h1')[0].text_content()
        art.props.text = art.doc.cssselect('.content')[0]
        art.props.category = art.props.url.split('/')[3]

        return [art,]

    def comments(self, art):
        # Search nujij reference
        nujij = art.doc.cssselect('iframe.NUjijButton')

        if not nujij:
            log.warn("NuJij button not found for %s" % art.props.url)
        else:
            nujij = nujij[0].get('src')
            nujij = self.getdoc(nujij).cssselect('a')[0].get('href')

            # Loop through all comment pages
            i = 0
            while i < 2:
                startnr = (COMMENTS_PER_NUJIJ_PAGE * i) + 1
                doc = self.getdoc(nujij + '?pageStart=%s' % startnr)

                comments = doc.cssselect('ol.reacties')
                if not len(comments):
                    # Article not yet made
                    break
                
                if not len(comments[0].cssselect('.reactie-body')):
                    # No more comments
                    break

                for comment in comments[0].cssselect('ol > li'):
                    kop = comment.cssselect('.reactie-kop')[0]

                    try:
                        minus, plus = kop.cssselect('.reactie-saldo')
                    except ValueError:
                        # Comment deleted by moderator
                        continue

                    comm = art.copy()
                    comm.props.reply_score_minus = minus.text_content()
                    comm.props.reply_score_plus = plus.text_content()
                    comm.props.author = kop.cssselect('strong a')[0].text
                    comm.props.text = comment.cssselect('.reactie-body')[0]

                    date = kop.cssselect('.tijdsverschil')[0].get('publicationdate')
                    comm.props.date = toolkit.readDate(date)

                    yield comm

                i += 1

if __name__ == '__main__':
    from amcat.scripts.tools import cli
    cli.run_cli(NuScraper)
