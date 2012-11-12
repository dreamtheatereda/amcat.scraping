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

from amcat.scraping.document import Document, IndexDocument


from pdfminer.pdfinterp import PDFResourceManager, process_pdf 
from pdfminer.pdfdevice import PDFDevice 
from pdfminer.converter import TextConverter 
from pdfminer.layout import LAParams 

import StringIO 

from urlparse import urljoin

INDEX_URL = "http://www.dekrantvantoen.nl/vw/edition.do?dp={paper}&altd=true&date={y:04d}{m:02d}{d:02d}"
PDF_URL = "http://www.dekrantvantoen.nl/vw/pdf.do?id=DVHN-{y:04d}{m:02d}{d:02d}-{id}"

from amcat.scraping.scraper import HTTPScraper,DatedScraper,ArchiveForm
from datetime import timedelta

class DeKrantVanToenScraper(HTTPScraper):
    options_form = ArchiveForm
    paper = ""
    medium_name = ""

    def __init__(self, *args, **kwargs):
        super(DeKrantVanToenScraper, self).__init__(*args, **kwargs)

    def _get_units(self):
        self.date = self.options['first_date']
        while self.date <= self.options['last_date']:
            
            index_dict = {
                'y' : self.date.year,
                'm' : self.date.month,
                'd' : self.date.day,
                'paper' : self.paper
                }
            url = INDEX_URL.format(**index_dict)
            stop=False
            while stop==False:
                ipage = IndexDocument(url=url)
                ipage.prepare(self)
                yield ipage
                try:
                    href = ipage.doc.cssselect("#artVwIntro table")[1].cssselect("td")[1].cssselect("a")[0].get('href')
                except IndexError:
                
                    stop=True
                else:
                    url = urljoin(url,href)
            
            


            self.date += timedelta(days=1)



        
    def _scrape_unit(self, ipage): 
        try:
            ipage.page = int(ipage.props.url.split("?id=")[1].split("-")[2])
        except IndexError:
            ipage.page = 1
        
        ipage.props.date = self.date
        onclicks = set([])
        [onclicks.add(td.get('onclick')) for td in ipage.doc.cssselect("div.pageview td")]
        articles = [onclick.split("'")[1].split("-")[2] for onclick in onclicks]

        


        for article in articles:
            art = Document()

            url_dict = {
                'y': self.date.year,
                'm': self.date.month,
                'd': self.date.day,
                'id':article
            }
            
            
            doc = self.open(PDF_URL.format(**url_dict)).read()
            art.props.text = self.pdf_to_text(doc).decode('utf-8')
            art.parent = ipage
            art.props.date = self.date
            art.coords = ""
            yield art
            ipage.addchild(art)


        yield ipage



            
    def pdf_to_text(self,data): 
    
        fp = StringIO.StringIO() 
        fp.write(data) 
        fp.seek(0) 
        outfp = StringIO.StringIO() 
        
        rsrcmgr = PDFResourceManager() 
        device = TextConverter(rsrcmgr, outfp, laparams=LAParams()) 
        process_pdf(rsrcmgr, device, fp) 
        device.close() 

        t = outfp.getvalue() 
        outfp.close() 
        fp.close() 
        return t
            
         



if __name__ == '__main__':
    from amcat.scripts.tools import cli
    from amcat.tools import amcatlogging
    amcatlogging.debug_module("amcat.scraping.scraper")
    amcatlogging.debug_module("amcat.scraping.document")
    cli.run_cli(DeKrantVanToenScraper)


