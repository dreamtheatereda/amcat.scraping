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

#possibly useful imports:

#from urllib import urlencode
from urlparse import urljoin
from amcat.tools import toolkit
import json
import math
from lxml import etree
import re
from lxml.html.soupparser import fromstring
from datetime import date

INDEX_URL = "http://steamcommunity.com/apps"
FORUM_URL = "http://steamcommunity.com/forum/{f_id}/General/render/0/?start={start}&count=15"
PLAYERS = {}


from amcat.scraping.scraper import HTTPScraper,DBScraper,DatedScraper,Scraper

class SteamScraper(HTTPScraper):
    medium_name = "steamcommunity.com"

    def __init__(self, *args, **kwargs):
        super(SteamScraper, self).__init__(*args, **kwargs)

    def _get_units(self):
        index = self.getdoc(INDEX_URL) 
        for unit in index.cssselect('#popular1 a'):
            CURRENT_GAME = unit.cssselect("span.appHubTitle")[0].text.strip()
            href = unit.get('href')
            self.opener.opener.addheaders.append(('Cookie','rgDiscussionPrefs=%7B%22cTopicRepliesPerPage%22%3A50%7'))
            # ^ for more comments per page
            app = self.getdoc(href+"/discussions")
            for html in self.get_pages(app):
                for topic in html.cssselect("div.forum_topic"):
                    a = topic.cssselect("a")[0]
                    title = a.text
                    href = a.get('href')
                    yield HTMLDocument(url=href,headline=title,section=CURRENT_GAME)

    def get_pages(self,first):
        forum_id = first.cssselect("#AppHubContent div.leftcol div.forum_area")[0].get('id').split("_")[2]
        total_topics = int(re.sub(",","",first.cssselect("#forum_General_{}_pagetotal".format(forum_id))[0].text.strip()))
        for x in range(int(math.floor(total_topics/15)+1)):
            page_request = self.open(FORUM_URL.format(f_id=forum_id,start=x*15))
            print(FORUM_URL.format(f_id=forum_id,start=x*15))
            html = fromstring(json.loads(page_request.read())['topics_html'])
            yield html
            
        
    def _scrape_unit(self, topic): 
        topic.doc = self.getdoc(topic.props.url)

        a = topic.doc.cssselect("div.forum_op div.authorline a.forum_op_author")[0]

        topic = self.get_author_props(topic,a)
        
        topic.props.text = topic.doc.cssselect("div.forum_op div.content")[0].text_content()
        topic.props.headline = topic.doc.cssselect("div.forum_op div.topic")[0].text_content().strip()

        _date = topic.doc.cssselect("div.forum_op span.date")[0].text.split("@")[0]
        try:
            topic.props.date = toolkit.readDate(_date)
        except ValueError: #holds value like 'x minutes ago'
            topic.props.date = date.today()

        for _comment in topic.doc.cssselect("div.commentthread_comment"):
            comment = Document()
            a = _comment.cssselect("a.commentthread_author_link")[0]
            comment = self.get_author_props(comment,a)
            comment.props.text = _comment.cssselect("div.commentthread_comment_text")[0].text_content()
            _date = _comment.cssselect("span.commentthread_comment_timestamp")[0].text.split("@")[0]
            try:
                comment.props.date = toolkit.readDate(_date)
            except ValueError:
                comment.props.date = date.today()
            comment.props.headline = "Re: {}".format(topic.props.headline)
            comment.parent = topic
            comment.props.section = topic.props.section
            yield comment

        yield topic
            

    def get_author_props(self,document, a):
        author_onclick = a.get('onclick')
        start = author_onclick.find("(");end = author_onclick.find(")",start)
        args = [arg.strip("' ()") for arg in author_onclick[start:end].split(",")]
        document.props.author = args[5]
        document.props.author_text = args[6]
        
        author_url = a.get('href')
        if author_url not in PLAYERS.keys():
            meta = self.get_author_meta(author_url,args[5])
            document.props.author_meta = meta
            PLAYERS[author_url] = meta
        else:
            print("already got author in list, total: {}".format(len(PLAYERS.keys())+1))
            document.props.author_meta = PLAYERS[author_url]
        return document



    def get_author_meta(self, url, _id):
        profile = self.getdoc(url)
        author = {'name':'','location':'','url':'','id':_id,'url':url,'aliases':[],'games':[],'groups':[]}

        try:
            author['name'] = profile.cssselect("title")[0].text_content().split("::")[2]
        except IndexError: #profile not yet set up
            author['name'] = _id
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



        groups_url = url+"/groups"
        groups_doc = self.getdoc(groups_url)
        for group in groups_doc.cssselect("#BG_bottom div.resultItem"):
            a = group.cssselect("a.linkTitle")[0]
            _group = {
                'name':a.text_content(),
                'url':a.get('href'),
                'tag':a.get('href').split("/")[-1]
                }
            author['groups'].append(_group)

        return author


if __name__ == '__main__':
    from amcat.scripts.tools import cli
    from amcat.tools import amcatlogging
    amcatlogging.debug_module("amcat.scraping.scraper")
    amcatlogging.debug_module("amcat.scraping.document")
    cli.run_cli(SteamScraper)


