#!/usr/bin/env python3
from graphbuilder import solve_mincost_problem_for_expenses
import os
import cherrypy
import uuid
import json
import itertools
import sys
import copy
from collections import OrderedDict

def struuid():
    return hex(int.from_bytes(os.urandom(4), byteorder="big"))[2:]

with open("db","r") as f:
    global db
    db = json.loads(f.read())

def exit():
    print("STOP")
    with open("db","w") as f:
        f.write(json.dumps(db))
    os._exit(0)

cherrypy.engine.signal_handler.set_handler("SIGINT", exit)

@cherrypy.popargs("jobid", "version", "access_token", "user_token", "indices")
class Pay(object):
    exposed = True
    def GET(self, *args, **kwargs):
        return "<form action='' method='post'><input type='submit' value='Mark as paid'>"
    def POST(self, jobid, version, access_token, user_token, indices):
        try:
            indices = json.loads(indices)
            assert isinstance(indices, list)
        except:
            raise cherrypy.HTTPError(400, "couldn't decode given json, or it wasn't a list")
        try:
            c = db[jobid][int(version)]["frozen"][access_token]
            d = c["graph"]

            d = d[indices[0]]
            d = d[1] # 0 is sender, 1 is paid,to,amount dicts
            d = d[indices[1]]
            assert d["to"] == c["user_tokens"][user_token]
            if d["paid"]: raise cherrypy.HTTPError(400, "already paid")
            d["paid"] = True
            return json.dumps(c["graph"])
        except (KeyError, IndexError, AssertionError):
            raise cherrypy.NotFound()

@cherrypy.popargs("jobid", "version", "access_token", "admin_token")
class Frozen(object):
    exposed = True
    def GET(self, jobid, version, access_token, admin_token):
        try:
            c = db[jobid][int(version)]
            d = c["frozen"][access_token]
            assert d["admin_token"] == admin_token
            
            return json.dumps(dict(list(d.items()) + [("people", c["people"]), ("description", c["description"])]))
        except (KeyError, IndexError, AssertionError):
            raise cherrypy.NotFound()

@cherrypy.popargs("jobid", "version")
class Freeze(object):
    exposed = True
    def POST(self, jobid, version):
        try:
            c = db[jobid][int(version)]
        except (IndexError, KeyError):
            raise cherrypy.NotFound()

        user_tokens = dict((struuid(), x[0]) for x in enumerate(c["people"]))
        graph = [(x[0], x[1].items()) for x in solve_mincost_problem_for_expenses(c).items()]
        def gennew():
            for (debtor, receivers) in graph:
                yield (debtor, [{"to": x[0], "amount": x[1], "paid": False} for x in receivers])
        graph = list(gennew())

        if "frozen" not in c: c["frozen"] = {}

        access_token = struuid()
        while access_token in c["frozen"]:
            access_token = struuid()

        admin_token = struuid()

        c["frozen"][access_token] = {"user_tokens": user_tokens, "graph": graph, "admin_token": admin_token}
        return json.dumps({"access_token": access_token, "admin_token": admin_token})
        raise cherrypy.HTTPRedirect("/frozen/{0}/{1}/{2}/{3}".format(jobid, version, access_token, admin_token))
        #return json.dumps({"description": c["description"], "graph": graph, "user_tokens": user_tokens})

@cherrypy.popargs("jobid", "version")
class Expenses(object):
    exposed = True
    def POST(self, jobid=None, version=None):
        try:
            content = json.loads(cherrypy.request.body.read().decode("utf-8")) # liste af expenses
            assert isinstance(content, dict)
        except:
            #return "could not decode"
            raise cherrypy.HTTPError(400, "couldn't decode given json, or it wasn't an object")
        if "description" not in content or "expenses" not in content or "people" not in content or len(content.keys()) > 3: return "illegal json data structure"
        if not isinstance(content["expenses"], list) or len(content["expenses"]) == 0 or len(content["expenses"][0]["whopaid"]) == 0: raise cherrypy.HTTPError(400, "expenses is not a list or has no elements")
        for i in content["expenses"]:
            if len(i["whoshouldpay"]) == 0:
                raise cherrypy.HTTPError(400, "one of the expenses has no designated payers!")
            if len(i["whopaid"]) == 0:
                raise cherrypy.HTTPError(400, "one of the expenses has no payers!")
        if not isinstance(content["people"], list) or len(content["people"]) <= 1:
            raise cherrypy.HTTPError(400, "system trivial or invalid! because: not a list, no people or only one person in 'people' property!")
        if jobid is None:
            jobid = struuid()
            while jobid in db: jobid = struuid()
            #db[jobid] = [content] # expenses, people
            db[jobid] = []
        if jobid not in db:
            raise cherrypy.NotFound()
            #return "not found: " + str(jobid) + " " + str(version)
        if version is not None:
            version = int(version)
            if len(db[jobid])-1 > version:
                raise cherrypy.HTTPError(400, "antique")
        db[jobid].append(content)
        return json.dumps({"jobid": jobid, "version": len(db[jobid])-1})
    def GET(self, jobid, version=-1):
        try:
            version = int(version)
            c = copy.deepcopy(db[jobid][version])
            del c["frozen"]
            return json.dumps(c)
        except:
            raise cherrypy.NotFound()
            #return "not found: " + str(jobid) + " " + str(version)

class Ledgers(object):
    exposed = True
    def GET(self):
        return json.dumps(list(db.keys()))


@cherrypy.popargs("jobid", "version")
class Graph(object):
    exposed = True
    def GET(self, jobid, version=-1):
        version = int(version)
        try:
            c = db[jobid][version]
        except (IndexError, KeyError):
            raise cherrypy.NotFound()
        return json.dumps({"description": c["description"], "graph": solve_mincost_problem_for_expenses(c), "people": c["people"]})

thisdir = os.path.abspath(os.path.dirname(__file__))

class App(object):
    exposed = True
    def GET(*args, **kwargs):
        return cherrypy.lib.static.serve_file(os.path.join(thisdir, "index.html"))

class Rest(object):
    pass

rest = Rest()
rest.expenses = Expenses()
rest.graph = Graph()
rest.frozen = Frozen()
rest.freeze = Freeze()
rest.pay = Pay()
rest.ledgers = Ledgers()

class Redir(object):
    exposed = True
    def GET(*args, **kwargs):
        raise cherrypy.HTTPRedirect("/app")

root = Redir()
root.rest = rest
root.app = App()

conf = {
    'global': {
       'server.socket_host': '0.0.0.0',
       'server.socket_port': 8000
    },
    '/': {
        'request.dispatch': cherrypy.dispatch.MethodDispatcher()
    },
    '/static': {
        'tools.staticdir.on': True,
        'tools.staticdir.dir': thisdir
#       'tools.staticdir.index': 'index.html',
    }
}
cherrypy.quickstart(root, '/', conf)
