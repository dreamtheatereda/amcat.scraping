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

from amcat.scraping.document import Document, HTMLDocument
import json

from urllib import urlencode
#from urlparse import urljoin
#from amcat.tools.toolkit import readDate

LOGIN_URL = "http://fd.nl/handle_login"

SEARCH_URL = "http://fd.nl/solr/select/?wt=json&indent=on&hl=on&hl.fl=title_fd,intro_fd&hl.simple.pre=%3Cspan%20class=%27cbBe2%20fBold%27%3E&hl.simple.post=%3C/span%3E&facet=true&fq=state:published&fq=contenttype:article&q=publication:fd%20publishdate:[{y:04d}-{m:02d}-{d:02d}T00:00:00.000Z%20TO%20{y:04d}-{m:02d}-{d:02d}T23:59:59.999Z]&start=0&rows=9999&sort=publishdate%20desc&facet.field=bron_fd&facet.field=company_fd&facet.field=icb_fd&facet.field=section_fd&facet.field=tag_fd&facet.field=author_fd&facet.field=person_fd&json.wrf=fdmg.fd.search.callback.searchResults&_=1349441426060"

NEXT_URL = "http://fd.nl/?service=searchRedirect&id={}"

from amcat.scraping.scraper import HTTPScraper,DBScraper
from amcat.tools.toolkit import readDate

class WebFDScraper(HTTPScraper, DBScraper):
    medium_name = "FD Website"

    def __init__(self, *args, **kwargs):
        super(WebFDScraper, self).__init__(*args, **kwargs)

    def _login(self,username,password):
        initial = self.open("http://digikrant.fd.nl")
        form = {
            'email' : username,
            'password' : password
            }
        pg = self.open(LOGIN_URL,urlencode(form))


    def _get_units(self):
        index_dict = {
            'y' : self.options['date'].year,
            'm' : self.options['date'].month,
            'd' : self.options['date'].day
        }


        url = SEARCH_URL.format(**index_dict)
        print(url)
        result = self.open(url) 
        data = json.loads(result.read()[38:-1])
        for doc in data['response']['docs']:
            nxt_url = NEXT_URL.format(doc['objectid'])
            text = self.open(nxt_url).read()
            start = text.find('setTimeout("location.href=\'')+27;end = text.find('\';",',start)
            print("start: {}, end: {}, url: {}".format(start,end,text[start:end]))
            yield HTMLDocument(url=text[start:end],date=readDate(doc['publishdate']),headline=doc['title'])

        
    def _scrape_unit(self, page): 
        page.prepare(self)
        page.doc = self.getdoc(page.props.url)
        page.props.headline = page.doc.cssselect("div.left h1")[0].text_content()
        page.props.text = page.doc.cssselect("div.left div.left div.left div.topDivider")[0].text_content()
        page.props.author = page.doc.cssselect("div.left div.left div.left div.left div.left div.fAr14")[0].text.strip()
        yield page
        
        
        
        

    def get_article(self, page):
        return page




if __name__ == '__main__':
    from amcat.scripts.tools import cli
    from amcat.tools import amcatlogging
    amcatlogging.debug_module("amcat.scraping.scraper")
    amcatlogging.debug_module("amcat.scraping.document")
    cli.run_cli(WebFDScraper)


