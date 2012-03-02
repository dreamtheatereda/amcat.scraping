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

from amcat.scraping.scraper import HTTPScraper
from amcat.scraping.document import HTMLDocument

from amcat.tools import toolkit

import re

INDEX_URL = "http://borstkanker.startpagina.nl/prikbord/list.php?372,page=%d"
OFFSET = 12

get_offset = lambda row: int(row.cssselect('td[valign=top]')[0].get('width'))

class BorstkankerPrikbordScraper(HTTPScraper):
    def _get_unit(self):
        """ """
        for page in self.get_pages():
            for tr in page.cssselect('.PhorumStdTable tr')[1:]:
                a = tr.cssselect('td > a')[0]
                yield HTMLDocument(url=a.get('href'), headline=a.text)

    def get_pages(self):
        index = self.getdoc(INDEX_URL % 1); yield index
        
        pages = index.cssselect('.PhorumNavBlock a.PhorumNavLink')[-3].text
        for i in range(2, int(pages)+1):
            yield self.getdoc(INDEX_URL % i)

    def get_children(self, doc):
        rows = doc.cssselect('.PhorumStdTable > tr')

        for row in rows:
            if not row.cssselect('b'):
                continue
            
            offset = get_offset(row)
            for row in rows[rows.index(row)+1:]:
                curr_offset = get_offset(row)
                if curr_offset == offset:
                    break
                elif curr_offset == offset + OFFSET:
                    yield row.cssselect('a')[0].get('href')

    def _scrape_unit(self, page):
        # Get page info
        post = page.doc.cssselect('.PhorumStdBlock')[0]
        page.props.author = post.cssselect('.PhorumReadBodyHead strong')[0].text_content().strip()
        page.props.date = toolkit.readDate(post.cssselect('.PhorumReadBodyHead')[-1].text)
        page.props.text = post.cssselect('.PhorumReadBodyText')

        yield page

        # Get children
        current = page.doc.cssselect('.PhorumStdTable b')
        for url in self.get_children(page.doc):
            child = page.copy(parent=page)
            child.props.url = url
            child.prepare(self, force=True)

            for p in self.get(child):
                yield p


if __name__ == '__main__':
    from amcat.tools.scraping.manager import main
    main(BorstkankerPrikbordScraper)

    #from amcat.tools.scraping.exporters.builtin import Exporter
    #s = BorstkankerPrikbordScraper(Exporter())
    #doc = s.getdoc("http://borstkanker.startpagina.nl/prikbord/12236848/12341549/re-kalkdeeltjes-gevonden#msg-12341549")
    #print(len(list(s.get_children(doc))))
    #s.quit()
