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

from urlparse import urljoin
from cStringIO import StringIO
import ftplib, datetime, threading
from contextlib import contextmanager

from xml.sax.saxutils import unescape
import logging, os
log = logging.getLogger(__name__)

from amcat.scraping.scraper import DBScraper
from amcat.scraping.document import HTMLDocument
from amcat.models.article import Article
from amcat.tools.stl import STLtoText
from amcat.scraping.toolkit import todate
from amcat.models.medium import get_or_create_medium

mediadict = {} #replace by reference to database table
HOST = "ftp.tt888.nl"

def getDate(fn):
    datestring = fn.split('/')[1].split('.txt')[0].split('-')
    timestring = datestring[3].split(',')
    date = datetime.datetime(int(datestring[0]),int(datestring[1]),int(datestring[2]),int(timestring[0]),int(timestring[1]))
    return date

def getUrlsFromSet(setid, check_back=30):
    """Returns list with all URLS of articles in the articleset for the last [check_back] days"""
    fromdate = (datetime.date.today() - datetime.timedelta(days = check_back))
    articles = (Article.objects.filter(date__gt = fromdate)
                .filter(articlesets_set = setid).only("url"))
    urls = set(a.url for a in articles)
    return urls

def cleanUpDraaiboek(text):
    body = ''
    for t in text.readlines():
        t = t.decode('latin-1', 'ignore')
        t = t.replace('\n',' ').replace('\r','')
        if t == ' ': continue
        if '000 ' in t: t = '\n\n'
        if '888' in t: t = '\n\n'
        body += t
    return body
            
class DraaiboekenScraper(DBScraper):

    def __init__(self, *args, **kargs):
        super(DraaiboekenScraper, self).__init__(*args, **kargs)
        self._ftp = ftplib.FTP(HOST)  
        self._ftp.login(self.options['username'], self.options['password'])
        self._ftp_lock = threading.Lock()

    @contextmanager
    def ftp(self):
        self._ftp_lock.acquire()
        try:
            yield self._ftp
        finally:
            self._ftp_lock.release()
        
    def _get_units(self):
        existing_files = getUrlsFromSet(setid=self.articleset, check_back=30)
        print(existing_files)
        with self.ftp() as ftp:
            for folder in ftp.nlst():
                if '.txt' in folder: continue
                files = {}
                got_xml = False
                for f in ftp.nlst(folder):
                    if '.txt' in f:
                        if f in existing_files:
                            print('Already in database: %s' % f)
                            continue
                        files[f.split('/')[1].split('.txt')[0]] = f
                    if '.xml' in f: got_xml = f
                if got_xml:
                    if len(files) == 0:
                        print('\nAll files in %s already in database\n' % got_xml)
                        continue
                    dest = StringIO()
                    ftp.retrbinary(b'RETR %s' % got_xml, dest.write)
                    
                    xml = dest.getvalue()
                    for p in xml.split('<qry_Nieuwsmonitor>')[1:]:
                        tb = p.split('titelbestand>')[1].split('<')[0]
                        pn = p.split('Programmanaam>')[1].split('<')[0].strip()
                        if tb in files:
                            dest = StringIO()
                            ftp.retrbinary(b'RETR %s' % files[tb], dest.write)
                            dest.seek(0)
                            body = cleanUpDraaiboek(dest)
                            yield (pn,files[tb],body)
                        else:
                            print('Missing or already in database: %s' % tb)
                    

    def _scrape_unit(self, ftuple):
        medium = ftuple[0]
        url = ftuple[1]
        body = ftuple[2]
        
        title = medium
        date = getDate(url)    
        print(title, date)
        med = get_or_create_medium(medium)
    
        art = Article(headline=medium, text=body,
                      medium = med, date=date, url = url)
        #yield art
        return []


if __name__ == '__main__':
    from amcat.scripts.tools import cli
    from amcat.tools import amcatlogging
    amcatlogging.debug_module("amcat.scraping.scraper")
    amcatlogging.debug_module("amcat.scraping.document")
    cli.run_cli(DraaiboekenScraper)


