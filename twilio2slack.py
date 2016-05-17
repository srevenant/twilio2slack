#!./python/bin/python
# vim:set et ts=4 sw=4 ai ft=python:

"""
Twilio 2 Slack SMS gateway

Copyright 2016 Brandon Gillespie

"""

__version__ = 1.0

import requests
import config
import json
import cherrypy
import os, os.path
import re
import sys
import string
import time

def secureheaders():
    headers = cherrypy.response.headers
    headers['X-Frame-Options'] = 'DENY'
    headers['X-XSS-Protection'] = '1; mode=block'
    headers['Content-Security-Policy'] = "default-src='self'"

cherrypy.tools.secureheaders = cherrypy.Tool('before_finalize', secureheaders, priority=60)

class Twilio(object):

    @cherrypy.expose
    def sms(self, **kwargs):
        frm = kwargs.get('From')
        msg = kwargs.get('Body')

        match = re.search(r'([0-9]{3})([0-9]{3})([0-9]{4})$', frm)
        if match:
            frm = "(" + match.group(1) + ") " + match.group(2) + "-" + match.group(3)

        res = requests.post(config.slack_hook,
                  json.dumps({
                    "text": frm + ": " + msg,
                    "username": "sms",
                    "icon_emoji": ":sms:"
                  }))

        return ""

if __name__ == '__main__':
    conf = {
        'global':{
            'server.socket_port': config.port,
            'server.socket_host': '0.0.0.0'
        },
        '/': {
            'response.headers.server': "stack",
            'tools.secureheaders.on': True
        },
        '/message': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'tools.response_headers.on': True,
            'tools.response_headers.headers': [('Content-Type', 'text/plain')],
        }
    }

    cherrypy.quickstart(Twilio(), config.endpoint, conf)

