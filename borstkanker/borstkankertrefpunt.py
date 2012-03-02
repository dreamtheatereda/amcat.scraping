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

from amcatcraping.processors import HTTPScraper
from amcat.scraping.document import HTMLDocument
#from amcat.scraping import toolkit as stoolkit

from amcat.tools import toolkit

INDEX_URL = "http://borstkankertrefpunt.weblog.nl/page/%(page)s/"

class BorstkankerTrefpuntScraper(HTTPScraper):
    def __init__(self, exporter, max_threads=None):
        super(BorstkankerTrefpuntScraper, self).__init__(exporter, max_threads=max_threads)

    def _get_unit(self):
        """
        """
        for i in range(1, 10**6):
            doc = self.getdoc(INDEX_URL % dict(page=i))
            for post in doc.cssselect('.post'):
                a = post.cssselect('a')[0]
                href = a.get('href')
                
                yield HTMLDocument(url=a.get('href'),
                                   headline=a.text_content())

            if not doc.cssselect('.post'):
                break


    def _scrape_unit(self, page):
        date = page.doc.cssselect('.meta')[0].text_content().replace('Door borstkankertrefpunt op', ',')

        page.props.date = toolkit.readDate(date.strip())
        page.props.text = page.doc.cssselect('.entry')

        yield page
    
        for comm in page.doc.cssselect('#comments .comment'):
            ca = page.copy(parent=page)
            ca.props.author = comm.cssselect('.comment-meta.commentmetadata .fn')[0].text_content()
            ca.props.url = comm.cssselect('a')[0].get('href')
            ca.props.text = comm.cssselect('.comment-body')

            yield ca


if __name__ == '__main__':
        from amcat.tools.scraping.manager import main
        main(BorstkankerTrefpuntScraper)
