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


from amcat.scraping.scraper import ScraperForm

try:
    from scraping.blogs.geenstijl import GeenstijlScraper
except ImportError:
    from amcatscraping.blogs.geenstijl import GeenstijlScraper

from datetime import date,timedelta

FROM_DATE = date(year=2012,month=01,day=01)

class GeenstijlArchiveScraper(GeenstijlScraper):
    options_form = ScraperForm
    
    def _get_units(self):
        self.options['date'] = date.today()
        while self.options['date'] >= FROM_DATE:
            for unit in super(GeenstijlArchiveScraper,self)._get_units():
                yield unit
            self.options['date'] -= timedelta(days=1)



if __name__ == '__main__':
    from amcat.scripts.tools import cli
    from amcat.tools import amcatlogging
    amcatlogging.debug_module("amcat.scraping.scraper")
    amcatlogging.debug_module("amcat.scraping.document")
    cli.run_cli(GeenstijlArchiveScraper)
