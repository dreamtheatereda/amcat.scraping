"""One-time script to update the database with the new locations of the scrapers"""

from amcat.models.scraper import Scraper

scrapers = Scraper.objects.all()

def changes(location):
    location = "scrapers." + location.split(".",1)[1]
    if "scrapers.news." in location:
        location = "scrapers.newssites" + location.split(".")[-1]

    if "teletekst" in location:
        location = "scrapers.tv.teletekst"
    
    if "tmp" in location:
        location = "scrapers" + location.split(".tmp.")[1]

    return location
    
    
for s in scrapers:
    s.module = changes(s.module)
    print(s, s.module)
    #s.save()
