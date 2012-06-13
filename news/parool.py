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

from amcat.scraping.scraper import HTTPScraper, DatedScraper
from amcat.scraping.document import HTMLDocument

from amcat.tools import toolkit
#from amcat.model.medium import Medium

from urlparse import urljoin
import datetime

class ParoolScraper(HTTPScraper, DatedScraper):
    medium_name = 'Parool'
    index_url = "http://www.parool.nl/"
        
    def _get_units(self):
        date = self.options['date']
        if date == datetime.date.today():
            for li in self.getdoc(self.index_url).cssselect('.art_box8 li'):
                href = li.cssselect('a')[0].get('href')
                href = urljoin(self.index_url, href)
                yield HTMLDocument(url=href)
        else:
            print( 'blaat' )

    def _scrape_unit(self,doc):
        doc.doc = self.getdoc(doc.props.url)
        doc.props.headline = doc.doc.cssselect('.k20')[0].text
        datum = doc.doc.cssselect('.time_post')[0].text
        doc.props.date = toolkit.readDate(datum)
        articlebody = doc.doc.cssselect('.art_box2')[0]
        print(repr(articlebody.text_content()))
        articlebody.cssselect('.k20')[0].drop_tree()
        articlebody.cssselect('.time_post')[0].drop_tree()
        try:
            articlebody.cssselect('script')[0].drop_tree()
        except:
            pass
        articlebody = articlebody.text_content().strip()
        doc.props.text = articlebody
        doc.props.author = '' # zeer inconsistent weergegeven, meestal ANP
        yield doc


if __name__ == '__main__':
    from amcat.scripts.tools import cli
    from amcat.tools import amcatlogging
    amcatlogging.debug_module("amcat.scraping.scraper")
    amcatlogging.debug_module("amcat.scraping.document")
    cli.run_cli(ParoolScraper)
