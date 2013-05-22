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


from pdfminer.pdfinterp import PDFResourceManager, process_pdf 
from pdfminer.pdfdevice import PDFDevice 
from pdfminer.converter import TextConverter 
from pdfminer.layout import LAParams 

import StringIO 
import re

from urllib import urlencode
from urlparse import urljoin

from datetime import timedelta

from amcat.tools.toolkit import readDate
from amcat.scraping.document import HTMLDocument
from amcat.scraping.scraper import HTTPScraper,DatedScraper,ArchiveForm

class DeKrantVanToenScraper(HTTPScraper):
    """to be subclassed by scrapers which provide a 'paper' and a 'paper_full_name'"""
    options_form = ArchiveForm
    paper = ""
    paper_full_name = ""
    medium_name = ""
    search_url = "http://www.dekrantvantoen.nl/srch/query.do?q=%20date:[{sdate.year:04d}{sdate.month:02d}{sdate.day:02d}%20TO%20{edate.year:04d}{edate.month:02d}{edate.day:02d}]%20pubcode:%20{self.paper}&from={offset}"
    pdf_url = "http://www.dekrantvantoen.nl/vw/pdf.do?id={article_id}"

    def _get_units(self):
        for page in self.search_result_pages():
            for table in page.cssselect("#containerContent table"):
                try:
                    onclick = table.cssselect("td.result a")[0].get('onclick')
                except IndexError:
                    continue
                article_id = onclick.split("('")[1].split("',")[0]

                try:
                    right_td = [td for td in table.cssselect("td") if td.get('align') == 'right'][0]
                    date = readDate(right_td.text_content())
                except IndexError:
                    continue
                
                footer = table.cssselect("span i nobr")[0].text_content()
                pagenr_section_pattern = re.compile(
                    "\({self.paper_full_name} +([a-zA-Z ]+) +, blz ([0-9]+)\)".format(**locals()))
                section, pagenr = pagenr_section_pattern.search(footer).groups()

                headline = table.cssselect("td.result a")[0].text_content().strip()

                yield (headline, date, pagenr, section.strip(), self.pdf_url.format(**locals()))
        
    def search_result_pages(self):
        sdate = self.options['first_date']
        edate = self.options['last_date']
        offset = 0
        page = self.getdoc(self.search_url.format(**locals()))
        yield page
        while len(page.cssselect("#containerContent table")) > 11:
            offset += 11
            page = self.getdoc(self.search_url.format(**locals()))
            yield page                    
        
    def _scrape_unit(self, data): 
        headline, article_date, pagenr, section, url = data
        art = HTMLDocument(
            headline = headline, date = article_date, 
            pagenr = pagenr, section = section, url = url)
        art.doc = self.open(url).read()
        text = self.pdf_to_text(art.doc).decode('utf-8')
        art.props.text = self.fix_text(text)
        art.props.source = "dekrantvantoen.nl"
        yield art
            
    def fix_text(self, text):
        text = re.sub("-\n", "", text)
        text = re.sub("([A-Za-z])\n([A-Za-z])", self.repl_newline, text)
        return text

    def repl_newline(self, match):
        return match.group(1) + " " + match.group(2)

    def pdf_to_text(self, data): 
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
    raise Exception("not to be directly used, subclass this.")


