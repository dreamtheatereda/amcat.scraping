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
        
class HandelingenPerSprekerScraper(OfficieleBekendmakingenScraper):
    doctypelist = ['handelingen']
    medium_name = "Handelingen 2e kamer"

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
        yield parent

        for nr, sprekerdict in enumerate(self.sprekerDictReader(xml)):
            spreker = self.printSpreker(sprekerdict)
            headline_spreker = "%s - #%s | %s" % (document_id, nr+1, spreker)
            yield Article(headline=headline_spreker, author=spreker, byline=itemnaam, text=sprekerdict['tekst'], date=date, section=section, url="%s#%s" % (url, nr+1), pagenr=nr+1, parent=parent)

            for motie in sprekerdict['moties']:
                yield Article(headline="%s | MOTIE" % headline_spreker, author=spreker, byline=itemnaam, text=motie, date=date, section=section, url="%s#%s" % (url, nr+1), pagenr=nr+1, parent=parent)
        #return []

    def getMotie(self, element):
        try: motie = '\n'.join([mtekst.text_content() for mtekst in element.find('mtekst')])
        except:
            motie = '\n'.join([mtekst.text_content() for mtekst in element.cssselect('al')])
        return motie

    def parseSpreker2(self, spreker_element):
        tekst, moties, otherelements = '', [], []
        sprekerdict = {}
        for s in spreker_element.getchildren():
            if s.tag == 'spreker':
                for wie in s.getchildren():
                    if wie.tag == 'voorvoegsels': sprekerdict['aanspr'] = wie.text
                    elif wie.tag == 'naam': sprekerdict['naam'] = wie.text_content()
                    elif wie.tag == 'politiek': sprekerdict['partij'] = wie.text
                    else: otherelements.append()
            elif s.tag == 'tekst':
                for t in s.getchildren():
                    if t.tag == 'al-groep': tekst += ('\n'.join([al.text_content() for al in t.getchildren()]))     
                    elif t.tag == 'al': tekst += t.text_content()
                    elif t.tag == 'motie': moties.append(self.getMotie(t))
                    else: otherelements.append(s)
                       
        sprekerdict['tekst'], sprekerdict['other_el'], sprekerdict['moties'] = tekst, otherelements, moties
        if len(otherelements) > 0: log.warn("UNUSED <SPREKER> ELEMENTS, CONTAINING: %s" % [o.text_content() for o in otherelements])
        return sprekerdict
    
                
    def parseSpreker1(self, spreker_element):
        tekst, moties, otherelements = '', [], []
        sprekerdict = {}
        for s in spreker_element.getchildren():
            if s.tag == 'wie': sprekerdict = dict((e.tag, e.text_content()) for e in s.getchildren())
            elif s.tag == 'al':
                for element in s.getchildren():
                    if element.tag == 'motie': moties.append(self.getMotie(s))
                tekst += s.text_content()
            elif s.tag == 'motie': moties.append(self.getMotie(s))
            else:
                otherelements.append(s)
        sprekerdict['tekst'], sprekerdict['other_el'], sprekerdict['moties'] = tekst, otherelements, moties
        if len(otherelements) > 0: log.warn("UNUSED <SPREKER> ELEMENTS, CONTAINING: %s" % [o.text_content() for o in otherelements])
        return sprekerdict

    def parseVoorzitter(self, voorzitter_element, naam='Voorzitter'):
        sprekerdict = {}
        sprekerdict['naam'] = naam
        tekst, moties, otherelements = '', [], []
        for s in voorzitter_element.getchildren():
            if s.tag == 'al':
                for al_child in s.getchildren():      
                    if al_child.tag == 'lijst':
                        for li in al_child.getchildren():
                            tekst += li.text_content()
                    else: otherelements += [element for element in s.getchildren()]
                tekst += s.text_content()
            elif s.tag == 'motie': moties.append(self.getMotie(s))
            else:
                otherelements.append(s)
        sprekerdict['tekst'], sprekerdict['other_el'], sprekerdict['moties'] = tekst, otherelements, moties
        if len(otherelements) > 0: log.warn("UNUSED <SPREKER> ELEMENTS, CONTAINING: %s" % [o for o in otherelements])
        return sprekerdict

    def sprekerDictReader(self, xml):
        """yields dictionaries containing meta-info and text for each consequtive speaker"""
        if len(xml.cssselect('spreekbeurt')) == 0: # Determines which parseSpreker() should be used for respective xml
            print('Using parsSpreker1')
            try: sprekerparent = xml.cssselect('spreker')[0].getparent()
            except:
            	try: sprekerparent = xml.cssselect('voorz')[0].getparent()
            	except: return


            try: naam = "Voorzitter (%s)" % xml.cssselect('vrznaam')[0].text_content()
            except: naam = 'Voorzitter'
                
            for par in sprekerparent.getchildren():
                if par.tag == 'spreker': yield self.parseSpreker1(par)
                if par.tag == 'voorz': yield self.parseVoorzitter(par, naam)
                
        else:
            print('Using parsSpreker2')
        
            for par in xml.cssselect('spreekbeurt'):
                yield self.parseSpreker2(par)
                                               
            
    def printSpreker(self, sprekerdict):
        spreker = sprekerdict['naam']
        if 'aanspr' in sprekerdict: spreker = "%s %s" % (sprekerdict['aanspr'], spreker)
        if 'partij' in sprekerdict: spreker = "%s (%s)" % (spreker, sprekerdict['partij'])
        return spreker


if __name__ == '__main__':
    from amcat.scripts.tools import cli
    from amcat.tools import amcatlogging
    amcatlogging.debug_module("amcat.scraping.scraper")
    amcatlogging.debug_module("amcat.scraping.document")
    cli.run_cli(HandelingenPerSprekerScraper)


