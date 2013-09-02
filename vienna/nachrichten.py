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

from urllib import urlencode
from urlparse import urljoin
from random import randint
import json
from lxml import html

from amcat.scraping.document import  HTMLDocument
from amcat.scraping.scraper import HTTPScraper, DatedScraper
from amcat.tools.toolkit import readDate
from amcat.scraping.toolkit import parse_form

class NachrichtenScraper(HTTPScraper, DatedScraper):
    medium_name = "nachrichten.at"
    index_url = "http://nachrichten.at/archiv/"
    search_url = "http://www.nachrichten.at/_fWS/json/GlobalSearch/artikelarchiv/triggerSearch/?r={random}"

    def _get_units(self):
        for page in self.get_pages():
            for div in page.cssselect("div.archivsuche_suche_hit"):
                a = div.cssselect("a")[0]
                yield HTMLDocument(url = urljoin(self.index_url,a.get('href')),
                                   headline = a.text)

    def get_pages(self):
        index = self.getdoc(self.index_url)
        form = parse_form(index.cssselect("#globalesucheContainer")[0])
        page_1 = self.getpage(0, form)
        yield page_1
        n_pages = int(page_1.cssselect("a.pager-pagenr")[-2].text)
        for x in range(1, n_pages+1):
            yield self.getpage(x, form)

    def getpage(self, pagenum, form):
        random = randint(1000000000,9999999999)
        post = urlencode(self.build_post(form, page = pagenum))
        response = json.loads(self.open(self.search_url.format(**locals()), post).read())
        response_html = html.fromstring(response['data'])
        return response_html.cssselect("#plugin_artikelarchiv")[0]

    def build_post(self, form, page=0):
        form["gs[plugin-settings][artikelarchiv][start]"] = page
        form["gs[parameter][date][fromday]"] = self.options['date'].day
        form["gs[parameter][date][frommonth]"] = self.options['date'].month
        form["gs[parameter][date][fromyear]"] = self.options['date'].year
        for var in ('day','month','year'):
            form["gs[parameter][date][from{var}]".format(**locals())] = getattr(self.options['date'], var)
            form["gs[parameter][date][to{var}]".format(**locals())] = getattr(self.options['date'], var)
        form["gs[availablePlugins]"] = "artikelarchiv,ressortpromotion"
        form["gs[parameter][sortfield]"] = "newest"
        form["gs[parameter][ressort]"] = "Start (2)"
        form[""] = "Ressort wählen".encode('utf-8')
        form["gs[parameter][catchmentarea][standort]"] = ""
        form["gs[parameter][catchmentarea][radius]"] = ""
        post = {"fWScontext":"/archiv/",
                "fWSin":json.dumps(form)}
        return post

    german_months = ["Januar","Februar","März","April","Mai","Juni","Juli","August","September","Oktober","November","Dezember"]

    def _scrape_unit(self, article):
        article.prepare(self)
        date = article.doc.cssselect("span.sidebar-datum")[0].text
        for month in self.german_months:
            if month in date:
                n_month = self.german_months.index(month) + 1
                date.replace(". {month} ".format(**locals()),"-{n_month}-".format(**locals()))
                break
        article.props.date = readDate(date)
        article.props.section = article.doc.cssselect("div.u2_breadcrumb")[0].text_content().strip()
        article.props.externalid = article.props.url.split(",")[-1]
        article.props.text = article.doc.cssselect("h3.leadtext") + article.doc.cssselect("ArtikelText")
        article.props.author = article.doc.cssselect("span.sidebar-autor")[0].text
        yield article

if __name__ == '__main__':
    from amcat.scripts.tools import cli
    from amcat.tools import amcatlogging
    amcatlogging.info_module("amcat.scraping")
    cli.run_cli(NachrichtenScraper)


