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
        
INDEXURL = "%s/actueel/1/%s"
BASEURL = "https://zoek.officielebekendmakingen.nl/%s"

def getUrlsFromSet(setid):
    articles = (Article.objects.filter(articlesets_set = setid).only("url"))
    urls = set(a.url.split('#')[0] for a in articles)
    return urls

class OfficieleBekendmakingenScraper(DatedScraper, HTTPScraper):
    """Downloads XML files of documents that are PUBLISHED (!) on the assigned date"""
    doctypelist = ['kamerstuk','handelingen','kamervragen_zonder_antwoord', 'kamervragen_aanhangsel','agenda','niet_dossierstuk']
    
    def _get_units(self):
        existing_urls = []
        for page in self.get_pages():
            doc = self.getdoc(page)
            for arturl in set(a.get('href') for a in doc.cssselect('div.lijst > ul > li > a')):
                if existing_urls == []: existing_urls = getUrlsFromSet(setid=self.articleset)
                arturl = BASEURL % arturl
                if arturl in existing_urls:
                    print("Already in articleset: %s" % arturl)
                    continue
                yield(arturl.replace('html','xml'))
 
    def get_pages(self):
        for doctype in self.doctypelist:
            url = INDEXURL % (doctype, self.options['date'].strftime('%d%m%Y'))
            doc = self.getdoc(BASEURL % url)
            
            pages = set(p.get('href') for p in doc.cssselect('div."paginering boven" > a'))
            pages.add(url)
            for page in pages:
                yield BASEURL % page

    def getNotesDict(self, xml, printit=False):
        notesdict = {}
        for noot in xml.cssselect('noot'):
            
            if 'nr' in [e.tag for e in noot]:
                print(noot.get('nr'))
                notesdict[noot.get('nr')] = noot.text_content().strip()
            elif not noot.get('nr') == None: notesdict[noot.get('nr')] = noot.text_content().strip()
            elif not noot.find('noot.lijst') == None:
                for nr, n in enumerate(noot.find('noot.lijst')):
                        notesdict[noot.find('noot.nr').text_content() + '.%s' % nr] = n.text_content()
            else:
                try: nootid = noot.find('noot.nr').text_content()
                except: nootid = noot.get('id').strip('n')
                notesdict[nootid] = noot.find('noot.al').text_content().strip()
 
                    
        if printit == True:
            for note in notesdict: print(note, ': ', notesdict[note])
        return notesdict

    def traceNootRefNr(self, nootref, xml):
        if not nootref.get('nr') == None: return nootref.get('nr')
        
        for noot in xml.cssselect('noot'):
            if noot.get('id') == nootref.get('refid'):
                nootrefnr = noot.find('noot.nr').text_content()
                return nootrefnr

    def getMetaDict(self, xml, printit=False):
        metadict = dict((meta.get('name'), meta.get('content')) for meta in xml.cssselect('meta'))
        if printit == True:
            for meta in metadict: print(meta, ': ', metadict[meta])
        return metadict

    def safeMetaGet(self, d, key):
        try: value = d[key]
        except:
            value = 'missing'
            log.warn('MISSING METADATA FOR %s' % key)
        return value


    def _scrape_unit(self, url):
        xml = self.getdoc(url)
        return []


if __name__ == '__main__':
    from amcat.scripts.tools import cli
    from amcat.tools import amcatlogging
    amcatlogging.debug_module("amcat.scraping.scraper")
    amcatlogging.debug_module("amcat.scraping.document")
    cli.run_cli(OfficieleBekendmakingenScraper)


