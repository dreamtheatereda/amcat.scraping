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


from amcat.scraping.scraper import DatedScraper, HTTPScraper
from amcat.scraping.document import HTMLDocument, IndexDocument

from amcat.tools.toolkit import readDate
from urlparse import urljoin

INDEX_URL = "http://vagz.nl/index.php/the-news"

class Vagz_nlScraper(HTTPScraper, DatedScraper):
    medium_name = "vagz.nl"

    def __init__(self, *args, **kwargs):
        super(Vagz_nlScraper, self).__init__(*args, **kwargs)


    def _get_units(self):

      
        index = self.getdoc(INDEX_URL) 
        pages = [INDEX_URL] + [urljoin(INDEX_URL,l.get('href')) for l in index.cssselect("ul.pagination li a")[3:]]
        for p in pages:
            doc = self.getdoc(p)
            articles = doc.cssselect('table.contentpane tr.sectiontableentry2')
            articles2 = doc.cssselect('table.contentpane tr.sectiontableentry1')
            articles.extend(articles2)
            for article in articles:
                date = article.cssselect('td')[2].text
                if str(self.options['date']) in str(readDate(date)):
                    link = article.cssselect('td')[1].cssselect('a')[0].get('href')
                    href = urljoin(INDEX_URL,link)
                    yield HTMLDocument(url=href, date=readDate(date))





    def noscript(self,html):
        for script in html.cssselect("script"):
            script.drop_tree()
        return html
        
    def _scrape_unit(self, page):
        page.prepare(self)
        page.doc = self.noscript(self.getdoc(page.props.url))

        forwards = page.doc.cssselect("div.article-content a")
        for f in forwards:
            if "Lees verder..." in f.text:
                link = f.get('href')
        if link:
            if len(link)>=5:
                if not "Bron: ministerie" in page.doc.cssselect("div.article-content p")[-1].text:
                    page.props.text = self.get_text(link)
                else: #VWS uses pdfs in all publications...
                    page.props.text = page.doc.cssselect("div.article-content")[0].text_content()
            else: #pdf format
                page.props.text = page.doc.cssselect("div.article-content")[0].text_content()
           
        
        if page.props.text == None:
            page.props.text = page.doc.cssselect("div.article-content")[0].text_content()
            
        yield page


    def get_text(self, link):
        doc = self.getdoc(link)
        doc = self.noscript(doc)

        text = "none"
        MEDIA = [('igz.nl','div#content'),   # based on last 100 articles, obviously not everything
                 ('onvz.nl','div.article'),  # is added but most of it is.
                 ('zorggeenmarkt.nl','div#content'),
                 ('nos.nl','div#article-content'),
                 ('zn.nl','div#newsText'),
                 ('skipr.nl','div#article'),
                 ('zonmw.nl','div.puu-section'),
                 ('zorgbelang-brabant.nl','div#inhoud'),
                 ('rijksoverheid.nl','div#content-column'),
                 ('nza.nl','div#comp_content'),
                 ('medischcontact.artsennet.nl','div.box-content'),
                 ('dbconderhoud.nl','div.article-content'),
                 ('booz.com','div#columns-1-4'),
                 ('achmeazorg.nl','td.CenteralBarContentContainer'),
                 ('rivm.nl','div#inhoudkolom'),
                 ('nivel.nl','div.panel-pane'),
                 ('volkskrant.nl','div#art_box2'),
                 ('heelkunde.nl','div.divContent'),
                 ('bmc.nl','div.node-content'),
                 ('kce.fgov.be','div.page_body'),
                 ('zorgstandaarden.nl','div#content'),
                 ('dutchhospitaldata.nl','div.tekst'),
                 ('orthopeden.org','div.column'),
                 ('rechtspraak.nl','nieuwsbericht'),
                 ('cbs.nl','div#blokken'),
                 ('nma.nl','div.GCCenter'),
                 ('nvu.nl','div#dnn_ContentPane'),
                 ('bdo.nl','div.article-content'),
                 ('trimbos.nl','div.newsdetail'),
                 ('knmg.artsennet.nl','div.box-content'),
                 ('clinicalaudit.nl','div#content'),
                 ('maastrichtuniversity.nl','div#maincontent'),
                 ('pvda.nl','div.post-content'),
                 ('nvag.nl','hoofd-discussie-container'),
                 ('vkbanen.nl','div.str_col3')
                 ]
        
        paths = [medium[1] for medium in MEDIA]
        

        #special cases
        if 'ncpf.nl' in link:
            text = doc.cssselect("table.contentpaneopen_news")[1].text_content()

        elif 'akd.nl' in link:
            text = doc.cssselect("div#purple-box div.text")[0].text_content() 
            text += doc.cssselect("div.left-column")[0].text_content()
            


        else:
            for medium in MEDIA:
                if medium[0] in link:
                    try:
                        text = doc.cssselect(medium[1])[0].text_content()
                    except IndexError as e:
                        print(e)
        if not text == "none":
            return text
        else:
            for path in paths:
                try:
                    text = doc.cssselect(path)[0]
                except IndexError:
                    pass
                else:
                    if len(text)>200:
                        break
                    else:
                        text = "none"
            if not text == "none":
                return text
            else:
                print("\nno text found for url: {}\n".format(link))
                return None
                    
                  
                  
        



if __name__ == '__main__':
    from amcat.scripts.tools import cli
    from amcat.tools import amcatlogging
    amcatlogging.debug_module("amcat.scraping.scraper")
    amcatlogging.debug_module("amcat.scraping.document")
    cli.run_cli(Vagz_nlScraper)



