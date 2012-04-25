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

from amcat.scraping.scraper import DatedScraper, HTTPScraper
from amcat.scraping.document import HTMLDocument
from amcat.models.article import Article
from amcat.tools import toolkit
from amcat.models.medium import get_or_create_medium
        
INDEXURL = "%s/actueel/1/%s"
BASEURL = "https://zoek.officielebekendmakingen.nl/%s"

DOCTYPELIST = ['kamerstuk','handelingen','kamervragen_zonder_antwoord', 'kamervragen_aanhangsel','agenda','niet_dossierstuk']
DOCTYPELIST = ['kamervragen_zonder_antwoord']

            
class OfficieleBekendmakingenScraper(DatedScraper, HTTPScraper):
    
    def _get_units(self):
        for page in self.get_pages():
            doc = self.getdoc(page)
            for arturl in set(a.get('href') for a in doc.cssselect('div.lijst > ul > li > a')):
                arturl = BASEURL % arturl
                yield(arturl.replace('html','xml'))
 
    def get_pages(self):
        for doctype in DOCTYPELIST:
            url = INDEXURL % (doctype, self.options['date'].strftime('%d%m%Y'))
            doc = self.getdoc(BASEURL % url)
            
            pages = set(p.get('href') for p in doc.cssselect('div."paginering boven" > a'))
            pages.add(url)
            for page in pages:
                yield BASEURL % page

    def _scrape_unit(self, url):
        xml = self.getdoc(url)
        notedict = dict((noot.get('nr'),noot.text_content()) for noot in (xml.cssselect('noot')))
        metadict = dict((meta.get('name'), meta.get('content')) for meta in xml.cssselect('meta'))
        
        print('\nNOTES:')
        for note in notedict:
            print(note, ': ', notedict[note])
        print('\nMETA:')
        for meta in metadict:
            print(meta, ': ', metadict[meta])
        # DIFFERENT _SCRAPE_UNIT() REQUIRED FOR DIFFERENT DOCTYPES. MAKE SUBCLASSES FOR DOCTYPES  
        sys.exit()
        return []


if __name__ == '__main__':
    from amcat.scripts.tools import cli
    from amcat.tools import amcatlogging
    amcatlogging.debug_module("amcat.scraping.scraper")
    amcatlogging.debug_module("amcat.scraping.document")
    cli.run_cli(OfficieleBekendmakingenScraper)


