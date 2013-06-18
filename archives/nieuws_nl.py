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

from scraping.news.nieuws_nl import Nieuws_nlScraper
from amcat.scraping.scraper import ArchiveForm
from lxml import html
from datetime import timedelta
import json

class Nieuws_nlArchiveScraper(Nieuws_nlScraper):
    options_form = ArchiveForm

    def __init__(self, *args, **kwargs):
        super(Nieuws_nlArchiveScraper, self).__init__(*args, **kwargs)
        day_difference = self.options['last_date'] - self.options['first_date']
        self.dates = [self.options['first_date'] + timedelta(days = x) for x in range(day_difference.days)]
        self.options['date'] = self.options['last_date']
    def get_articles(self, category_url):
        page_doc = self.getdoc(category_url)
        data_after = page_doc.cssselect("#nextPage")
        if not data_after:
            for a, _date in self.scrape_page(page_doc):
                if _date.date() in self.dates:
                    yield a, _date
        else:
            data_after = data_after[0].get('data-after')
            while True:
                br = False
                print
                for a, _date in self.scrape_page(page_doc):
                    if _date.date() in self.dates:
                        yield a, _date
                    elif _date.date() < self.dates[0]:
                        br = True
                        break
                if br:
                    break
                try:
                    data_after = page_doc.cssselect("#nextPage")[0].get('data-after')
                except IndexError:
                    break
                page_doc = json.loads(self.open(self.page_url.format(**locals())).read())
                page_doc = html.fromstring(page_doc['content']['div#nextPage'])

if __name__ == "__main__":
    from amcat.scripts.tools import cli
    from amcat.tools import amcatlogging
    amcatlogging.info_module("amcat.scraping")
    cli.run_cli(Nieuws_nlArchiveScraper)
