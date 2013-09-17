#!/bin/sh -ex
curl $@ --data-binary @demodata -H "Content-type: text/plain" 127.0.0.1:8000/rest/expenses
