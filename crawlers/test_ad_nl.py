from amcat.scraping.scraper import Crawler
import re

class TestScraper(Crawler):
    initial_url = "http://www.ad.nl"
    include_patterns = [
        re.compile("ad.nl"),
        ]
    deny_patterns = [
        ]

    def article_url(self, url):
        return False


    def _scrape_unit(self, doc):
        yield "something"


if __name__ == '__main__':
    from amcat.scripts.tools import cli
    from amcat.tools import amcatlogging
    amcatlogging.debug_module("amcat.scraping.scraper")
    amcatlogging.debug_module("amcat.scraping.document")
    cli.run_cli(TestScraper)
