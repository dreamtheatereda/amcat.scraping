# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import
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

from amcat.scraping.scraper import Scraper,ScraperForm
from amcat.scraping.document import HTMLDocument
from amcat.models.article import Article
from amcat.tools import toolkit


import json
from django import forms

class TwitterFileForm(ScraperForm):
    _file = forms.CharField()


class TwitterFileScraper(Scraper):
    """Get tweets from a textfile containing output from _twitter.py"""
    medium_name = "Twitter"
    missed = 0
    n=0
    options_form = TwitterFileForm

    def _get_units(self):
        for line in open(self.options['_file'],'r').readlines():
            yield line

    def _scrape_unit(self,text):
        
        date = readDate(self.options['_file'].split("_")[2].rstrip(".txt"))
        

        yield Article(text=text,date=date)

if __name__=="__main__":
    from amcat.scripts.tools import cli
    cli.run_cli(TwitterFileScraper)
