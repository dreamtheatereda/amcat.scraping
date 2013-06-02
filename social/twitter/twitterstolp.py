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
from urllib2 import HTTPError, URLError
from urlparse import urljoin
from amcat.tools.toolkit import readDate
from datetime import datetime

import json

import csv
import os

target = os.environ.get('PYTHONPATH')+"/{scraping_module}/social/twitter/users.csv"
if os.path.exists(target.format(scraping_module="scraping")):
    CSV_FILE = csv.reader(open(target.format(scraping_module="scraping")))
elif os.path.exists(target.format(scraping_module="amcatscraping")):
    CSV_FILE = csv.reader(open(target.format(scraping_module="amcatscraping")))


INDEX_URL = "https://www.twitter.com"
DATA_URL = "https://twitter.com/i/profiles/show/{screenname}/timeline/with_replies?include_available_features=1&include_entities=1"

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
from lxml import html



class TwitterPoliticiScraper(HTTPScraper, DBScraper):
    medium_name = "Twitter"

    def __init__(self, *args, **kwargs):
        super(TwitterPoliticiScraper, self).__init__(*args, **kwargs)
        self.notfound = open('readme.txt','w')

    def _login(self, username, password):
        
        POST_DATA = {
            'email' : username,
            'password' : password
        }
        self.open(INDEX_URL, urlencode(POST_DATA))

    def fix_row(self, row):
        #as of 2013-05-28 the csv file has a strange format in an unknown dialect
        #this is a quick fix in wait of a more elegant solution
        n_row = row[:]
        for item in row:
            n_row = unicode(item, 'utf-8')
        row = n_row[:]
        if len(row) > 1:
            return row
        list_initial = unicode(row[0],'utf-8').split(",")
        list_final = []
        chain = False
        for item in list_initial:
            if item.strip().startswith('"') and item.strip().endswith('"'):
                list_final.append(item)
            elif item.startswith('"'):
                chain = item.lstrip('"')
            elif item.endswith('"') and chain:
                list_final.append(chain + item.rstrip('"'))
                chain = False
            else:
                if chain:
                    chain += item
                else:
                    list_final.append(item)
        return list_final

    def _get_units(self):
        """get pages"""
        i = 0
        for row in CSV_FILE:
            row = self.fix_row(row)
            i = i + 1
            if i == 1:
                continue
            url = row[7]
            screenname = url.split("/")[-1]
            yield DATA_URL.format(screenname=screenname)

        
    def _scrape_unit(self, url):
        """gets articles from a page"""
        try:
            _json = self.open(url).read()
        except (HTTPError, URLError):
            msg = "{} twitter addres ({}) not found\n".format(row[0],row[7]).encode('utf-8')
            print(msg)
            self.notfound.write(msg)
            return

        data = json.loads(_json)
        done=False
        while data['has_more_items'] and done==False:
            doc = html.fromstring(data['items_html'])
            for div in doc.cssselect("div.tweet"):
                tweet = HTMLDocument()
                tweet.props.author = div.cssselect("strong.fullname")[0].text_content()
                tweet.props.date = datetime.fromtimestamp(float(div.cssselect("a.tweet-timestamp ._timestamp")[0].get('data-time')))
                tweet.props.text = div.cssselect("p.js-tweet-text")[0]
                maxid = div.get('data-tweet-id')
                if tweet.props.date.date() < self.options['date']:
                    done=True;break
                elif tweet.props.date.date() == self.options['date']:
                    yield tweet
            if done==False:
                nexturl = url + "&max_id={}".format(maxid)
                data = json.loads(self.open(nexturl).read())


            
        
            


if __name__ == '__main__':
    from amcat.scripts.tools import cli
    from amcat.tools import amcatlogging
    amcatlogging.debug_module("amcat.scraping.scraper")
    amcatlogging.debug_module("amcat.scraping.document")
    cli.run_cli(TwitterPoliticiScraper)


