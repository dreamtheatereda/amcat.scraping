# -*- coding: utf-8 -*-
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

from amcat.scraping.scraper import DBScraper, HTTPScraper
from amcat.scraping.document import HTMLDocument
from amcat.scraping import toolkit
try:
    from scrapers.newspapers import wegenertools
except ImportError:
    from amcatscraping.newspapers import wegenertools

import re
from urllib import urlencode
from httplib2 import iri2uri


INDEX_URL = "http://{paper}.ned.newsmemory.com/eebrowser/frame/develop.4979.enea.3/load/newspaper.php?pSetup={paper}&userid=NOUSER&date=0@/{paper}/{year}{month}{day}"

PAGE_URL = "http://{paper}.ned.newsmemory.com/eebrowser/frame/develop.4979.enea.3/php-script/fullpage.php?pSetup={paper}&file=0@/{paper}/{year}{month}{day}/{pagefile}/&section={section}&edition={edition}&pageNum={page_str}"

LOGIN_URL = "http://{paper}.ned.newsmemory.com/eebrowser/frame/develop.4979.enea.3/protection/login.php?pSetup={paper}"

from httplib import BadStatusLine

from ast import literal_eval

class TubantiaScraper(HTTPScraper, DBScraper):
    medium_name = "Dagblad Tubantia/Twentsche Courant"
    paper = "tubantia"

    def _login(self, username, password):
        """log in on the web page
        @param username: username to log in with
        @param password: password 
        """
        url = LOGIN_URL.format(paper=self.paper)
        page = self.getdoc(url)
            
        form = toolkit.parse_form(page)
        form["username"] = str(username)
        form["password"] = str(password)
        page = self.open(url, urlencode(form))

        cookies=page.info()["Set-Cookie"]
        tauidloc = cookies.rfind("TAUID")
        tauid = cookies[tauidloc:cookies.find(";",tauidloc)]
        tauid_expires = cookies[cookies.find("expires",tauidloc):cookies.find(";",cookies.find(";",tauidloc)+1)]
 
        machineidloc = cookies.find("MACHINEID")
        machineid = cookies[machineidloc:cookies.find(";",machineidloc)]
        machineid_expires = cookies[cookies.find("expires",machineidloc):cookies.find(";",cookies.find(";",machineidloc)+1)]
        cookieheader = machineid+"; "+tauid
        self.opener.opener.addheaders.append(("Cookie",cookieheader))
        page = self.open(url, urlencode(form))

    def _get_units(self):
        year=self.options['date'].year
        month = self.options['date'].month
        day = self.options['date'].day
        if len(str(month))==1:
            month='0'+str(month)
        if len(str(day))==1:
            day='0'+str(day)

            
        INDEXURL = INDEX_URL.format(year=year,month=month,day=day,paper=self.paper)
        index_text = unicode(self.getdoc(INDEXURL).text_content())
        occurrences = [m.start() for m in re.finditer('p[i++]', index_text)]
        for occ in occurrences:
            start = index_text.find("(", occ); end = index_text.find("(", start)
            args = [arg.strip('"') for arg in index_text[start:end].split(',')]
            pagefile, section, page_str, edition = args[:4]
            url = PAGE_URL.format(paper=self.paper, **locals())
            yield dict(url = url, edition = edition, page_str = page_str)
        
    def _scrape_unit(self, ipage):
        page = ipage
        ipage = HTMLDocument(ipage)
        ipage.doc = self.open(page['url'])
        
        text = wegenertools.clean(ipage.doc.read())
        err_text = "Uw account is niet geregistreerd voor de door u gekozen uitgave."
        if err_text in text:
            raise Exception(err_text)
        for article_ids in wegenertools.get_article_ids(text):
            body,headline,byline = wegenertools.get_article(text,article_ids)
            if len(body) >= 300: #filtering non-articles, image links and other html crap
                artpage = HTMLDocument()
                stop = False
                for part in body.split("\n\n"):
                    if part.isupper():
                        pass
                    else:
                        if "\n" in part:
                             #when title has a linebreak it's probably not an article
                            stop=True
                            break
                        else:
                            
                            artpage.props.headline = part
                            break
                if stop:
                    break
                else:
                    
                    p = re.compile("[\\\]udc[\w\w]")
                    artpage.props.text = literal_eval(p.sub("",repr(body)))
                    artpage.props.edition = page['edition']
                    artpage.props.byline = byline
                    artpage.props.section = page['section']
                    if re.match("[A-Z][0-9]+", page['page_str']):
                        artpage.props.section += " - section " + page['page_str'][0]
                        artpage.props.pagenr = int(page['page_str'][1:])
                    else:
                        artpage.props.pagenr = int(page['page_str'])

                    dateline_pattern = re.compile("(^[^\n]+\n\n([A-Z]+( [A-Z]+)?) -\n)|(([A-Z]+( [A-Z]+)?)\n\n)")
                    match = dateline_pattern.search(artpage.props.text)
                    if match:
                        #dateline and theme have the same syntax and are therefore undistinguishable
                        artpage.props.dateline_or_theme = match.group(2) or match.group(5)
                    artpage.props.url = page['url']
                    yield artpage

if __name__ == '__main__':
    from amcat.scripts.tools import cli
    from amcat.tools import amcatlogging
    amcatlogging.debug_module("amcat.scraping.scraper")
    amcatlogging.debug_module("amcat.scraping.document")
    cli.run_cli(TubantiaScraper)

