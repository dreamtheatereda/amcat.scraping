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

APP_INDEX_URL = "http://store.steampowered.com/search/results?sort_order=ASC&page={}&snr=1_7_7_230_7"
CONTENT_INDEX_URL = "http://steamcommunity.com/app/{}/homecontent/?l=english"


from amcat.scraping.scraper import HTTPScraper

class SteamScraper(HTTPScraper):
    medium_name = "steamcommunity.com"

    def __init__(self, *args, **kwargs):
        super(SteamScraper, self).__init__(*args, **kwargs)

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
                    while app_doc.cssselect("div.apphub_Card"):
                        for div in app_doc.cssselect("div.apphub_Card"):
                            yield div
                        form = toolkit.parse_form(app_doc)
                        url = app_url
                        for inp in form.items():
                            url += "&{}={}".format(inp[0],inp[1])
                        app_doc = self.getdoc(url,urlencode(form))
            

    def _scrape_unit(self, div): 
        if "discussion" in div.get('class'):
            for item in self.scrape_discussion(div):
                yield item
            return

        _type = div.cssselect("div.CardContentType")[0].text.lower():
        if "video" in _type:
            for item in self.scrape_video(div):
                yield item
    
        elif "workshop item" in _type:
            for item in self.scrape_workshop_item(div):
                yield item
                
        elif "workshop collection" in _type:
            for item in self.scrape_workshop_collection(div):
                yield item
        
        ######################################################below not done








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


