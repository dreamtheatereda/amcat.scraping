import pycurl, json, urllib
import os

STREAM_URL = "https://stream.twitter.com/1/statuses/filter.json"

USER = "floorter"
PASS = ""

DATA_PATH = "."

def on_receive(data):
	if data.strip(): # Ignore keepalive empty lines
		data = json.loads(data)
		f = open(os.path.join(DATA_PATH, "%d.json" % (data["id"])), "w")
		json.dump(data, f)
		f.close()
		print "%s: %s" % (data["user"]["name"], data["text"])

post = {
	"track": "nuon, ajax",
	"follow": "1,2,3,4",
}

conn = pycurl.Curl()
conn.setopt(pycurl.USERPWD, "%s:%s" % (USER, PASS))
conn.setopt(pycurl.POSTFIELDS, urllib.urlencode(post))
conn.setopt(pycurl.URL, STREAM_URL)
conn.setopt(pycurl.WRITEFUNCTION, on_receive)
conn.perform()

