cherrypy-networkx-ledger
========================

Imagine you are three people on a roadtrip, you buy some stuff, sometimes you pay half, the other guy pays half, sometimes the third guy pays all, and so on. But in the end, you'd like to share all costs evenly.

This webapp makes it possible to create a ledger, which is a list of expenses. You can add and delete expenses, and you can freeze the ledger and the webapp will generate e-mails for each participant containing links with unique tokens. When they receive payment, they can mark the payment as done using that link.

Installation
------------
```
pip-3.3 install networkx
pip-3.3 install cherrypy
python3.3 server.py
x-www-browser http://localhost:8000/
```
