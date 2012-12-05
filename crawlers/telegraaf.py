from amcat.scraping.crawler import Crawler
from amcat.scraping.document import HTMLDocument,Document
from amcat.tools.toolkit import readDate
import re


class TelegraafCrawler(Crawler):
    medium_name = "telegraaf.nl"
    initial_url = "http://www.telegraaf.nl"
    include_patterns = [
        re.compile("http://www.telegraaf.nl"),
        ]
    deny_patterns = [
        re.compile("/wuz/")
        ]


    def article_url(self, url):
        pattern = re.compile("/\d+/__[a-zA-Z0-9_]+__.html")
        if pattern.search(url):
            return True
        else:
            return False


    def _scrape_unit(self, urldoc):
        page = HTMLDocument(url = urldoc[0])
        page.doc = urldoc[1]

        try:
            page.props.date = readDate(page.doc.cssselect("span.datum")[0].text_content())
        except (IndexError,AttributeError) as e: #wrong page or empty page
            print(e)
            return
        page.props.author = "Unknown"
        page.props.headline = page.doc.cssselect("#artikel h1")[0].text_content().strip()
        page.doc.cssselect("div.broodMediaBox")[0].drop_tree()
        page.props.text = page.doc.cssselect("#artikelKolom")[0].text_content()
        page.props.section = page.doc.cssselect("#breadcrumbs a")[-1].text
        for comment in self.scrape_comments(page):
            yield comment



        yield page

    def scrape_comments(self,page):
        p = page.props.url+"?page={}"
        if not page.doc.cssselect("ul.pager"):
            return
        total = int(page.doc.cssselect("ul.pager li.pager-last a")[0].get('href').split("page=")[-1].split("&")[0]) + 1
        docs = [self.getdoc(p.format(x)) for x in range(total)]
        for doc in docs:
            for div in doc.cssselect("#comments div.comment"):
                comment = Document()
                comment.props.text = div.cssselect("div.content")[0].text_content()
                comment.props.author = div.cssselect("span.submitted-username")[0].text_content()
                comment.props.date = readDate(div.cssselect("div.submitted div.floatr")[0].text_content())
                comment.parent = page
                yield comment
        
if __name__ == '__main__':
    from amcat.scripts.tools import cli
    from amcat.tools import amcatlogging
    amcatlogging.debug_module("amcat.scraping.crawler")
    amcatlogging.debug_module("amcat.scraping.scraper")
    amcatlogging.debug_module("amcat.scraping.document")
    cli.run_cli(TelegraafCrawler)

