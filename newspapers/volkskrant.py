# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import
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

import datetime
import urllib2
import urllib
import uuid

from amcat.scraping.scraper import DBScraper, HTTPScraper
from amcat.scraping.document import HTMLDocument, IndexDocument
from amcat.scraping import toolkit

# PyAMF imports
import pyamf
from pyamf import remoting
from pyamf.flex import messaging

# Logging
import logging; log = logging.getLogger(__name__)

# Login page
LOGINURL = "https://caps.volkskrant.nl/service/login"

# AMF API page
AMFURL = "http://krant.volkskrant.nl/ipaper-online/blaze/amf"

# Text displayed when login successfull
LOGIN_SUCCESS = "Log In Successful"

# Generate a valid uuid for an AMF object
uuid4 = lambda: str(uuid.uuid4()).upper()

# Volkskrant ID's
MAIN_ID = 8002
REGIO_CODE = "NL"

# Convienience function
def get_pubdate(paper):
    pd = dict([(k, int(v)) for k,v in paper['pubDate'].items()])
    pd['month'] += 1

    return datetime.date(**pd)

class VolkskrantScraper(HTTPScraper, DBScraper):
    """
    The Volkskrant uses a Flash based framework called iPaper. We
    communicate through AMF objects. For more information:

        http://code.google.com/p/amcat/wiki/iPaperAPI

    We use PyAMF to create and serialize the objects.
    """
    medium_name = "De Volkskrant"

    def __init__(self, *args, **kwargs):
        super(VolkskrantScraper, self).__init__(*args, **kwargs)

        self.client_id = uuid4()

    def _login(self, username, password, retry=False):
        """
        Parse login form and fill in wanted parts
        """
        if not retry:
            log.info("Logging in..")
            login_page = self.getdoc(LOGINURL)

            form = toolkit.parse_form(login_page)
            form['username'] = username
            form['password'] = password

            login_page = self.opener.opener.open(
                LOGINURL, urllib.urlencode(form)
            )

            if not LOGIN_SUCCESS in login_page.read():
                log.error("Login was not successful, check credentials!")
                import sys; sys.exit(1)

            log.info("Login successful")
            log.info("Preparing API..")

        com = self.create_message(messaging.CommandMessage, operation=5)
        com.headers = {
            'DSMessagingVersion' : 1,
            'DSId' : ''
        }

        req = self.create_request(com)
        env = self.create_envelope(req)
        res = self.apiget(env).bodies[0][1]

        error = not isinstance(res.body, messaging.AcknowledgeMessageExt)

        if error and retry:
            # Error occured and this was a retry
            log.error("Handshake not accepted. Error was: %s"
                        % res.body.faultString)
            import sys; sys.exit(1)

        elif error:
            # Error occured. Retry with logged out session
            self._login(username, password, retry=True)
        else:
            log.info("Handshake successful")


    def apiget(self, envelope):
        """
        Communicate with API.

        @type envelope: pyamf.remoting.Envelope
        @param envelope: request

        @return: decoded AMF stream
        """
        data = bytes(remoting.encode(envelope).read())

        req = urllib2.Request(AMFURL, data, headers={
            'Content-Type' : 'application/x-amf'
        })

        return remoting.decode(
            self.opener.opener.open(req).read()
        )

    def create_envelope(self, *requests):
        """
        Create AMF Envelope object with embedded requests.
        """
        env = remoting.Envelope(amfVersion=pyamf.AMF3)
        env.bodies = []

        for i, req in enumerate(requests):
            env.bodies.append(("/%s" % (i+1), req))

        return env

    def create_request(self, *messages):
        """
        Create MAF Request object and embed given
        messages.
        """
        return remoting.Request("null", body=messages)

    def create_message(self, msgtype, **args):
        """
        Creates message and sets messageId, clientId and
        given keyword arguments. For documentation see:

            http://api.pyamf.org/0.6.1/pyamf.flex.messaging.\
            AbstractMessage-class.html

        Example:

            msg = self.create_message(
                pyamf.flex.messaging.RemotingMessage,
                operation="getHome"
            )
        """
        return msgtype(messageId=uuid4(), clientId=self.client_id, **args)

    def _get_units(self):
        # Get urls for last 6 newspapers
        rmsg = self.create_message(
            messaging.RemotingMessage,
            operation="getHome", body=[MAIN_ID],
            destination="onlineFacade"
        )

        req = self.create_request(rmsg)
        env = self.create_envelope(req)
        resp = self.apiget(env).bodies[0][1].body.body['homePapers']

        # Create date:paper dictionary and check for date
        pages = dict([(get_pubdate(p), p) for p in resp])
        page = pages.get(self.options['date'])

        if page is None:
            log.error("Page for this date could not be found!")
            import sys; sys.exit(1)

        print(page)

        return []

    def _scrape_unit(self, ipage): # ipage --> index_page
        pass

if __name__ == '__main__':
    from amcat.scripts.tools import cli
    from amcat.tools import amcatlogging
    amcatlogging.debug_module("amcat.scraping.scraper")
    amcatlogging.debug_module("amcat.scraping.document")
    cli.run_cli(VolkskrantScraper)
