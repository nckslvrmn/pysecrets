#!/bin/sh

haproxy -f /config/haproxy.cfg

source pysecrets/bin/activate

gunicorn \
-c /config/gunicorn.conf.py \
app:app
