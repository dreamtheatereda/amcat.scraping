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
        
def adhocDateFix(datestring):
    datestring = datestring.replace('-02-31','-03-03').replace('-02-30','-03-02').replace('20090', '2009')
    return datestring


class KamerstukkenScraper(OfficieleBekendmakingenScraper):
    doctypelist = ['kamerstuk']
    
    def _scrape_unit(self, url):
        try: xml = self.getdoc(url)
        except: return

        url = url.replace('.xml','.html')
        metadict = self.getMetaDict(xml, printit=False)
        
        try: kamerwrk = xml.cssselect('kamerwrk')[0].getchildren()
        except: return []
        #print(kamerwrk)
        headtags = [headtag.tag for headtag in kamerwrk]

        if 'wet' in headtags: return []
        if 'blwstuk' in headtags: return []
        for bodypart in xml.cssselect('stuk')[0].getchildren():
            if bodypart.tag == 'titel':
                if bodypart.text == None: return []
                if not 'amendement' in bodypart.text.lower(): return []
                
                for titelpart in bodypart.getchildren():
                    print(titelpart.tag)
        
        
        if len(metadict) == 0:
            log.warn("NO METADATA FOR %s. SKIPPING URL" % url)
            return

        section = self.safeMetaGet(metadict,'OVERHEID.category')
        document_id = metadict['DC.identifier']
        author = self.safeMetaGet(metadict,'OVERHEIDop.indiener')
        try: archieftype = metadict['OVERHEIDop.ArchiefType']
        except: archieftype = metadict['DC.type']
        aanleiding = metadict['DC.title']

        headline = ("%s | %s - %s" % (document_id, archieftype, author)).strip()
        try: datestring = adhocDateFix(metadict['DCTERMS.issued'])
        except:
            datestring = adhocDateFix(metadict['OVERHEIDop.datumOntvangst'])
            headline += " (publicatiedatum)"

        try: date = datetime.datetime.strptime(datestring, '%Y-%m-%d')
        except: date = datetime.datetime.strptime(datestring, '%d-%m-%Y')

        
        #yield Article(headline=headline, byline=vraagnummer, text=body, date=date, section=section, url=url)
                
        return []

if __name__ == '__main__':
    from amcat.scripts.tools import cli
    from amcat.tools import amcatlogging
    amcatlogging.debug_module("amcat.scraping.scraper")
    amcatlogging.debug_module("amcat.scraping.document")
    cli.run_cli(KamerstukkenScraper)


