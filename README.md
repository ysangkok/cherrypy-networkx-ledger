cherrypy-networkx-ledger
========================

Static file serving with Apache, forwarding REST queries to CherryPy:

    ProxyPass <project-directory>/rest http://localhost:8000 # forward to CherryPy server
    
Note that the project also depends on the URL rewriting in `.htaccess`.
