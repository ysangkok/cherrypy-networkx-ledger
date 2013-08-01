#!/usr/bin/env python3
from graphbuilder import solve_mincost_problem_for_expenses
import os
import cherrypy
import uuid
import json

class Root(object):
    def __init__(self):
        cherrypy.engine.subscribe('start', self.start)
        cherrypy.engine.subscribe('stop', self.stop)
    def start(self):
        # TODO persistence
        print("START")
    def stop(self):
        # TODO persistence
        print("STOP")

db = dict()

@cherrypy.popargs("jobid","version")
class Expenses(object):
    exposed = True
    def POST(self, jobid=None, version=None):
        try:
            content = json.loads(cherrypy.request.body.read().decode("utf-8")) # liste af expenses
            assert isinstance(content, dict)
        except:
            #return "could not decode"
            raise cherrypy.HTTPError(400, "couldn't decode given json, or it wasn't an object")
        if "description" not in content or "expenses" not in content or "people" not in content: return "illegal json data structure"
        if not isinstance(content["expenses"], list) or len(content["expenses"]) == 0 or len(content["expenses"][0]["whopaid"]) == 0: raise cherrypy.HTTPError(400, "expenses is not a list or has no elements")
        for i in content["expenses"]:
            if len(i["whoshouldpay"]) == 0:
                raise cherrypy.HTTPError(400, "one of the expenses has no designated payers!")
            if len(i["whopaid"]) == 0:
                raise cherrypy.HTTPError(400, "one of the expenses has no payers!")
        if not isinstance(content["people"], list) or len(content["people"]) <= 1:
            raise cherrypy.HTTPError(400, "system trivial or invalid! because: not a list, no people or only one person in 'people' property!")
        if jobid is None:
            jobid = str(uuid.uuid4())
            while jobid in db: jobid = str(uuid.uuid4())
            #db[jobid] = [content] # expenses, people
            db[jobid] = []
        if jobid not in db:
            raise cherrypy.NotFound()
            #return "not found: " + str(jobid) + " " + str(version)
        olddata = {"description": "Unnamed", "expenses": [], "people": []} if len(db[jobid]) == 0 else db[jobid][-1]
        if version is not None:
            version = int(version)
            if len(db[jobid]) > version:
                return "antique"
        db[jobid].append({"expenses": olddata["expenses"] + content["expenses"], "people": olddata["people"] + content["people"], "description": content["description"]})
        return json.dumps({"jobid": jobid, "version": len(db[jobid])-1})
    def GET(self, jobid, version=-1):
        try:
            version = int(version)
            return json.dumps(db[jobid][version])
        except:
            raise cherrypy.NotFound()
            #return "not found: " + str(jobid) + " " + str(version)

@cherrypy.popargs("jobid","version")
class Graph(object):
    exposed = True
    def GET(self, jobid, version=-1):
        version = int(version)
        try:
            c = db[jobid][version]
        except (IndexError, KeyError):
            raise cherrypy.NotFound()
        return json.dumps(solve_mincost_problem_for_expenses(c))

root = Root()
root.expenses = Expenses()
root.graph = Graph()

conf = {
 'global': {
 'server.socket_host': '0.0.0.0', 
 'server.socket_port': 8000 
 } ,
 '/': {
 'request.dispatch': cherrypy.dispatch.MethodDispatcher() 
 } 
}
cherrypy.quickstart(root, '/', conf)
#        '/static': {
#                'tools.staticdir.on': True,
#                'tools.staticdir.dir': os.path.abspath(os.path.dirname(__file__)),
#                'tools.staticdir.index': 'index.html',
#            },

