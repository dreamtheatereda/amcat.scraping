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

from amcat.tools.scraping.processors import CommentScraper, Form
from amcat.tools.scraping.objects import HTMLDocument
from amcat.tools.scraping import toolkit as stoolkit

from amcat.tools import toolkit
from amcat.model.medium import Medium

from django import forms

import logging
log = logging.getLogger(__name__)

#it will be easy to implement multiple paper scraping from the same makers as the code is the same
paper = "tubantia"
#1st 2nd 3rd paper (tubantia) 4th date (20120215) 5th page (tt_go-a01_120215_2.pdf.0) 6th section (Voorpagina) 7th edition(Almelo) 8th pagenum (1)
INDEX_URL = "http://{paper}.ned.newsmemory.com/eebrowser/frame/develop.4979.enea.1/php-script/fullpage.php?pSetup={paper}&file=0@/{paper}/{year}{month}{day}/{pagefile}/&section={section}&edition={edition}&pageNum={pagenum}"
MAIN_URL = "http://{paper}.ned.newsmemory.com/"
PAGES_URL = "http://{paper}.ned.newsmemory.com/eebrowser/frame/develop.4979.enea.1/load/newspaper.php?pSetup={paper}&userid=9635&date=0@/{paper}/{year}{month}{day}&flagTime={timestamp}"

#om er te komen: functie p[x].S = new mS() voegt de tekst toe, zoek die functie in firebug op tubantia.ned.newsmemory.com
#titles staan in een ander bestand, moet nog url zoeken
#alle pagina's en opties (zoals editie) staan in de HTML op elke pagina
#toe te voegen: een functie die alle variaties van de URL yield, een functie die de tekst uit de javascript-functieaanroep aanpast, een functie die de javascript-functieaanroep matcht.

class NewsmemoryForm(Form):
    date = forms.DateField()

class NewsmemoryScraper(CommentScraper):
    options_form = NewsmemoryForm

    def editions(self): #not in use
        for option in self.getdoc(MAIN_URL).cssselect('.pulldown2'):
            if option.text == "voorpagina":
                break #before voorpagina, pulldown2 contains editions. after voorpagina, sections.
            else:
                yield option.text

    def sections(self): #not in use
        for option in self.getdoc(MAIN_URL).cssselect('.pulldown2'):
            if option.text == "voorpagina":
                yieldnext = 1
                yield option.text
            else:
                if yieldnext:
                    yield option.text

    def getpages(self):
        doctext = self.getdoc(PAGES_URL).format(**locals).text
        strpos = 0
        while strpos!=-1:
            strpos = str.find(doctext,"p[i++]=new dP(",strpos+1)
            args = doctext[str.find(doctext,"(",strpos)+1:str.find(doctext,")",strpos)]
            args = str.split(args,'","')
            page = dict(pagefile = str.lstrip(args[0],'"'),section = args[1],pagenum = args[2],edition = args[3])
            yield page

    def __init__(self, options):

        s = Scraper.objects.get(class_name=NewsmemoryScraper.__name__)

        self.login_url = LOGIN_URL
        self.login_data = dict(username=s.email, password=s.password)

        super(NewsmemoryScraper, self).__init__(options)

    def init(self):
        date = self.options['date']
        year = date.year
        month = date.month
        day = date.day
        for page in getpages():
            section = page['section']
            pagefile = page['pagefile']
            pagenum = page['pagenum']
            edition = page['edition']
            url = INDEX_URL.format(**locals())
            yield HTMLDocument(url=href)


    def main(self, doc):
        doctext = str(doctext).decode('utf-8')
        doctext = re.sub("\x1d\\d", " ", doctext)
        doctext = doctext.replace("-\x1e","")
        doctext = doctext.replace("\x1e","")
        doctext = doctext.replace("\x1dC","")
        doctext = re.sub("\\s+", " ", doctext)
        doctext = doctext.encode('utf-8')
        #de tekst staat in de functieaanroep van mS
        #de artikelverdeling is bepaald door de functie mE
        #p[LINK].S[x] = new mS(x,"text")
        #a[x].e[x] = new mE(x,LINK)
        articlelinks = range(20)
        for number in articlelinks:
            strpos = 1
            linklist = str(articlelinks[number])
            while strpos>0:
                strpos = str.find(doctext,"a["+str(number)+"].e",strpos+1)
                if strpos > 0:
                    args = doctext[str.find(doctext,"(",strpos)+1:str.find(doctext,")",strpos)]
                    args = str.split(args,',')
     
                    linklist+=","
                    linklist+=args[1]
            articlelinks[number] = linklist
 
        for article in articlelinks:
            articletext = ""
            links = str.split(article,",")
            for link in links[0:]:
                strpos = str.find(doctext,"p[")
                while strpos>0:
                    
                    if strpos > 0:
                        args = doctext[str.find(doctext,"(",strpos)+1:str.find(doctext,")",strpos)]
                        args = str.split(args,',')
                        articletext += args[1]
                    strpos = str.find(doctext,"p["+str(link)+"].S",strpos+1)
            doc.props.text = articletext
            #te doen:
            #titel
            #datum
            #auteur
            yield doc
            

    def comments(self, doc):
        return []
if __name__ == '__main__':
    from amcat.scripts.tools import cli
    cli.run_cli(NewsmemoryScraper)
