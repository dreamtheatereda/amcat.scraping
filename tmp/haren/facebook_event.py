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

from amcat.scraping.document import Document, HTMLDocument, IndexDocument

import json
from datetime import datetime

POSTS = "http://cohen-doe-er-je-voordeel-mee.nl/posts/{}/50"
COMMENTS = "http://cohen-doe-er-je-voordeel-mee.nl/comments/{}"

from amcat.scraping.scraper import HTTPScraper

class FBHarenEventScraper(HTTPScraper):
    medium_name = "Facebook event project x Haren"

    def __init__(self, *args, **kwargs):
        super(FBHarenEventScraper, self).__init__(*args, **kwargs)
        
    def _get_units(self):
        i = 0
        _text = self.open(POSTS.format(i)).read()
        while i < 10000:
            _json = json.loads(_text)
            for unit in _json:
                yield unit
            i += 50
            _text = self.open(POSTS.format(i)).read()

        
    def _scrape_unit(self, doc): 

        post = Document()
        post.doc = doc
        post.props.date = datetime.fromtimestamp(post.doc['created_time'])
        post.props.author = "{} | {}".format(post.doc['from_id'],post.doc['from'])
        post.props.text = post.doc['message']
        post.props.likes = post.doc['likes']

        comments = json.loads(self.open(COMMENTS.format(post.doc['id'])).read())
        for _comment in comments:
            comment = Document(parent=post)
            comment.props.date = datetime.fromtimestamp(_comment['created_time'])
            comment.props.author = "{} | {}".format(_comment['from_id'],_comment['from'])
            comment.props.text = _comment['message']
            comment.props.likes = _comment['likes']

            yield comment

        yield post
        



if __name__ == '__main__':
    from amcat.scripts.tools import cli
    from amcat.tools import amcatlogging
    amcatlogging.debug_module("amcat.scraping.scraper")
    amcatlogging.debug_module("amcat.scraping.document")
    cli.run_cli(FBHarenEventScraper)


