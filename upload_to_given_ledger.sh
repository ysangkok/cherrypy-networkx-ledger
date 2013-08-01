#!/bin/sh
curl --data-binary @demodata -H "Content-type: text/plain" localhost:8000/expenses/$1
