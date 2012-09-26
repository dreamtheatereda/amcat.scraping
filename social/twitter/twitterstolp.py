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
from amcat.scraping.document import Document, HTMLDocument


from urllib import urlencode
from urllib2 import HTTPError
from urlparse import urljoin
from amcat.tools.toolkit import readDate
from datetime import date

import csv
import os
CSV_FILE = csv.reader(open(os.environ.get('PYTHONPATH')+'scraping/social/twitter/twitter.csv','rb'))



INDEX_URL = "https://www.twitter.com"

import oauth2 as oauth
 
CONSUMER_KEY = 'YLDO7j9C7MigKeGnhcAjbQ'
CONSUMER_SECRET = 'njXW1bLzPZPBpUswkOhYHbSYl8VQ80paTPtoD6NiJg'




def oauth_req(url, key, secret, http_method="GET",post_body=None,http_headers=None):
    consumer = oauth.Consumer(key=CONSUMER_KEY, secret=CONSUMER_SECRET)
    token = oauth.Token(key=key, secret=secret)
    client = oauth.Client(consumer, token)
    resp, content = client.request(
        url,
        method=http_method
        )
    return content

import json




class TwitterPoliticiScraper(HTTPScraper, DBScraper):
    medium_name = "Twitter - invloedrijke twitteraars en politici"

    def __init__(self, *args, **kwargs):
        super(TwitterPoliticiScraper, self).__init__(*args, **kwargs)


    def _login(self, username, password):
        
        POST_DATA = {
            'email' : username,
            'password' : password
        }
        self.opener.opener.open(INDEX_URL, urlencode(POST_DATA))


    def _get_units(self):
        """get pages"""
        i = 0
        for row in CSV_FILE:
            i = i + 1
            if i == 1:
                continue
            try:
                url = row[7]
                page = self.opener.opener.open(url)
            except:
                print("twitter addres {} not found".format(row[7]))
                open('readme.txt','a+').write("twitter addres {} not found".format(row[7]))
                continue

            page = HTMLDocument(url = url,date = self.options['date'])
            yield page 
                


        

        
    def _scrape_unit(self, page):
        """gets articles from a page"""
        try:
            page.prepare(self)
            page.doc = self.getdoc(page.props.url)
        except (HTTPError,ValueError):
            return
        FULL_NAME = page.doc.cssselect("h1.fullname")[0].text.strip()
        for div in page.doc.cssselect("div.stream-item"):
            if div.get('data-item-type')=="tweet":
                t_date=readDate(div.cssselect("small.time a")[0].get('title')).date()
                if self.options['date'] == t_date:
                    tweet = Document()
                    tweet.text = div.cssselect("p.js-tweet-text")[0].text_content()
                    tweet.date = div.cssselect("small.time a")[0].get('title')
                    tweet.author = FULL_NAME
                    yield tweet
                elif self.options['date']>t_date:
                    break
            


if __name__ == '__main__':
    from amcat.scripts.tools import cli
    from amcat.tools import amcatlogging
    amcatlogging.debug_module("amcat.scraping.scraper")
    amcatlogging.debug_module("amcat.scraping.document")
    cli.run_cli(TwitterPoliticiScraper)


