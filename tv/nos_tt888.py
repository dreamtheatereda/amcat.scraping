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
    
import logging
log = logging.getLogger(__name__)

from amcat.scraping.scraper import DBScraper
from amcat.scraping.document import HTMLDocument
from amcat.models.article import Article
from amcat.tools.stl import STLtoText
from amcat.scraping.toolkit import todate
from amcat.models.medium import Medium

mediadict = {989900373:77,
             989900380:87,
             989900392:96,
             989900395:163,
             989900365:479,
             989900389:490,
             989900555:999,
             989900427:81,
             989900423:269,
             989900387:78,
             989900390:271,
             989900617:113}

HOST = "ftp.tt888.nl"

def getDate(title):
    """Parses date (datetime object) from title of tt-888 .stl files. If hour > 24 (the date of nighttime broadcasts to a certain hour are attributed to former day), the true date of the broadcast is used. (hour minus 24, and day plus 1)"""
    datestring = title.split('-')[0:4]
    year, month, day, hour, minute = int(datestring[0]), int(datestring[1]), int(datestring[2]), int(datestring[3].split(',')[0]), int(datestring[3].split(',')[1])
    if hour > 23:
        hour = hour - 24
        date = datetime.datetime(year,month,day,hour,minute)
        return date + datetime.timedelta(1)
    else:
        return datetime.datetime(year,month,day,hour,minute)

def getUrlsFromSet(setid, check_back=30):
    """Returns list with all URLS of articles in the articleset for the last [check_back] days"""
    fromdate = (datetime.date.today() - datetime.timedelta(days = check_back))
    articles = (Article.objects.filter(date__gt = fromdate)
                .filter(articlesets_set = setid).only("url"))
    urls = set(a.url.split('/')[-1] for a in articles if a.url)
    return urls
            
class tt888Scraper(DBScraper):

    def __init__(self, *args, **kargs):
        super(tt888Scraper, self).__init__(*args, **kargs)
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
        with self.ftp() as ftp:
            files = ftp.nlst()
        for fn in files:
            fn = fn.decode("latin-1")
            title = fn.split('/')[-1]                
            if title in existing_files:
                print("Already in articleset: %s" % title)
                continue # Skip if already in database
            if title.count('-') > 9:
                continue # Filter out reruns (marked by double dates)
            yield fn

    def _scrape_unit(self, fn):
        dest = StringIO()
        with self.ftp() as ftp:
            ftp.retrbinary(b'RETR %s' % (fn.encode('latin-1')) , dest.write)
        body = STLtoText(dest.getvalue())
        body = body.decode('latin-1','ignore').strip().lstrip('888').strip()
        title = fn.split('/')[-1]
        medium = title.split('-')[-1].split('.stl')[0].strip().lower()
        date = getDate(title)

        if medium == 'nos journaal' and int(format(date, '%H')) == 20 and int(format(date, '%M')) == 0: medium = 'nos journaal 20:00'
        med = Medium.get_or_create(medium)
        if med.id in mediadict:
            print("saving %s as %s" % (med.id,mediadict[med.id]))
            med = Medium.objects.get(id=mediadict[med.id])
        
        art = Article(headline=medium, text=body,
                      medium = med, date=date, url = fn)
        yield art
        


if __name__ == '__main__':
    from amcat.scripts.tools import cli
    from amcat.tools import amcatlogging
    amcatlogging.debug_module("amcat.scraping.scraper")
    amcatlogging.debug_module("amcat.scraping.document")
    cli.run_cli(tt888Scraper)


