 #!/usr/bin/python
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

from __future__ import unicode_literals, print_function, absolute_import

import datetime, sys, urllib, urllib2, re
    
import logging
log = logging.getLogger(__name__)

from officiele_bekendmakingen import OfficieleBekendmakingenScraper

from amcat.scraping.scraper import DatedScraper, HTTPScraper
from amcat.scraping.document import HTMLDocument
from amcat.models.article import Article
from amcat.tools import toolkit
from amcat.models.medium import get_or_create_medium
        
class HandelingenPerSprekerScraper(OfficieleBekendmakingenScraper):
    doctypelist = ['handelingen']

    def _scrape_unit(self, url):
        print(url.replace('.xml','.html'))
        xml = self.getdoc(url)
        metadict = self.getMetaDict(xml, printit=False)
        
        headline = metadict['DC.title']
        external_id = metadict['DC.identifier']
        date = datetime.datetime.strptime(metadict['OVERHEIDop.datumVergadering'], '%d-%m-%Y')
        section = metadict['OVERHEID.category']

        

        for line in self.sprekerDictReader(xml):
            line
            
        #sys.exit()
        return []


if __name__ == '__main__':
    from amcat.scripts.tools import cli
    from amcat.tools import amcatlogging
    amcatlogging.debug_module("amcat.scraping.scraper")
    amcatlogging.debug_module("amcat.scraping.document")
    cli.run_cli(HandelingenPerSprekerScraper)


