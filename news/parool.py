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

INDEX_URL = "http://www.parool.nl/"

from amcat.tools.scraping.processors import HTTPScraper, CommentScraper, Form
from amcat.tools.scraping.objects import HTMLDocument

from amcat.tools import toolkit
from amcat.model.medium import Medium

from urlparse import urljoin

from django import forms

class ParoolScraper(Form):
    date = forms.DateField()

class ParoolScraper(HTTPScraper,CommentScraper):

    def __init__(self, options):
        super(ParoolScraper, self).__init__(options)
        
    def init(self):
        url = INDEX_URL
        for li in self.getdoc(url).cssselect('.art_box8 li'):
            href = li.cssselect('a')[0].get('href')
            href = urljoin(INDEX_URL, href)
            yield HTMLDocument(url=href)

    def main(self,doc):
        #print(tostring(doc.props.url))

        doc.props.headline = doc.doc.cssselect('.k20')[0].text
        doc.props.text = doc.doc.cssselect('.intro2')[0].text
        doc.props.author = doc.doc.cssselect('.intro2')[0].text.rpartition('(')[2].partition(')')[0]
        datum = doc.doc.cssselect('.time_post')[0].text
        doc.props.date = toolkit.readDate(datum)

        yield doc

    
if __name__ == '__main__':
    from amcat.scripts.tools import cli
    cli.run_cli(ParoolScraper)







