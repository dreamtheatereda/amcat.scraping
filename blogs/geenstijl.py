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


from __future__ import unicode_literals, print_function, absolute_import

from datetime import datetime

from amcat.scraping.scraper import HTTPScraper, DatedScraper
from amcat.scraping.document import Document
from amcat.scraping import toolkit

class GeenstijlScraper(HTTPScraper, DatedScraper):
    medium_name = "Geenstijl"
    def __init__(self, *args, **kargs):
        super(GeenstijlScraper, self).__init__(*args, **kargs)
        
        self.index_url = "http://www.geenstijl.nl/mt/archieven/maandelijks/%(year)d/%(month)02d/"

    def _get_units(self):
        date = self.options['date']
        doc = self.getdoc(self.index_url % dict(year=date.year, month=date.month))
        listitems = doc.cssselect('div.content > ul li')
        for li in listitems:
            print(li.cssselect('a')[0])
            href = li.cssselect('a')[0].get('href')
            day = li.text[:2]
            if day == date.day:
                yield HTMLDocument(url=ref, date=self.options['date'])
            if day < date.day:
                break

    def _scrape_unit(self,doc):
        doc.doc = self.getdoc(doc.props.url)

        articles = doc.cssselect('article')
        headline = articles[0].cssselect('h1')[0].text
        footer = unit.cssselect('footer')[0].text_content.split('|')
        comment = False
        for article in articles:
            unit = doc.copy(parent=doc) if comment else doc
            if comment:
                unit.props.headline = headline + ' - comment'
                unit.props.date = toolkit.readDate(''.join(footer[1:]))
            else:
                unit.props.headline = headline
                unit.props.date = unit.cssselect('time').get('datetime')
                comment = True
        unit.props.text = unit.text_content[1:-2] 
        unit.props.author = footer[0]

if __name__ == '__main__':
    from amcat.scripts.tools import cli
    from amcat.tools import amcatlogging
    amcatlogging.debug_module("amcat.scraping.scraper")
    amcatlogging.debug_module("amcat.scraping.document")
    cli.run_cli(GeenstijlScraper)
