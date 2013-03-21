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

from urllib import urlencode
from urlparse import urljoin
import json
import math
import re
import logging;log = logging.getLogger(__name__)
from lxml.html.soupparser import fromstring
from datetime import date
from amcat.scraping import toolkit
from amcat.tools.toolkit import readDate

STORE_INDEX_URL = "http://store.steampowered.com/search/results?sort_order=ASC&page={}&snr=1_7_7_230_7"
APP_INDEX_URL = "http://steamcommunity.com/app/{appid}"
COMMENT_DATA_URL = "http://steamcommunity.com/comment/{type}/render/{id1}/{id2}/"
PLAYERS = {}

from amcat.scraping.scraper import HTTPScraper

class SteamScraper(HTTPScraper):
    medium_name = "steamcommunity.com"
    
    classes = set([])
    
    def __init__(self, *args, **kwargs):
        super(SteamScraper, self).__init__(*args, **kwargs)
        self.open("http://steamcommunity.com")

    def _get_units(self):
        for appid, url in self.get_app_urls():
            try:
                self.current_app = self.getdoc(url).cssselect("title")[0].text.split("::")[1].strip()
                discussions_url = url + "/discussions"
                for unit in self.get_discussions(discussions_url):
                    yield (unit, "discussion")
                subsections = [2,3]
                for s in subsections:
                    try:
                        for unit in self.get_media_units(appid, s):
                            yield (unit, "media")
                    except Exception:
                        log.exception("subsection failed")
            except Exception: #no exceptions approach, this scraper runs for a long time
                log.exception("app failed")
                


    def get_app_urls(self):
        print(STORE_INDEX_URL.format(1))
        app_index = self.getdoc(STORE_INDEX_URL.format(1))
        totalpages = int(app_index.cssselect("div.search_pagination_right a")[-2].text)
        pattern = re.compile("http://store.steampowered.com/app/(\d+)/")
        appids = set([])

        for page in range(totalpages):
            try:
                url = STORE_INDEX_URL.format(page+1)
                doc = self.getdoc(url)
            except Exception as e:
                continue
            for app in doc.cssselect("#search_result_container a.search_result_row"):
                try:
                    href = app.get('href')
                except Exception as e:
                    continue
                match = pattern.search(href)
                if match:
                    try:
                        appid = match.group(1)
                        yield (appid, APP_INDEX_URL.format(**locals()))

                    except Exception:
                        continue

    

    def get_media_units(self, appid, subsection):
        media_url = "http://steamcommunity.com/app/{appid}/homecontent/?l=english&p={p}&itemspage={p}&itemsfilter=trend&screenshotspage={p}&screenshotsfilter=trend&videospage={p}&videosfilter=trend&artpage={p}&artfilter=trend&webguidepage={p}&webguidefilter=trend&discussionspage={p}&appHubSubSection={subsection}&browsefilter=toprated&searchText="
        
        p = 0
        doc = self.getdoc(media_url.format(**locals()))
        while doc is not None:
            url = media_url.format(**locals())
            doc = self.getdoc(url)
            for div in doc.cssselect("div.apphub_Card"):
                yield div

            p += 1



    def get_discussions(self, url):
        forum_id = self.getdoc(url).cssselect("div.forum_area")[0].get('id').split("_")[2]
        for topic in self.get_topics(forum_id):
            yield topic
            
    def get_topics(self, forum_id):
        url = "http://steamcommunity.com/forum/{}/General/render/0/?start={}&count=15"
        initial_json = self.open(url.format(forum_id,0)).read()
        initial_data = json.loads(initial_json)
        total = initial_data['total_count']
        html = fromstring(unicode(initial_data['topics_html']).encode('utf-8').decode('string_escape'))
        yield self.getdoc(html.cssselect("a")[0].get('href'))

        page = 1
        while page * 15 < total:
            data = json.loads(self.open(url.format(forum_id, page * 15)).read())
            try:
                html = fromstring(unicode(data['topics_html']).encode('utf-8').decode('string_escape'))

            except ValueError:
                pass
            else:
                yield self.getdoc(html.cssselect("a")[0].get('href'))
            page += 1

    def _scrape_unit(self, htmltype): 
        (html,_type) = htmltype
        if _type == "media":
            url = html.get('onclick').split("(")[1].split("', '")[0].lstrip(" '")
            doc = self.getdoc(url)

            for item in self.scrape_media(doc,_type):
                item.game = self.current_app
                yield item
            
        elif _type == "discussion":
            for item in self.scrape_discussion(html):
                item.game = self.current_app
                yield item

    def scrape_comments(self, parent):
        doc = parent.doc
        i = 0
        while doc is not None:
            for div in doc.cssselect("div.commentthread_comment"):
                comment = HTMLDocument()
                author_url = div.cssselect("a.commentthread_author_link")[0].get('href')
                comment = self.get_author_props(comment, author_url)
                comment.props.text = div.cssselect("div.commentthread_comment_text")[0]
                try:
                    comment.props.date = readDate(div.cssselect("span.commentthread_comment_timestamp")[0].text)
                except ValueError:
                    comment.props.date = date.today()
                comment.parent = parent
                yield comment

            i += 1
            
            doc = self.getdoc_comments(parent.doc, i)




    def getdoc_comments(self, parent, i):
        data = parent.cssselect("div.commentthread_area")[0].get('id').split("_")
        id1 = data[2]
        id2 = data[3]
        type = data[1]
        url = COMMENT_DATA_URL.format(**locals())
        post = {
            'start' : i * 50 - 40,
            'count' : 50,
            'sessionid' : [r for r in parent.cssselect("input") if r.get('name') == "sessionid"][0].get('value')
            }
        json_doc = self.open(url, urlencode(post)).read()
        
        data = json.loads(json_doc)
        try:
            str_html = unicode(data['comments_html'])
            str_html = str_html.encode('utf-8')
            str_html = str_html.decode('string_escape')
        except KeyError:
            return None

        doc = fromstring(str_html)
        
        if len(str_html) > 0:
            return doc
        else:
            return None
        

    def scrape_discussion(self,doc):
        disc = HTMLDocument()
        disc.doc = doc
        disc.props.headline = doc.cssselect("div.forum_op div.topic")[0].text
        disc.props.text = doc.cssselect("div.forum_op div.content")[0]
        try:
            disc.props.date = readDate(doc.cssselect("span.date")[0].text)
        except ValueError:
            disc.props.date = date.today()
        author_url = doc.cssselect("a.forum_op_author")[0].get('href')
        disc = self.get_author_props(disc,author_url)

        for comment in self.scrape_comments(disc):
            yield comment

        yield disc


    def scrape_media(self,doc,_type):
        scrn = HTMLDocument()
        scrn.doc = doc
        try:
            scrn.props.text = scrn.doc.cssselect("div.mediaDescription")[0]
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
            for comment in self.scrape_comments(scrn):
                yield comment
        else:
            raise NotImplementedError

        yield scrn
            
    def get_author_props(self,document, author_url):
        document.props.author = author_url
        if author_url not in PLAYERS.keys():
            meta = self.get_author_meta(author_url)
            document.props.author_meta = meta
            PLAYERS[author_url] = meta
        else:
            document.props.author_meta = PLAYERS[author_url]
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


