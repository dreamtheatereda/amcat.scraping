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



#this file can be used for:

#BN DeStem
#Brabants Dagblad
#De Gelderlander
#De Stentor
#De Twentsche Courant 
#Tubantia
#Eindhovens Dagblad
#PZC


import re, collections
from itertools import count

from amcat.tools import toolkit

def clean(text):
    """Clean the javascript document before parsing"""

    text = text.decode('iso-8859-1',errors='replace')
    text = re.sub("\x1d+[\dA-Z]", " ", text)
    text = text.replace("-\x1e","")
    text = text.replace("\x1e","")
    text = re.sub("[ \t]+", " ", text)
    
    return text    

ARTICLE_IDS_PATTERN = r"a\[(\d+)\].e\[\d+\]=new mE\(\d+,(\d+)\);"

def get_article_ids(txt):
    """
    Get the list of paragraph ids per article. 
    @param txt: the cleaned js source
    @return: a sequence of articles, where each article is a list of paragraph ids
    """
    articles = collections.defaultdict(list)
    for number, parid in re.findall(ARTICLE_IDS_PATTERN, txt):
        articles[number].append(int(parid))
    return articles.values()

       
import htmlentitydefs
def decode_html_entity(entity):
    if entity.startswith("#"):
        codepoint = int(entity[1:])
    else:

        try:
            codepoint = htmlentitydefs.name2codepoint[entity]
        except KeyError:
            return entity #sometimes whole sentence gets in here somehow
    return unichr(codepoint)


def decode_html_entities(text):
    return re.sub('&([^&;]+);', lambda m: decode_html_entity(m.group(1)), text)

def _chunks_to_text(chunks):
    text = "\n".join(chunks)
    text = text.replace("\\n", "\n")
    text = decode_html_entities(text)
    text = toolkit.stripAccents(text)
    return text.strip()
                 
def get_article(txt, ids):
    """
    Get the text for an article
    @param txt: the cleaned js source
    @param ids:  a list of paragraph ids to concatenate
    @return: a string representing the text of the article
    """
    body = []
    headline = []
    byline = []
    for parid in ids:
        offset = 1

        pattern = r'p\[{parid}\].S\[\d+\]=new mS\((\d+),"([^"]*)"\);$'.format(**locals())
        m = re.findall(pattern, txt, re.MULTILINE)
        for font, chunk in m:
            if font == 0:
                byline.append(chunk)
            elif font == 1:
                headline.append(chunk)
            else:
                body.append(chunk)

    body, headline, byline = map(_chunks_to_text, [body, headline, byline])
    return body, headline, byline


###########################################################################
#                          U N I T   T E S T S                            #
###########################################################################
        
import unittest

class TestArticle(unittest.TestCase):
    def setUp(self):
        self.txt = open("tubantia_test.html").read()
        
    def test_clean(self):
        self.assertTrue("\x1e" in self.txt)
        cleaned = clean(self.txt)
        self.assertFalse("\x1e" in cleaned)

    def test_get_article_ids(self):
        cleaned = clean(self.txt)
        articles = list(get_article_ids(cleaned))
        self.assertIn([19,20], articles)

    def test_decode_html_entities(self):
        self.assertEqual(decode_html_entity("lt"), "<")
        self.assertEqual(decode_html_entity("#8216"), u"\u2018")

        out = decode_html_entities(u'een &#8216; boardi')
        self.assertEqual(out, u"een \u2018 boardi")


    def test_get_article(self):
        ids = [19, 20]
        expected = u"""ALMELO\n\nKlinkende namen bij stadionplan Heracles\n
Oud-KNVB-bestuurders Henk Kesler en Arie van Eijden, alsmede de oud- burgemeesters Bert Meulman (Hardenberg) en Menno Knip (Almelo) hebben zich verbonden aan het stadionplan van Heracles Almelo. De bestuurders maken deel uit van een ' boardingcommissie'. Deze kiest binnenkort een partner om het nieuwe stadion in Almelo te bouwen en te exploiteren. Vier consortia hebben daarvoor belangstelling: Ballast- Nedam, BAM, VanWijnen- Trebbe en VolkerWessels- Dura Vermeer- Bramer. De namen zijn gisteren bekend gemaakt."""
    
        cleaned = clean(self.txt)
        text = get_article_text(cleaned, ids)

        self.assertEqual(text, expected)
        

if __name__ == '__main__':
    unittest.main()
        
