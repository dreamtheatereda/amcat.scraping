from amcat.scraping.scraper import Crawler
from amcat.scraping.document import HTMLDocument
from amcat.tools.toolkit import readDate
import re

class TestScraper(Crawler):
    medium_name = "nu.nl"
    initial_url = "http://www.nu.nl"
    include_patterns = [
        re.compile("http://www.nu.nl"),
        re.compile("http://www.nuzakelijk.nl")
        ]
    deny_patterns = [
        re.compile("nu.nl/tvgids/")
        ]


    def article_url(self, url):
        pattern = re.compile("^http://www.nu.nl/[a-zA-Z]+/\d+/[a-zA-Z0-9\-]+.html")
        if pattern.search(url):
            return True
        else:
            return False


    def _scrape_unit(self, doc):
        art = HTMLDocument()
        try:
            datestring = doc.cssselect("div.dateplace-data")[0].text_content().split("\n")[2]
        except IndexError:  
            datestring = doc.cssselect("div.dateplace span")[0].text_content()

        art.props.date = readDate(datestring)
        art.props.headline = doc.cssselect("div.header h1")[0].text_content()
        if doc.cssselect("div.content center"):
            doc.cssselect("div.content center")[0].drop_tree()
        art.props.text = doc.cssselect("div.content")[0]
        try:
            art.props.author = doc.cssselect("span.smallprint")[0].text_content().strip()
        except IndexError as e:
            print(e)
        yield art
        print("\n")
        
if __name__ == '__main__':
    from amcat.scripts.tools import cli
    from amcat.tools import amcatlogging
    amcatlogging.debug_module("amcat.scraping.scraper")
    amcatlogging.debug_module("amcat.scraping.document")
    cli.run_cli(TestScraper)


### works very well!
