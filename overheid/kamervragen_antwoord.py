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
        
class KamervragenAntwoordScraper(OfficieleBekendmakingenScraper):
    doctypelist = ['kamervragen_aanhangsel']
    medium_name ="antwoord op kamervraag"

    def getAntwoord(self, bodypart, xml):
        nr = bodypart.find('nummer')
        if nr == None: nr = bodypart.find('nr')
        
        vraag = ' '.join([al.text_content().replace('\n', ' ').replace('\r','').strip() for al in bodypart.cssselect('al')])
        for nootref in bodypart.cssselect('nootref'):
            vraag += " (Noot %s)" % self.traceNootRefNr(nootref, xml)

        if nr:
            nr = nr.text_content().replace('Antwoord', '').strip()
            return "Antwoord %s:\n%s" % (nr, vraag)
        else:
            return vraag

    def getBody(self, xml):
        body = ''
        notesdict = self.getNotesDict(xml, printit=False)

        if len(xml.cssselect('reactie')) > 0: bodyparts = xml.cssselect('reactie')[0].getchildren() 
        elif len(xml.cssselect('kamervragen')) > 0: bodyparts = xml.cssselect('kamervragen')[0].getchildren()
        else: bodyparts = xml.cssselect('body')[0].getchildren()
        

        for bodypart in bodyparts:
            if bodypart.tag in ['omschr', 'kamervraagomschrijving']:               
                body += bodypart.text_content().replace('\n',' ').replace('\r','').strip() + '\n'
            elif bodypart.tag == 'antwoord':
                body += "\n%s\n" % self.getAntwoord(bodypart, xml)
            elif bodypart.tag in ['toelicht']:
                body += '\n' + bodypart.text_content().replace('\n',' ').replace('\r','').replace('Toelichting:', 'Toelichting:\n') + '\n'
            elif bodypart.tag == 'al': body += '\n' + bodypart.text_content().replace('\n',' ').replace('\r','') + '\n'
            elif bodypart.tag == 'kamervraagopmerking': body += '\n' + bodypart.text_content().replace('\n',' ').replace('\r','').replace('Mededeling','\n') + '\n'
            elif bodypart.tag in ['titel','vraagnummer','noot','kamervraagkop','kamervraagnummer','vraag']: None
            else:
                log.warn("Unused <reactie> element: %s" % bodypart)
                
        for nr in sorted(notesdict):
            noteref1, noteref2, noteref3 = "%s%s" % (nr, notesdict[nr]), "%s %s" % (nr, notesdict[nr]), "%s  %s" % (nr, notesdict[nr])
            if notesdict[nr] in body: body = body.replace(noteref1, ' (Noot %s)' % nr).replace(noteref2, ' (Noot %s)' % nr).replace(noteref3, ' (Noot %s)' % nr)
            if "(Noot %s)" % nr in body: body += "\nNoot %s: %s" % (nr, notesdict[nr])
            else: body += "\nNoot %s (alleen in vraag): %s" % (nr, notesdict[nr])
                        
        return body
     
    def _scrape_unit(self, url):
        try: xml = self.getdoc(url)
        except:
            log.warn("COULD NOT FIND XML FOR %s" % url) 
            return
   
        url = url.replace('.xml','.html')
        metadict = self.getMetaDict(xml, printit=False)

        if len(metadict) == 0:
            log.warn("NO METADATA FOR %s. SKIPPING URL" % url) 
            return

        section = self.safeMetaGet(metadict,'OVERHEID.category')
        document_id = metadict['DC.identifier']
        author = self.safeMetaGet(metadict,'OVERHEIDop.ontvanger')
        try: archieftype = metadict['OVERHEIDop.ArchiefType']
        except: archieftype = metadict['DC.type']
        aanleiding = metadict['DC.title']
        try: vraagnummer = metadict['OVERHEIDop.vraagnummer'].strip()
        except: vraagnummer = self.safeMetaGet(metadict,'OVERHEIDop.vraagNummer').strip()

        headline = ("%s | %s - %s" % (document_id, archieftype, vraagnummer)).strip()
        try: datestring = adhocDateFix(metadict['OVERHEIDop.datumOntvangst'])
        except:
            datestring = adhocDateFix(metadict['OVERHEIDop.datumIndiening'])
            headline += " (publicatiedatum)"
            
        try: date = datetime.datetime.strptime(datestring, '%Y-%m-%d')
        except: date = datetime.datetime.strptime(datestring, '%d-%m-%Y')
        
        body = "%s\n\n%s" % (aanleiding, self.getBody(xml))
           
        #print('--------------\n', headline, '\n', body, '\n\n') 
        yield Article(headline=headline, byline=vraagnummer, text=body, date=date, section=section, url=url)
        #return []

if __name__ == '__main__':
    from amcat.scripts.tools import cli
    from amcat.tools import amcatlogging
    amcatlogging.debug_module("amcat.scraping.scraper")
    amcatlogging.debug_module("amcat.scraping.document")
    cli.run_cli(KamervragenAntwoordScraper)


