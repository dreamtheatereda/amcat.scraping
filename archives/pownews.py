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

from amcat.scraping.document import Document
from amcat.scraping.scraper import ScraperForm

try:
    from amcatscraping.news.pownews import PownewsScraper
except ImportError:
    from scraping.news.pownews import PownewsScraper

from datetime import date,timedelta

FROMDATE = date(year=2010,month=1,day=1)

class PownewstmpScraper(PownewsScraper):
    options_form = ScraperForm
    
    def _get_units(self):
        self.options['date'] = date.today()
        while self.options['date'] > FROMDATE:
            for unit in super(PownewstmpScraper,self)._get_units():
                yield unit
            self.options['date'] -= timedelta(days=1)



if __name__ == '__main__':
    from amcat.scripts.tools import cli
    from amcat.tools import amcatlogging
    amcatlogging.debug_module("amcat.scraping.scraper")
    amcatlogging.debug_module("amcat.scraping.document")
    cli.run_cli(PownewstmpScraper)

