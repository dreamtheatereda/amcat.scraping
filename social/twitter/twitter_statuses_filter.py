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

"""
Script to be run continuously with possibly several sets of arguments, filtering tweets
"""

from django import forms
from amcat.scripts.script import Script
from tweepy import OAuthHandler,Stream
from tweepy.streaming import StreamListener
from os import environ
import csv
from datetime import date

consumer_key="XC92JObeStin0qEHuu08KQ"
consumer_secret="UkEZhOEPI0Ydft85PDF3S2KLrV2AlhZqXMtGVnNSEAc"
access_token="816243289-14u7zplDIiAkTf1fomp9ZUg62eDlzFspXXZv9bty"
access_token_secret="0FncNCYPgBfQvzwqV0a0kJ7Orr4mQUFsDwkPkrCvo"



TRACK_FILES_PATH="{}twitter/track/".format(environ.get('PYTHONPATH'))

class TwitterFilterForm(forms.Form):
    track_file = forms.FilePathField(TRACK_FILES_PATH,required=False)

class TwitterFilterScript(Script):
    options_form = TwitterFilterForm

    def __init__(self,*args,**kargs):
        super(TwitterFilterScript, self).__init__(*args, **kargs)

    def run(self, _input):
        if len(self.options['track_file'])<=1:
            self.options['track_file']='{}default.txt'.format(TRACK_FILES_PATH)

        words = []
        word_file = open(self.options['track_file'])
        for l in word_file.readlines():
            if not l.startswith("#"):
                [words.append(w.strip()) for w in l.strip("\n").split(",") if len(w.strip())>1]

        print(words)

        s = self.stream()
        s.filter(None,words)



    def stream(self):
        auth = OAuthHandler(consumer_key,consumer_secret)
        auth.set_access_token(access_token,access_token_secret)
        l = Listener()
        stream = Stream(auth,l)
        return stream

class Listener(StreamListener):

    def __init__(self):
        f = "{}twitter/tweets/{}".format(environ.get('PYTHONPATH'),date.today().strftime("filter_%Y-%m-%d.csv"))
        outputfile = open(f,'a+')
        self.writer = csv.writer(outputfile)
        self.i = 0

    def on_data(self,data):
        print("win!")
        self.writer.writerow(data)
        if self.i % 1:
            print("{} tweets written.".format(self.i))
        return True


    def on_error(self,status):
        print(status)




if __name__ == '__main__':
    from amcat.scripts.tools import cli
    cli.run_cli(TwitterFilterScript)
