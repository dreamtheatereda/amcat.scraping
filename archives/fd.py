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

try:
    from scraping.newspapers.fd import FDScraper
except ImportError:
    from amcatscraping.newspapers.fd import FDScraper

from datetime import date,timedelta
from amcat.scraping.scraper import AuthForm,ArchiveForm

class FDForm(AuthForm,ArchiveForm):
    pass


class FDArchiveScraper(FDScraper):
    options_form = FDForm
    def __init__(self,*args,**kwargs):
        super(FDArchiveScraper,self).__init__(*args,**kwargs)
        self.options['date'] = self.options['first_date']

    def _get_units(self):
        while self.options['date'] <= self.options['last_date']:
            self.options['date'] += timedelta(days=1)
            for unit in super(FDArchiveScraper,self)._get_units():
                yield unit



if __name__ == '__main__':
    from amcat.scripts.tools import cli
    from amcat.tools import amcatlogging
    amcatlogging.debug_module("amcat.scraping.scraper")
    amcatlogging.debug_module("amcat.scraping.document")
    cli.run_cli(FDArchiveScraper)
