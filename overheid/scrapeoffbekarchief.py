from kamervragen_vraag import KamervragenVraagScraper
from kamervragen_antwoord import KamervragenAntwoordScraper
from handelingenperspreker import HandelingenPerSprekerScraper
from kamerstukken import KamerstukkenScraper
from amcat.scripts.script import Script

from amcat.scraping.controller import scrape_logged

import logging, datetime
from amcat.scraping.controller import SimpleController

log = logging.getLogger(__name__)


class RunScraper(Script):  
    def run(self, _input):
        startdate = datetime.date(2006,1,1)
        #startdate = datetime.date(2012,7,3)
        #astdate = datetime.date(2012,7,3)

        #lastdate = datetime.date(2011,7,22)
        lastdate = datetime.date(2012,1,1)

        
        dateinterval = 1
        #articleset = 22855 # handelingen
        #articleset = 22859 # kamervragen
        project = 15
        
        date = startdate

        scrapers = []
        

        while date <= lastdate:
            print('------------------', date)
            scrapers = []
            #scrapers.append(HandelingenPerSprekerScraper(date=date, articleset=220, project=project))
            scrapers.append(KamervragenVraagScraper(date=date, articleset=414, project=project))
            #scrapers.append(KamervragenAntwoordScraper(date=date, articleset=418, project=project))
            #scrapers.append(KamerstukkenScraper(date=date, articleset=22860, project=project))
            log.info("Starting scraping with {} scrapers: {}".format(
                len(scrapers), [s.__class__.__name__ for s in scrapers]))
            count, messages =  scrape_logged(SimpleController(), scrapers)
            date += datetime.timedelta(dateinterval)

if __name__ == '__main__':
    from amcat.scripts.tools import cli
   

    from amcat.tools import amcatlogging
    amcatlogging.debug_module("amcat.scraping.scraper")
    amcatlogging.debug_module("amcat.scraping.document")

    
    cli.run_cli(RunScraper)


