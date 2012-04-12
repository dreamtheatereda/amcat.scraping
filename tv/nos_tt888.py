#!/usr/bin/python
from __future__ import unicode_literals, print_function, absolute_import
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

NAME = 'Subtitle (stl) scraper'

HOST = "ftp.tt888.nl"
FOLDER = ""
OUTPUT = "tt888backup"

MEDIADICT = {}
    
import logging
log = logging.getLogger(__name__)

from amcat.scraping.scraper import DBScraper
from amcat.scraping.document import HTMLDocument
from amcat.models.article import Article
from amcat.tools import toolkit
from amcat.tools.stl import STLtoText
from amcat.scraping.toolkit import todate
from amcat.models.medium import get_or_create_medium
from urlparse import urljoin
import os, re, struct, sys, ftplib, datetime

def read(ftp, OUTPUT):
    stlfiles = []
    for fn in ftp.nlst():
        fn = fn.decode("latin-1")
        stlfiles.append('%s/%s' % (OUTPUT, fn))
        dest = open(os.path.join(OUTPUT, fn), 'wb')
        ftp.retrbinary(b'RETR %s' % (fn.encode('latin-1')) , dest.write)
    return stlfiles

def getStlFiles(HOST, USER, PASSWD, FOLDER):  
    ftp = ftplib.FTP(HOST)  
    ftp.login(USER, PASSWD)
    ftp.cwd(FOLDER)
    stlfiles = read(ftp, OUTPUT)
    return stlfiles

def getDate(title):
    """LENGTHY WORK-AROUND, DUE TO 'HOUR' OCCASIONALLY EXCEEDING 24 (LATE NIGHT SHOWS)"""
    datestring = title.split('-')[0:4]
    year, month, day, hour, minute = int(datestring[0]), int(datestring[1]), int(datestring[2]), int(datestring[3].split(',')[0]), int(datestring[3].split(',')[1])
    if hour > 23:
        hour = hour - 24
        date = datetime.datetime(year,month,day,hour,minute)
        date = date + datetime.timedelta(1)
    else: date = datetime.datetime(year,month,day,hour,minute)
    return date

def getUrlsFromSet(setid, check_back=30):
    fromdate = (datetime.date.today() - datetime.timedelta(days = check_back))
    urls = set(a.url.split('/')[-1] for a in Article.objects.filter(date__gt = datetime.date(2012,3,20)).filter(articlesets = 9).only("url"))
    return urls

class tt888Scraper(DBScraper):
    #medium_name = "TT888_unassigned"

    def _get_units(self):
        existing_files = getUrlsFromSet(setid=self.articleset, check_back=30)
        for fn in getStlFiles(HOST, self.options['username'], self.options['password'], FOLDER):
                title = fn.split('/')[-1]                
                if title in existing_files:
                    print("Already in articleset: %s" % title)
                    continue # Skip if already in database
                if len(title.split('-')) > 9: continue # Filter out rewinds (marked by dubble dates)
                yield fn


    def _scrape_unit(self, fn):
        body = STLtoText(open(fn).read())
        title = fn.split('/')[-1]
        naam = title.split('-')[-1].split('.stl')[0].strip().lower()
        date = getDate(title)    
        if naam in MEDIADICT:
            med = get_or_create_medium(MEDIADICT[naam])
        else: med = get_or_create_medium('TT888_unassigned')
        print(naam, med, date, fn)
        
        art = Article(headline=naam, text=body.decode('latin-1'), medium = med, date=date, url = fn)

        yield art


if __name__ == '__main__':
    from amcat.scripts.tools import cli
    from amcat.tools import amcatlogging
    amcatlogging.debug_module("amcat.scraping.scraper")
    amcatlogging.debug_module("amcat.scraping.document")
    cli.run_cli(tt888Scraper)

