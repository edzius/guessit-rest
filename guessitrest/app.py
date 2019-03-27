#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json

import logging
from logging.handlers import RotatingFileHandler

import os

from flask import Flask, make_response
from flask_cors import CORS  # pylint:disable=no-name-in-module,import-error
from flask_restful import Api, Resource, reqparse

import guessit
from guessit.jsonutils import GuessitEncoder

import omdbref

from . import __version__

app = Flask(__name__)
CORS(app)
api = Api(app)
app.debug = os.environ.get('GUESSIT-REST-DEBUG', False)

if not app.debug:
    handler = RotatingFileHandler('guessit-rest.log', maxBytes=5 * 1024 * 1024, backupCount=5)
    handler.setLevel(logging.DEBUG)
    app.logger.addHandler(handler)


@api.representation('application/json')
def output_json(data, code, headers=None):
    resp = make_response(json.dumps(data, cls=GuessitEncoder, ensure_ascii=False), code)
    resp.headers.extend(headers or {})
    return resp


class GuessItOmdb(Resource):
    def _impl(self, location):
        parser = reqparse.RequestParser()
        parser.add_argument('title', action='store', required=True, help='Title to search', location=location)
        parser.add_argument('season', action='store', help='Season info', location=location)
        parser.add_argument('episode', action='store', help='Episode info', location=location)
        args = parser.parse_args()

        if not args.season or not args.episode:
            data = omdbref.receive(args.title, "movie")
        else:
            data = omdbref.receive(args.title, "series")
            if data:
                data['specific'] = omdbref.receive(args.title, None, args.season, args.episode)

        return data

    def get(self):
        return self._impl('args')

    def post(self):
        return self._impl('json')


class GuessIt(Resource):
    def _impl(self, location):
        parser = reqparse.RequestParser()
        parser.add_argument('filename', action='store', required=True, help='Filename to parse', location=location)
        parser.add_argument('options', action='store', help='Guessit options', location=location)
        args = parser.parse_args()

        return guessit.guessit(args.filename, args.options)

    def get(self):
        return self._impl('args')

    def post(self):
        return self._impl('json')


class GuessItList(Resource):
    def _impl(self, location):
        parser = reqparse.RequestParser()
        parser.add_argument('filename', action='append', required=True, help='Filename to parse', location=location)
        parser.add_argument('options', action='store', help='Guessit options', location=location)
        args = parser.parse_args()

        ret = []

        for filename in args.filename:
            ret.append(guessit.guessit(filename, args.options))

        return ret

    def get(self):
        return self._impl('args')

    def post(self):
        return self._impl('json')


class GuessItVersion(Resource):
    def get(self):
        return {'guessit': guessit.__version__, 'rest': __version__}


api.add_resource(GuessItOmdb, '/omdb/')
api.add_resource(GuessIt, '/')
api.add_resource(GuessItList, '/list/')
api.add_resource(GuessItVersion, '/version/')
