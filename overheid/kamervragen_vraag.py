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

def adhocDatefix(datestring):
    datestring = datestring.replace('-02-31','-03-03').replace('-02-30','-03-02').replace('20090', '2009')
    return datestring
        
class KamervragenVraagScraper(OfficieleBekendmakingenScraper):
    doctypelist = ['kamervragen_zonder_antwoord']
    medium_name = "Kamervraag"

    def getVraag(self, bodypart, xml):
        try: nr = bodypart.find('nummer').text_content()
        except: nr = bodypart.find('nr').text_content()
        nr = nr.replace('Vraag', '').strip()
            
        vraag = ' '.join([al.text_content().replace('\n', ' ').replace('\r','').strip() for al in bodypart.cssselect('al')])
        for nootref in bodypart.cssselect('nootref'):
            vraag += " (Noot %s)" % self.traceNootRefNr(nootref, xml)
        return "Vraag %s:\n%s" % (nr, vraag)

    def getBody(self, xml):
        body = ''
        notesdict = self.getNotesDict(xml, printit=False)
    
        try: bodyparts = xml.cssselect('vragen')[0].getchildren() # alternatives for different notation styles
        except: bodyparts = xml.cssselect('kamervragen')[0].getchildren()

        for bodypart in bodyparts:
            if bodypart.tag in ['omschr', 'kamervraagomschrijving']:               
                body += bodypart.text_content().replace('\n',' ').replace('\r','') + '\n'
            elif bodypart.tag == 'vraag':
                body += "\n%s\n" % self.getVraag(bodypart, xml)
            elif bodypart.tag in ['toelicht']:
                body += '\n' + bodypart.text_content().replace('\n',' ').replace('\r','').replace('Toelichting:', 'Toelichting:\n') + '\n'
            elif bodypart.tag in ['vraagnummer','noot','kamervraagkop','kamervraagnummer']: None
            else:
                print('\n\n\n\n',bodypart)
                
        for nr in sorted(notesdict):
            noteref1, noteref2, noteref3 = "%s%s" % (nr, notesdict[nr]), "%s %s" % (nr, notesdict[nr]), "%s  %s" % (nr, notesdict[nr])
            if notesdict[nr] in body: body = body.replace(noteref1, ' (Noot %s)' % nr).replace(noteref2, ' (Noot %s)' % nr).replace(noteref3, ' (Noot %s)' % nr)
            body += "\nNoot %s: %s" % (nr, notesdict[nr])
                        
        return body
            
    def _scrape_unit(self, url):
        try: xml = self.getdoc(url)
        except:
            log.warn("COULD NOT FIND XML FOR %s" % url) 
            return
           
        url = url.replace('.xml','.html')
        metadict = self.getMetaDict(xml, printit=False)

        datestring = adhocDatefix(metadict['OVERHEIDop.datumIndiening'])
        date = datetime.datetime.strptime(datestring, '%Y-%m-%d')
        
        section = self.safeMetaGet(metadict,'OVERHEID.category')
        document_id = metadict['DC.identifier'].strip()
        author = self.safeMetaGet(metadict,'OVERHEIDop.indiener')
        typevraag = metadict['DC.type']

        body = self.getBody(xml)
        headline = "document_id (%s)" % author
        #print('--------------\n', document_id, typevraag, '\n', body, '\n\n') 
       
        yield Article(headline=document_id, byline=typevraag, text=body, date=date, section=section, url=url)
        #return []


if __name__ == '__main__':
    from amcat.scripts.tools import cli
    from amcat.tools import amcatlogging
    amcatlogging.debug_module("amcat.scraping.scraper")
    amcatlogging.debug_module("amcat.scraping.document")
    cli.run_cli(KamervragenVraagScraper)


