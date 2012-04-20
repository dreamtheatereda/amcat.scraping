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
#test
import datetime
import urllib2
import urllib
import base64
import uuid

from urllib import quote

from amcat.scraping.scraper import DBScraper, HTTPScraper
from amcat.scraping.document import Document
from amcat.scraping import toolkit

# PyAMF imports
# if you get an import error, you might not have installed pyamf yet. Try:
# sudo apt-get install python-pyamf
import pyamf
from pyamf import remoting
from pyamf.flex import messaging

# Logging
import logging; log = logging.getLogger(__name__)

CHECK_CREDENTIALS = "Login was not successful, check credentials!"

# Login page
LOGINURL = "https://caps.{domain}/service/login?service=http%3A%2F%2Fkrant.{domain}%2F%3Fpaper%3D{paper_id}%26zone%3D{regio_code}"
AUTHURL = "https://caps.{domain}/service/validate?service="
SAVEURL = "http://krant.%(domain)s/ipaper-online/saveLoginHistory?zone=%(regio_code)s&pubId=%(main_id)s&method=CAPS&paperId=%(paper_id)s&login=%(username)s"

# AMF API page
AMFURL = "http://krant.{domain}/ipaper-online/blaze/amf"

# Text displayed when login successfull
LOGIN_SUCCESS = "Log In Successful"

# Generate a valid uuid for an AMF object
uuid4 = lambda: str(uuid.uuid4()).upper()

# Convienience function
def get_pubdate(paper):
    pd = dict([(k, int(v)) for k,v in paper['pubDate'].items()])
    pd['month'] += 1

    return datetime.date(**pd)

class PCMScraper(HTTPScraper, DBScraper):
    """
    The PCM papers use a Flash based framework called iPaper.
    We communicate through AMF objects. For more information:

        http://code.google.com/p/amcat/wiki/iPaperAPI

    We use PyAMF to create and serialize the objects.
    """
    domain = None # exp: ad.nl
    paper_id = None # exp: 8002
    context_id = None # exp: NL or AD

    def __init__(self, *args, **kwargs):
        super(PCMScraper, self).__init__(*args, **kwargs)

        self.ticket_url = None
        self.client_id = uuid4()
        self.headers = {
            'DSMessagingVersion' : 1,
            'DSId' : 'nil'
        }

    def _login(self, username, password, retry=False):
        """
        Parse login form and fill in wanted parts
        """
        # Get latest paper id
        latest = self._get_latest()
        latest = latest[(sorted(latest.keys())[-1])]
        paper_id = int(latest['paperId'])

        # Build url
        url = LOGINURL.format(paper_id=paper_id,
                              regio_code=self.context_id,
                              domain=self.domain)

        # Login
        log.info("Logging in..")
        login_page = self.getdoc(url)

        form = toolkit.parse_form(login_page)
        form['username'] = username
        form['password'] = password

        login_page = self.opener.opener.open(
            url, urllib.urlencode(form)
        )

        # Resolve ticket_url and save it
        #print(login_page.read())
        self.ticket_url = login_page.geturl()

        if 'ticket' not in self.ticket_url:
            log.error(CHECK_CREDENTIALS)
            raise ValueError(CHECK_CREDENTIALS)

        # Handshake server
        com = self.create_message(messaging.CommandMessage, operation=5)
        req = self.create_request(com)
        env = self.create_envelope(req)
        res = self.apiget(env).bodies[0][1]

        self.headers.update(res.body.headers)

        # Save to webserver
        url = SAVEURL % {
            'paper_id' : paper_id,
            'regio_code' : self.context_id,
            'main_id' : self.paper_id,
            'username' : quote(username).replace('.', '%2E'),
            'domain' : self.domain
        }

        req = urllib2.Request(url, data=None, headers={
            'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
        })

        self.opener.opener.open(req).read()

        # Send AMF Auth message to server
        ticket = "TICKET_%s:%s%s" % (
            self.paper_id,
            AUTHURL.format(domain=self.domain),
            quote(self.ticket_url, '&')
        )

        ticket = ticket.replace('ticket%3D', 'ticket=')
        ticket = ticket.replace('&zone', '%26zone')

        com = self.create_message(messaging.CommandMessage, operation=8)
        com.destination = 'auth'
        com.body = base64.b64encode(ticket)

        com.headers["DSEndpoint"] = "_IPaperOnlineServiceLocator_AMFChannel1"
        com.correlationId = ""

        env = self.create_envelope(self.create_request(com))
        res = self.apiget(env)

        log.info("Logged in")



    def apiget(self, envelope):
        """
        Communicate with API.

        @type envelope: pyamf.remoting.Envelope
        @param envelope: request

        @return: decoded AMF stream
        """
        data = bytes(remoting.encode(envelope).read())
        url = AMFURL.format(domain=self.domain)

        req = urllib2.Request(url, data, headers={
            'Content-Type' : 'application/x-amf'
        })

        resp = remoting.decode(
            self.opener.opener.open(req).read()
        )

        return resp

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
        msg = msgtype(messageId=uuid4(), clientId=self.client_id, **args)
        msg.headers.update(self.headers)
        return msg

    def _get_paper(self, paper_id):
        date = self.options['date']

        rmsg = self.create_message(
            messaging.RemotingMessage,
            operation="getPaper",
            body=[self.paper_id, paper_id, self.context_id],
            destination="onlineFacade"
        )

        env = self.create_envelope(self.create_request(rmsg))
        resp = self.apiget(env).bodies[0][1]

        for spread in resp.body.body['spreads']:
            for page in [spread.get(p) for p in ('leftPage', 'rightPage')]:
                if page is None: continue

                index = Document()
                index.props.date = date
                index.props.section = page.get('section')
                index.props.pagenr = index.page = page.get('nr')
                index.doc = page

                yield index

    def _get_latest(self):
        """
        Get latest newspapers
        """
        rmsg = self.create_message(
            messaging.RemotingMessage,
            operation="getHome", body=[self.paper_id],
            destination="onlineFacade"
        )

        req = self.create_request(rmsg)
        env = self.create_envelope(req)
        resp = self.apiget(env).bodies[0][1].body #.body['homePapers']

        if isinstance(resp, messaging.ErrorMessage):
            # Session was not cleared. Try again..
            return self._get_latest()

        # Create date:paper dictionary and check for date
        return dict([(get_pubdate(p), p) for p in resp.body['homePapers']])

    def _get_units(self):
        date = self.options['date']

        # Get urls for last 6 newspapers
        page = self._get_latest().get(date)

        if page is None:
            raise ValueError("Could not find paper for %s" % date)

        pid = int(page['paperId'])
        log.info("Found paper of %r with id %r" % (date, pid))

        return self._get_paper(pid)

    def _scrape_unit(self, ipage): # ipage --> index_page
        for art in ipage.doc['articles']:
            page = ipage.copy()
            page.props.author = art['author'][:100]
            page.props.headline = art['title']
            page.props.text = "\n\n".join([el['text'] for el in art['bodyElements']])

            if page.props.headline is None:
                log.warning("Skipping article (headline was None)")
                continue

            yield page.create_article()
