#!/usr/bin/python2.6
import json
import sys
import time

try:
    unicode
except NameError:
    unicode = str

try:
    next
except NameError:
    next = lambda gen: gen.next()

try:
    from io import StringIO as sio
except:
    from stringIO import StringIO as io

from amcat.db import dbtoolkit; db=dbtoolkit.amcatDB()
from amcat.models.article import Article, ArticleText, ArticlePost

PROPS = ['headline', 'byline', 'section', 'date', 'pagenr',
         'url', 'externalid', 'text', 'medium']

BATCH = int(sys.argv[1])
IDS = {}

def create_article(art):
    aid, pid = art['id'], art['parent']

    del art['id']
    del art['parent']

    args = dict(metastring={})
    for k,v in art.items():
        if k in PROPS:
            args[str(k)] = v
        else:
            args['metastring'][k] = v

    args['metastring'] = unicode(args['metastring'])
    args['length'] = len(args['text'])

    text = args['text']
    del args['text']

    new_aid = Article.create(db, batch=BATCH, **args).id
    ArticleText.create(db, article=id, text=text, type=2, insertuserid=2, encoding=2)

    IDS[aid] = new_aid
    if pid is not None:
        pid = IDS[pid]
        create_comment(pid, new_aid)

    return aid

def create_comment(pid, cid):
    ArticlePost.create(db, article=cid, parent=pid)

def main(path):
    js = open(path)

    count = 0
    io = sio()
    for l in js:
        if l.startswith('}'):
            io.write('}')

            io.seek(0)
            art = json.load(io)
            io = sio()

            create_article(art)

            count += 1
            if not count % 500:
                print(count)
                db.commit()
                
        elif l.startswith('['):
            pass
        elif l.startswith(']'):
            pass
        else:
            io.write(l)
    db.commit()

if __name__ == '__main__':
    main(sys.argv[2])