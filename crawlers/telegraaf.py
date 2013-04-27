from amcat.scraping.crawler import Crawler
from amcat.scraping.document import HTMLDocument
from amcat.tools.toolkit import readDate
from scraping.newssites.telegraaf import scrape_unit
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
        url = urldoc[0]
        page = HTMLDocument(url = urldoc[0])
        page.prepare(self)
        for unit in scrape_unit(self, page):
            yield unit
        
if __name__ == '__main__':
    from amcat.scripts.tools import cli
    from amcat.tools import amcatlogging
    amcatlogging.debug_module("amcat.scraping.crawler")
    amcatlogging.debug_module("amcat.scraping.scraper")
    amcatlogging.debug_module("amcat.scraping.document")
    cli.run_cli(TelegraafCrawler)

