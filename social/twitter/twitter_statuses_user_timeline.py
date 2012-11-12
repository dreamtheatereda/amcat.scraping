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

import tweepy
from amcat.scraping.document import Document
from amcat.scraping.scraper import DBScraperForm, HTTPScraper, DBScraper
from urllib2 import HTTPError
from urllib import urlencode
from urlparse import urljoin
from django import forms
from amcat.scraping.toolkit import parse_form

class TwitterUserTimelineForm(DBScraperForm):
    user_id = forms.CharField(required=False)
    url = forms.CharField(required=False)
    screen_name = forms.CharField(required=False)

class TwitterStatusesUserTimelineScraper(HTTPScraper,DBScraper):
    options_form = TwitterUserTimelineForm
    medium_name = "Twitter"

    def __init__(self, *args, **kwargs):
        super(TwitterStatusesUserTimelineScraper, self).__init__(*args, **kwargs)

    def get_user_id(self, url):
        doc = self.getdoc(url)
        return doc.cssselect("div.profile-card-inner")[0].get('data-user-id')

    def _login(self, username, password):
        """requires the username/password of a twitter account
        with a registered application in dev.twitter.com.

        the consumer key/secret and acces token key/secret 
        are scraped from dev.twitter.com and put to use."""

        print("logging in...")

        login_url = "https://dev.twitter.com/user/login"
        doc = self.getdoc(login_url)
        form = parse_form(doc)
        form['name'] = username
        form['pass'] = password
        self.open(login_url,urlencode(form))

        print("...done")
        
        print("getting tokens and keys for auth...")
        appsurl = "https://dev.twitter.com/apps"
        appsdoc = self.getdoc(appsurl)

        c_k,c_s,a_t,a_t_s = 0,0,0,0
        for app in appsdoc.cssselect("#content-main ul.apps-list li"):
            try:
                href = app.cssselect("a")[0].get('href')
                authhref = "/".join(href.split("/")[:-1]) + "/oauth"
                authdoc = self.getdoc(urljoin(appsurl,authhref))
            
                c_k = authdoc.cssselect("#edit-consumer-key")[0].get('value')
                c_s = authdoc.cssselect("#edit-consumer-secret")[0].get('value')
                a_t = authdoc.cssselect("#edit-access-token")[0].get('value')
                a_t_s = authdoc.cssselect("#edit-access-token-secret")[0].get('value')

            except (IndexError, HTTPError):
                pass
            else:
                break
        if not c_k:
            raise Exception("consumer key at {} not found".format(appsurl))
        print("...done")

        auth = tweepy.OAuthHandler(c_k, c_s)
        auth.set_access_token(a_t, a_t_s)
        
        self.auth = auth


    def _get_units(self):
        self.api = tweepy.API(self.auth)

        if not (self.options['user_id'] or self.options['screen_name'] or self.options['url']):
            raise IOError("supply either a screen name, a url or a user id")

        elif (not self.options['user_id']):
            print("getting user id...")
            if not self.options['url']:
                self.options['url'] = "https://twitter.com/{}".format(self.options['screen_name'])
            self.options['user_id'] = self.get_user_id(self.options['url'])
            print("...done")





        lastid = None
        stop = False
        while stop == False:
            try:
                statuses = self.api.user_timeline(
                    user_id=self.options['user_id'],
                    count=200,
                    max_id = lastid)
            except tweepy.TweepError as e:
                if "Rate limit exceeded" in str(e):
                    raise self.RateLimitError("only 350 requests/hour allowed")

            
            import time;time.sleep(10) #only 350 requests/hour allowed

            
            for status in statuses:
                lastid = status.id
                if status.created_at.date() == self.options['date']:
                    yield status
                elif status.created_at.date() < self.options['date']:
                    stop=True;break
            
        
    class RateLimitError(Exception):
        pass

    def _scrape_unit(self, status):
        tweet = Document()
        tweet.props.author = status.author
        tweet.props.text = status.text
        tweet.props.date = status.created_at
        tweet.props.meta = status
        yield tweet
            
          
    
if __name__ == "__main__":
    from amcat.scripts.tools import cli
    from amcat.tools import amcatlogging
    amcatlogging.debug_module("amcat.scraping.scraper")
    amcatlogging.debug_module("amcat.scraping.document")
    cli.run_cli(TwitterStatusesUserTimelineScraper)
