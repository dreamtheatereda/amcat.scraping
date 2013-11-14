from kamervragen_vraag import KamervragenVraagScraper
from kamervragen_antwoord import KamervragenAntwoordScraper
from handelingenperspreker import HandelingenPerSprekerScraper
from kamerstukken import KamerstukkenScraper
from stemmingen import StemmingenScraper

from amcat.scripts.script import Script

from amcat.scraping.controller import scrape_logged

import logging, datetime
from amcat.scraping.controller import SimpleController

log = logging.getLogger(__name__)


class RunScraper(Script):  
    def run(self, _input):
        startdate = datetime.date(2013,7,1)
        lastdate = datetime.date(2013,11,05)        
        dateinterval = 1
        
    
        date = startdate
        while date <= lastdate:
            print('------------------', date)
           
            scrapers = []
            scrapers.append(HandelingenPerSprekerScraper(date=date, articleset=2245, project=34))
            #scrapers.append(KamervragenVraagScraper(date=date, articleset=414, project=15))
            #scrapers.append(KamervragenAntwoordScraper(date=date, articleset=418, project=15))
            #scrapers.append(StemmingenScraper(date=date, articleset=3447, project=15))

                                                    
            result = {s : [] for s in scrapers}
            counts = dict((s, 0) for s in scrapers)

            controller = SimpleController()
            for a in controller.scrape(scrapers):
                a.scraper
            
            date += datetime.timedelta(dateinterval)

if __name__ == '__main__':
    from amcat.scripts.tools import cli
   

    from amcat.tools import amcatlogging
    amcatlogging.debug_module("amcat.scraping.scraper")
    amcatlogging.debug_module("amcat.scraping.document")

    
    cli.run_cli(RunScraper)


