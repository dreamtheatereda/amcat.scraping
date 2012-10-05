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

from amcat.scraping.phpbbscraper import PhpBBScraper
from amcat.scraping.scraper import DatedScraper
from amcat.tools.toolkit import readDate


class DeAmazonesScraper(PhpBBScraper,DatedScraper):
    index_url = "http://www.de-amazones.nl/phpbbforum/"
    medium_name = "de-amazones.nl - forum"
    i = 0
    def _scrape_unit(self, thread):
        p = 0
        fipo = True
        thread.doc = self.getdoc(thread.props.url)
        for page in self.get_pages(thread.doc):
            p += 1
            for post in page.cssselect('.post'):
                self.i += 1
                ca = thread if fipo else thread.copy(parent=thread)
                ca.props.date = readDate(post.cssselect('.author')[0].text_content()[-22:])
                ca.props.text = post.cssselect('.content')

                title = post.cssselect('.postbody h3 a')[0].text
                if fipo:
                    optitle = title
                if title:
                    ca.props.headline = title
                else:
                    ca.props.headline = 're: {}'.format( optitle )

                try:
                    ca.props.author = post.cssselect('.author strong')[0].text_content()
                except:
                    try:
                        ca.props.author = post.cssselect('.author a')[0].text_content()
                    except:
                        # Least reliable method
                        ca.props.author = post.cssselect('.author')[0].text_content().split()[0]
                
                if ca.props.date.date() == self.options['date']:        
                    yield ca

                fipo = False


if __name__ == '__main__':
    from amcat.scripts.tools import cli
    from amcat.tools import amcatlogging
    amcatlogging.debug_module("amcat.scraping.scraper")
    amcatlogging.debug_module("amcat.scraping.document")
    cli.run_cli(DeAmazonesScraper)
