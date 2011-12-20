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

INDEX_URL = ""

class NuForm(Form):
    date = forms.DateField()

class NuScraper(CommentScraper):
    options_form = NuForm
    medium = Medium.objects.get(name="nu.nl - website")

    def __init__(self, options):
        super(NuScraper, self).__init__(options)

    def init(self):
        date = self.options['date']

        print(data)

        return []

    def main(self, doc):
        return []

    def comments(self, doc):
        return []

if __name__ == '__main__':
    from amcat.scripts.tools import cli
    cli.run_cli(NuScraper)
