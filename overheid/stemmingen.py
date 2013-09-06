
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
        
class StemmingenScraper(OfficieleBekendmakingenScraper):
    doctypelist = ['handelingen']
    medium_name = "Stemmingen"

    def _scrape_unit(self, url):
        try: xml = self.getdoc(url)
        except: return
        
        url = url.replace('.xml','.html')
        
        metadict = self.getMetaDict(xml, printit=False)
        if len(metadict) == 0:
            log.warn("NO METADATA FOR %s. SKIPPING URL" % url) 
            return
            
        try: itemnaam = xml.cssselect('itemnaam')[0].text_content()
        except: itemnaam = ''

        datestring = metadict['OVERHEIDop.datumVergadering']
        try: date = datetime.datetime.strptime(datestring, '%d-%m-%Y')
        except: date = datetime.datetime.strptime(datestring, '%Y-%m-%d')
        section = self.safeMetaGet(metadict,'OVERHEID.category')
        document_id = metadict['DC.identifier']
   
        try: omschrijving = xml.cssselect('itemkop')[0].text_content()
        except:
            try: omschrijving = xml.cssselect('onderwerp')[0].text_content()
            except: omschrijving = metadict['DC.title']

        #metabody = '\n'.join(["%s:\t%s;" % (meta, metadict[meta]) for meta in metadict])
        parentbody = omschrijving 
        
        parent = Article(headline=document_id, byline=itemnaam, text=parentbody, date=date, section=section, url=url, pagenr=0)

        stemmingen_check = 0
        for nr, stemming in enumerate(self.getStemmingen(xml)):
            headline, text = stemming
            headline = "%s - #%s | %s" % (document_id, nr+1, headline)

            if stemmingen_check == 0:
                yield parent
                stemmingen_check = 1
            bevat_stemmingen = True
            print("%s --> %s" % (headline, text))
         
            yield Article(headline=headline, byline=itemnaam, text=text, date=date, section=section, url=url, pagenr=nr+1, parent=parent)

        #return []

    def parseStemronde(self, spreker_element):
        sprekerdict = {}
        for s in spreker_element.getchildren():
            if s.tag == 'tekst':
                for t in s.getchildren():
                    if t.tag == 'al-groep': tekst += ('\n'.join([al.text_content() for al in t.getchildren()]))     
                    elif t.tag == 'al': tekst += t.text_content()
                       
        return tekst

    def checkIrrelevant(self, draad_text):
        irrelevant = 1
        for cr in ['stemming ','stemmen ','gestemd', 'stemmingen ']:
            if cr in draad_text.lower(): irrelevant = 0

        for ci in ['aan de orde zijn']:
            if ci in draad_text.lower(): irrelevant = 1

        return irrelevant

    def getStemmingen(self, xml):
        if len(xml.cssselect('spreekbeurt')) == 0: # Determines which way to parse
            try: sprekerparent = xml.cssselect('spreker')[0].getparent()
            except:
            	try: sprekerparent = xml.cssselect('voorz')[0].getparent()
            	except: return

            check_stemming = False
            for par in sprekerparent.getchildren():
                if check_stemming == True: 
                    stemverslag = draad_text + '\n\n' + par.text_content()
                    yield ('met stemming' ,stemverslag)
                    check_stemming = False
                if par.tag == 'draad':
                    draad_text = par.text_content()

                    check_irrelevant = self.checkIrrelevant(draad_text)                        
                    if check_irrelevant == 1: continue
                    
                    if 'stemming komt' in draad_text:
                        draad_text = draad_text.split('In stemming komt')[1]
                        check_stemming = True
                    else: yield ('zonder stemming', draad_text)
                        
                
        else: # Using alternative
            check_stemming = False
            for par in xml.cssselect('spreekbeurt')[0].getparent():
                if check_stemming == True:
                    stemverslag = draad_text + '\n\n' + self.parseStemronde(par)
                    yield ('met stemming', stemverslag)
                    check_stemming = False
                if par.tag == 'tekst':
                    draad_text = ''.join([p.text_content() for p in par.getchildren()])

                    check_irrelevant = self.checkIrrelevant(draad_text)                        
                    if check_irrelevant == 1: continue
                    
                    if not 'stem' in draad_text: continue
                    if 'stemming komt' in draad_text:
                        draad_text = draad_text.split('In stemming komt')[1]
                        check_stemming = True
                    else: yield ('zonder stemming', draad_text)

                                               
if __name__ == '__main__':
    from amcat.scripts.tools import cli
    from amcat.tools import amcatlogging
    amcatlogging.debug_module("amcat.scraping.scraper")
    amcatlogging.debug_module("amcat.scraping.document")
    cli.run_cli(StemmingenScraper)


