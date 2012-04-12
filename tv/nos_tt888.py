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

NAME = 'Subtitle (stl) scraper'

HOST = "ftp.tt888.nl"
FOLDER = ""
OUTPUT = "tt888backup"

MEDIADICT = {} # geen fijne oplossing, liever zoeken in media tabel op naam oid?
from urlparse import urljoin
import os, re, struct, sys, ftplib, datetime
    
import logging
log = logging.getLogger(__name__)

from amcat.scraping.scraper import DBScraper
from amcat.scraping.document import HTMLDocument
from amcat.models.article import Article
from amcat.tools import toolkit
from amcat.tools.stl import STLtoText
from amcat.scraping.toolkit import todate
from amcat.models.medium import get_or_create_medium

def read(ftp, OUTPUT): # geen hoofdletters voor lokale variabelen
    # liever bestanden als string doorgeven dan via schijf?
    stlfiles = []
    for fn in ftp.nlst():
        fn = fn.decode("latin-1")
        stlfiles.append('%s/%s' % (OUTPUT, fn))
        dest = open(os.path.join(OUTPUT, fn), 'wb')
        ftp.retrbinary(b'RETR %s' % (fn.encode('latin-1')) , dest.write)
    return stlfiles

def getStlFiles(HOST, USER, PASSWD, FOLDER): # geen hoofdletters voor lokale variabelen
    ftp = ftplib.FTP(HOST)  
    ftp.login(USER, PASSWD)
    ftp.cwd(FOLDER)
    stlfiles = read(ftp, OUTPUT)
    return stlfiles

def getDate(title):
    """LENGTHY WORK-AROUND, DUE TO 'HOUR' OCCASIONALLY EXCEEDING 24 (LATE NIGHT SHOWS)"""
    # docstring moet aangeven wat de functie doet (dus inclusief hoe om te gaan met >24 uren
    datestring = title.split('-')[0:4]
    year, month, day, hour, minute = int(datestring[0]), int(datestring[1]), int(datestring[2]), int(datestring[3].split(',')[0]), int(datestring[3].split(',')[1])
    if hour > 23:
        hour = hour - 24
        date = datetime.datetime(year,month,day,hour,minute)
        return date + datetime.timedelta(1)
    else:
        return datetime.datetime(year,month,day,hour,minute)

def getUrlsFromSet(setid, check_back=30):
    fromdate = (datetime.date.today() - datetime.timedelta(days = check_back))
    # vanwaar deze datum check??
    articles = (Article.objects.filter(date__gt = datetime.date(2012,3,20))
                .filter(articlesets = 9).only("url"))
    urls = set(a.url.split('/')[-1] for a in articles)
    return urls

class tt888Scraper(DBScraper):
    medium_name = 'TT888_unassigned'
    def _get_units(self):
        existing_files = getUrlsFromSet(setid=self.articleset, check_back=30)
        for fn in getStlFiles(HOST, self.options['username'], self.options['password'], FOLDER):
                title = fn.split('/')[-1]                
                if title in existing_files:
                    print("Already in articleset: %s" % title)
                    continue # Skip if already in database
                if len(title.split('-')) > 9:
                   continue # Filter out repeats (marked by dubble dates)
                yield fn


    def _scrape_unit(self, fn):
        body = STLtoText(open(fn).read())
        title = fn.split('/')[-1]
        naam = title.split('-')[-1].split('.stl')[0].strip().lower()
        date = getDate(title)    
        med = get_or_create_medium(MEDIADICT[naam]) if naam in MEDIADICT else None
        
        art = Article(headline=naam, text=body.decode('latin-1'),
                      medium = med, date=date, url = fn)
        yield art


if __name__ == '__main__':
    from amcat.scripts.tools import cli
    from amcat.tools import amcatlogging
    amcatlogging.debug_module("amcat.scraping.scraper")
    amcatlogging.debug_module("amcat.scraping.document")
    cli.run_cli(tt888Scraper)

