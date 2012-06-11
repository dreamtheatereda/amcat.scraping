from kamervragen_vraag import KamervragenVraagScraper
from kamervragen_antwoord import KamervragenAntwoordScraper
from handelingenperspreker import HandelingenPerSprekerScraper
from amcat.scripts.script import Script

from amcat.scraping.controller import scrape_logged

import logging, datetime
from amcat.scraping.controller import SimpleController

log = logging.getLogger(__name__)




class RunScraper(Script):
  
    def run(self, _input):
        startdate = datetime.date(2010,4,26)
        #startdate = datetime.date(2005,1,1)
        lastdate = datetime.date(2012,3,31)
        dateinterval = 100
        articleset = 22847
        project = 506
        
        date = startdate

        scrapers = []
        

        while date <= lastdate:
            print('------------------', date)
            scrapers = []
            #scrapers.append(HandelingenPerSprekerScraper(date=date, articleset=articleset, project=project))
            #scrapers.append(KamervragenVraagScraper(date=date, articleset=articleset, project=project))
            scrapers.append(KamervragenAntwoordScraper(date=date, articleset=articleset, project=project))
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


