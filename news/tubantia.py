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
from amcat.scraping.document import HTMLDocument, IndexDocument
from amcat.scraping import toolkit
import wegenertools
import re
import urllib2
from urllib import urlencode
#from urlparse import urljoin

INDEX_URL = "http://tubantia.ned.newsmemory.com/eebrowser/frame/develop.4979.enea.1/load/newspaper.php?pSetup=tubantia&userid=9635&date=0@/tubantia/{year}{month}{day}"

PAGE_URL = "http://tubantia.ned.newsmemory.com/eebrowser/frame/develop.4979.enea.1/php-script/fullpage.php?pSetup=tubantia&file=0@/tubantia/{year}{month}{day}/{pagefile}/&section={section}&edition={edition}&pageNum={pagenum}"

LOGIN_URL = "http://tubantia.ned.newsmemory.com/eebrowser/frame/develop.4979.enea.1/protection/login.php?pSetup=tubantia"


class TubantiaScraper(HTTPScraper, DBScraper):
    medium_name = "Tubantia"

    def __init__(self, *args, **kwargs):
        super(TubantiaScraper, self).__init__(*args, **kwargs)








    def _login(self, username, password):
        """log in on the web page
        @param username: username to log in with
        @param password: password 
        """
        page = self.getdoc(LOGIN_URL)
        form = toolkit.parse_form(page)
        form["username"] = str(username)
        form["password"] = str(password)
        page = self.opener.opener.open(LOGIN_URL, urlencode(form))
        
        cookies=page.info()["Set-Cookie"]
        tauidloc = [m.start() for m in re.finditer('TAUID', cookies)][2]
        tauid = cookies[tauidloc:cookies.find(";",tauidloc)]
        tauid_expires = cookies[cookies.find("expires",tauidloc):cookies.find(";",cookies.find(";",tauidloc)+1)]
        
        machineidloc = cookies.find("MACHINEID")
        machineid = cookies[machineidloc:cookies.find(";",machineidloc)]
        machineid_expires = cookies[cookies.find("expires",machineidloc):cookies.find(";",cookies.find(";",machineidloc)+1)]
        cookieheader = machineid+"; "+tauid
        self.opener.opener.addheaders.append(("Cookie",cookieheader))
        page = self.opener.opener.open(LOGIN_URL, urlencode(form))
        


    


        

    def _get_units(self):
        """papers are often organised in blocks (pages) of articles, this method gets the blocks, articles are to be gotten later"""



        
        year=self.options['date'].year
        month='0'+str(self.options['date'].month)
        day=self.options['date'].day

        INDEXURL = INDEX_URL.format(year=year,month=month,day=day)
        index_text = str(self.getdoc(INDEXURL).text_content())
        cur = index_text.find("p[i++]")
        self.page_data = []
        while index_text.find("p[i++]",cur+1) >= 0:
            start = cur
            cur = index_text.find("p[i++]",cur+1) #find next occurrence
            end = cur
            start = index_text.find("(",start,end)
            end = index_text.find(")",start,end)
            args = index_text[start:end].split('","')
            pagefile = args[0].strip('("').lower()
            section = args[1]
            pagenum = args[2].lstrip("0")
            edition = args[3]
            url = PAGE_URL.format(**locals())
            self.page_data.append(dict(pagefile=args[0].strip('("'),section=args[1],pagenum=args[2],edition=args[3],url=url))
        for page in self.page_data:
            yield page

        
    def _scrape_unit(self, ipage):
        
        page = ipage
        ipage = HTMLDocument(ipage)
        ipage.doc = self.getdoc(page['url'])
        ipage.page = page['pagenum']
        ipage.props.category = page['section']
        text = wegenertools.clean(ipage.doc.text_content())

        for article_ids in wegenertools.get_article_ids(text):
            text,headline,byline = wegenertools.get_article(text,article_ids)
            artpage = HTMLDocument()
            artpage.props.text = text
            artpage.props.headline = headline

            yield artpage

            





if __name__ == '__main__':
    from amcat.scripts.tools import cli
    from amcat.tools import amcatlogging
    amcatlogging.debug_module("amcat.scraping.scraper")
    amcatlogging.debug_module("amcat.scraping.document")
    cli.run_cli(TubantiaScraper)

