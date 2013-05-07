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

from urllib import quote_plus
import json
import re

from amcat.scraping.scraper import DBScraper, HTTPScraper
from amcat.scraping.document import HTMLDocument
from amcat.tools.toolkit import readDate

class FDScraper(HTTPScraper, DBScraper):
    medium_name = "Het Financieele Dagblad"
    login_url_1 = "http://fd.nl/handle_login"
    login_url_2 = "http://digikrant.fd.nl/go?url=digikrant-archief.fd.nl/vw/edition.do?forward=true%26dp=FD%26altd=true%26date={self.datestring}%26uid=null%26oid=null%26abo=null%26ed=00"

    def _login(self, username, password):
        print("logging in...")

        #order of parameters matters
        parameters = "email={username}&password={password}&remember_me=&target=".format(**locals())        
        login = self.open(self.login_url_1, quote_plus(parameters, safe="=&"))

        if json.loads(login.read())["status"] != "ok":
            print(login.read())
            raise Exception("Login failed")

        self.datestring = "{d.year:04d}{d.month:02d}{d.day:02d}".format(d = self.options['date'])
        self.open("http://digikrant.fd.nl")
        self.open(self.login_url_2.format(**locals()))

    index_url = "http://digikrant-archief.fd.nl/vw/edition.do?dp=FD&altd=true&date={self.datestring}&ed=00"
    page_url = "http://digikrant-archief.fd.nl/vw/page.do?id={pageid}&pagedisplay=true&ed=00&date={self.datestring}"
    def _get_units(self):
        pageid = "FD-01-001-{self.datestring}".format(**locals())
        index = self.getdoc(self.page_url.format(**locals()))
        for pagedoc in self.get_pages(index):
            article_ids = set()
            for td in pagedoc.cssselect("#framePage td"):
                if td.get('onclick') and td.get('onclick').startswith("showArticle("):
                    article_ids.add(td.get('onclick').split("'")[1])
            for article_id in article_ids:
                yield article_id

    def get_pages(self, index):
        self.current_section = json.dumps(["Voorpagina"])
        yield index
        for option in index.cssselect("select#selectPage option")[1:]:
            self.current_section = [s.strip() for s in option.text.strip().split("-")[1].split("&")]
            if "Advertentie" in self.current_section:
                self.current_section.remove("Advertentie")
            if "Economie" in self.current_section and "Politiek" in self.current_section:
                self.current_section.remove("Economie")
                self.current_section.remove("Politiek")
                self.current_section.append("Economie & Politiek")
            self.current_section = json.dumps(self.current_section)
            pageid = option.get('value')
            page_url = self.page_url.format(**locals())
            yield self.getdoc(page_url)

    article_url = "http://digikrant-archief.fd.nl/vw/txt.do?id={article_id}"

    def _scrape_unit(self, article_id):
        article = HTMLDocument(url = self.article_url.format(**locals()))
        article.prepare(self)
        for i, table in enumerate(article.doc.cssselect("table")):
            if table.get('class') == "body":
                table_after_body = article.doc.cssselect("table")[i + 1]
        page_date = re.search(
            "Pagina ([0-9]+), ([0-9]{2}\-[0-9]{2}\-[0-9]{4})",
            table_after_body.text_content())
        article.props.pagenr = page_date.group(1)
        article.props.date = readDate(page_date.group(2))
        article.props.section = self.current_section
        article.props.headline = article.doc.cssselect("td.artheader")[0].text_content().strip()
        if article.doc.cssselect(".artsubheader"):
            article.props.byline = article.doc.cssselect(".artsubheader")[0]
        article.props.text = article.doc.cssselect("font.artbody")
        if article.doc.cssselect("td.artauthor"):
            article.props.author = article.doc.cssselect("td.artauthor")[0].text.split(":")[1].strip()
        dateline_match = re.search(
            "^([A-Z][a-z]+(( |/)[A-Z][a-z]+)?)\n\n",
            "\n".join([n.text_content() for n in article.props.text]).strip())
        if dateline_match:
            article.props.dateline = dateline_match.group(1)
            print(article.props.dateline)
                                          
        yield article

if __name__ == '__main__':
    from amcat.scripts.tools import cli
    from amcat.tools import amcatlogging
    amcatlogging.info_module("amcat.scraping")
    cli.run_cli(FDScraper)


