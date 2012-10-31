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

from amcat.scraping.document import Document, HTMLDocument, IndexDocument

from urllib import urlencode
from urlparse import urljoin
import json
import math
from lxml import etree
import re
from lxml.html.soupparser import fromstring
from datetime import date
from amcat.scraping import toolkit
from amcat.tools.toolkit import readDate

APP_INDEX_URL = "http://store.steampowered.com/search/results?sort_order=ASC&page={}&snr=1_7_7_230_7"
CONTENT_INDEX_URL = "http://steamcommunity.com/app/{}/homecontent/?l=english"
PLAYERS = {}

from amcat.scraping.scraper import HTTPScraper

class SteamScraper(HTTPScraper):
    medium_name = "steamcommunity.com"
    
    classes = set([])
    
    def __init__(self, *args, **kwargs):
        super(SteamScraper, self).__init__(*args, **kwargs)
        
        self.open("http://steamcommunity.com")
        sesid = self.opener.cookiejar.cookiejar._cookies['steamcommunity.com']['/']['sessionid'].value

        setpreference = {
            'preference':'topicrepliesperpage',
            'sessionid':sesid,
            'value':50
            }
        self.open("http://steamcommunity.com/forum/0/0/setpreference",urlencode(setpreference))

    
    media = 0
    news = 0
    discussions = 0

    def _get_units(self):
        app_index = self.getdoc(APP_INDEX_URL.format(1))
        totalpages = int(app_index.cssselect("div.search_pagination_right a")[-2].text)
        pattern = re.compile("http://store.steampowered.com/app/(\d+)/")
        appids = set([])
        for page in range(totalpages):
            url = APP_INDEX_URL.format(page+1)
            print(url)
            doc = self.getdoc(url)
            for app in doc.cssselect("#search_result_container a.search_result_row"):
                match = pattern.match(app.get('href'))
                if match:
                    appid = match.group(1)
                    
                    app_url = CONTENT_INDEX_URL.format(appid)
                    print(app_url)
                    app_doc = self.getdoc(app_url)
                    while app_doc is not None:
                        for div in app_doc.cssselect("div.apphub_Card"):
                            commentcount = int(div.cssselect("div.apphub_CardCommentCount")[0].text)
                            if commentcount > 0:
                                yield div
                        form = toolkit.parse_form(app_doc)
                        url = app_url
                        for inp in form.items():
                            url += "&{}={}".format(inp[0],inp[1])
                        app_doc = self.getdoc(url,urlencode(form))

                print("media: "+str(self.media))
                print("news: "+str(self.news))
                print("discussions: "+str(self.discussions))

    def _scrape_unit(self, div): 
        
        url = div.get('onclick').split("(")[1].split("', '")[0].lstrip(" '")
        print(url)
        doc = self.getdoc(url)

        if div.cssselect("div.discussion"):
            for item in self.scrape_discussion(doc):
                yield item
            return

        elif "/news/" in div.get('onclick'):
            for item in self.scrape_newsitem(doc):
                yield item
            return

        _type = div.cssselect("div.apphub_CardContentType")[0].text.lower()

        if "screenshot" in _type or "video" in _type:
            for item in self.scrape_media(doc,_type):
                yield item
        else:
            
            for item in self.scrape_media(doc, _type):
                yield item



            from lxml import etree;print(etree.tostring(div))
            raise ValueError("wrong input")



    def scrape_1page_comments(self,parent):
        for div in parent.doc.cssselect("div.commentthread_comment"):
            comment = Document()
            author_url = div.cssselect("a.commentthread_author_link")[0].get('href')
            comment = self.get_author_props(comment,author_url)
            comment.props.text = div.cssselect("div.commentthread_comment_text")[0].text
            try:
                comment.props.date = readDate(div.cssselect("span.commentthread_comment_timestamp")[0].text)
            except ValueError:
                comment.props.date = date.today()
            comment.parent = parent
            yield comment



























    def scrape_discussion(self,doc):
        self.discussions+=1
        disc = HTMLDocument()
        disc.doc = doc
        disc.props.headline = doc.cssselect("div.forum_op div.topic")[0].text
        disc.props.text = doc.cssselect("div.forum_op div.content")[0].text
        try:
            disc.props.date = readDate(doc.cssselect("span.date")[0].text)
        except ValueError:
            disc.props.date = date.today()
        author_url = doc.cssselect("a.forum_op_author")[0].get('href')
        disc = self.get_author_props(disc,author_url)

        print(disc.doc.cssselect("div.forum_paging_summary")[0].text_content())
        

            
        for comment in self.scrape_1page_comments(disc):
            yield comment

        yield disc


    def scrape_newsitem(self,doc):
        self.news +=1
        newsitem = HTMLDocument()
        newsitem.doc = doc
        newsitem.props.headline = newsitem.doc.cssselect("#main_header h1")[0].text
        newsitem.props.author = newsitem.doc.cssselect("div.headline div.feed")[0].text
        try:
            newsitem.props.date = readDate(newsitem.doc.cssselect("div.headline div.date")[0].text)
        except ValueError:
            newsitem.props.date = date.today()
        newsitem.props.text = newsitem.doc.cssselect("#news div.body")[0].text_content()

        if not newsitem.doc.cssselect("div.commentthread_paging")[0].get('style'):
            for comment in self.scrape_1page_comments(newsitem):
                yield comment

        else:
            raise NotImplementedError

        yield newsitem

    def scrape_media(self,doc,_type):
        self.media +=1
        scrn = HTMLDocument()
        scrn.doc = doc
        try:
            scrn.props.text = scrn.doc.cssselect("div.mediaDescription")[0].text
        except IndexError:
            scrn.props.text = "none"

        try:
            scrn.props.headline = "{} {}".format(scrn.doc.cssselect("div.screenshotAppName")[0].text,_type)
        except IndexError:
            scrn.props.headline = "unknown"

        author_url = "/".join(scrn.doc.cssselect("div.linkAuthor a")[0].get('href').split("/")[:-2])
        scrn = self.get_author_props(scrn, author_url)

        for obj in scrn.doc.cssselect("div.rightDetailsBlock div.detailsStatRight"):
            try:
                scrn.props.date = readDate(obj.text)
            except ValueError:
                continue
            else:
                break

        if not scrn.doc.cssselect("div.commentthread_paging"):
            yield scrn;return
        if not scrn.doc.cssselect("div.commentthread_header div.commentthread_paging span")[1].text_content():
            for comment in self.scrape_1page_comments(scrn):
                yield comment
        else:
            raise NotImplementedError

        yield scrn
            

































    def get_author_props(self,document, author_url):
        print("getting author meta")
        document.props.author = author_url
        if author_url not in PLAYERS.keys():
            meta = self.get_author_meta(author_url)
            document.props.author_meta = meta
            PLAYERS[author_url] = meta
        else:
            print("already got author in list, total: {}".format(len(PLAYERS.keys())+1))
            document.props.author_meta = PLAYERS[author_url]
        print("done")
        return document


    def get_author_meta(self, url):
        profile = self.getdoc(url)
        author = {'name':'','location':'','id':url,'url':url,'aliases':[],'games':[],'groups':[]}

        try:
            author['name'] = profile.cssselect("title")[0].text_content().split("::")[2]
        except IndexError: #profile not yet set up
            author['name'] = url
            author['profile_private'] = False
            return author

        try:
            author['location'] = profile.cssselect("#profileBlock h2")[1].text
        except (UnicodeEncodeError,UnicodeDecodeError):
            author['location'] = 'error'



        private = profile.cssselect("#profileBlock p.errorPrivate")
        if private:
            author['profile_private'] = True
            return author
        author['profile_private'] = False



        games_url = url+"/games?tab=all"
        games_doc = self.getdoc(games_url)
        script = "\n".join([script.text_content() for script in games_doc.cssselect("script")])
        start = script.find("var rgGames")+14;end = script.find("\n",start)-2
        rgGames = json.loads(script[start:end])
        for game in rgGames:
            _game = {
                'name':game['name'],
                'id':game['appid'],
                'hours played':float(re.sub(",","",unicode(game['hours_forever'])))
                }
            author['games'].append(_game)

        return author




if __name__ == '__main__':
    from amcat.scripts.tools import cli
    from amcat.tools import amcatlogging
    amcatlogging.debug_module("amcat.scraping.scraper")
    amcatlogging.debug_module("amcat.scraping.document")
    cli.run_cli(SteamScraper)


