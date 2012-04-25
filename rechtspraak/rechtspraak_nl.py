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

import datetime, sys, urllib, urllib2
    
import logging
from itertools import count

log = logging.getLogger(__name__)

from amcat.scraping.scraper import DatedScraper, HTTPScraper
from amcat.scraping.document import HTMLDocument
from amcat.models.article import Article
from amcat.tools import toolkit
from amcat.tools.stl import STLtoText
from amcat.scraping.toolkit import todate
from amcat.models.medium import get_or_create_medium



INDEX_URL = "http://zoeken.rechtspraak.nl/ResultPage.aspx?snelzoeken=true&searchtype=kenmerken&datum_tussen_vanaf=%s&datum_tussen_tm=%s&soort_datumzoek=Tussen&veld_datumzoek=datum_gepubliceerd&sortby=rechtsgebied_rechtspraak+asc+ljn"

def getDate(title):
    return

def getViewstate(url):
    """VIEWSTATE is a required formfield for ASP to allow a request""" 
    page = (urllib.urlopen(url).read()).decode("latin-1")
    vs = page.split('name="__VIEWSTATE"')[1].split('value="')[1].split('"')[0]
    return vs

def navigateASP(url, viewstate, page):
    """Makes a request to ASPX page and returns a string object. Forms and values are grouped in a list of tuples (filename, value). The viewstate forms are required to allow POST requests. (Rechtspraak.nl can almost entirely be navigated with url, except for navigating through multiple pages of articles or tampering with the limit of articles per page)""" 
    
    formFields = (
            (r'__VIEWSTATE', r'%s' % viewstate),
            (r'__VIEWSTATEENCRYPTED', r''),
            (r'ctl00$ContentPlaceHolder1$tbxPaginaNummer', page),
            (r'ctl00$ContentPlaceHolder1$tbxSorteerVolgorde',r'rechtsgebied_rechtspraak asc ljn'),
            (r'ctl00$ContentPlaceHolder1$tbxSetOverview', 'True') # If any value is given (=true), article per page limit is set to 250
            )

    encodedFields = urllib.urlencode(formFields)
    req = urllib2.Request(url, encodedFields)
    f = urllib2.urlopen(req).read().decode("latin-1")
    return f
            
class RechtspraakScraper(DatedScraper, HTTPScraper):
    medium_name = 'Rechtspraak.nl'
     
    def _get_units(self):
        date = self.options['date']
        url = INDEX_URL % ((date - datetime.timedelta(1)).strftime('%d-%m-%Y'), date.strftime('%d-%m-%Y'))
        print(url)
        viewstate = getViewstate(url)

        for page in count(1):
            f = navigateASP(url, viewstate, page=page)
            for arturl in f.split('t_kop t_default')[1:]:
                arturl = arturl.split('href="')[1].split('"')[0]
                yield arturl

            if not len(f) == 250: break 

    def _scrape_unit(self, arturl):
        doc = self.getdoc(arturl)
        metadata = {}
        for d in doc.cssselect('div'):
            if not d.get('id') == 'ctl00_ContentPlaceHolder1_BistroDetailMainControl_detailMainPanel': continue

            metatable = d.cssselect('table.l_resultSubTable')[0]
            for meta in metatable.cssselect('tr'):
                key, content = meta.cssselect('span')
                key, content = key.text_content().strip(':'), content.text_content()
                metadata[key] = content

            start = False
            for bodypart in d.cssselect('span'):
                if bodypart.text_content() == 'Uitspraak': start = True
                if start == False: continue
                print(bodypart.text_content())
                
            sys.exit()
            
            
            return []


if __name__ == '__main__':
    from amcat.scripts.tools import cli
    from amcat.tools import amcatlogging
    amcatlogging.debug_module("amcat.scraping.scraper")
    amcatlogging.debug_module("amcat.scraping.document")
    cli.run_cli(RechtspraakScraper)


