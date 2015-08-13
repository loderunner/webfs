#!/usr/bin/env python

# The MIT License (MIT)
#
# Copyright (c) 2015 Charles Francoise
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from flask import Flask, request
from argparse import ArgumentParser
from json import dumps as json

import os
import sys
import flask
import magic

app = Flask(__name__)
root_path = os.getcwd()

@app.route('/', defaults={'path': ''}, methods=['GET', 'HEAD'])
@app.route('/<path:path>', methods=['GET', 'HEAD'])
def get(path):
    path_components = path.split('/')
    if '.' in path_components or '..' in path_components:
        return flask.make_response("Path must be absolute.", 400)

    fullpath = '%s/%s' % (root_path, path)
    if os.path.exists(fullpath):
        if (request.args.get('stat') is not None):
            stat = os.stat(fullpath)
            mime = magic.from_file(fullpath, mime=True)
            if mime is None:
                mime = 'application/octet-stream'
            else:
                mime = mime.replace(' [ [', '')
            st = {'file' : os.path.basename(fullpath),
                  'path' : '/%s' % path,
                  'access_time' : int(stat.st_atime),
                  'modification_time' : int(stat.st_mtime),
                  'change_time' : int(stat.st_ctime),
                  'mimetype' : mime}
            if not os.path.isdir(fullpath):
                st['size'] = int(stat.st_size)
            res = flask.make_response(json(st))
            res.headers['Content-Type'] = 'application/json; charset=utf-8'
            return res

        if os.path.isdir(fullpath):
            res = flask.make_response(json(os.listdir(fullpath)))
            res.headers['Content-Type'] = 'application/json; charset=utf-8'
            return res
        else:
            return flask.send_file(fullpath)
    else:
        return flask.make_response('/%s: No such file or directory.' % path, 404)

@app.route('/<path:path>', methods=['PUT', 'POST'])
def put(path):
    path_components = path.split('/')
    if '.' in path_components or '..' in path_components:
        return flask.make_response("Path must be absolute.", 400)

    fullpath = '%s/%s' % (root_path, path)
    if os.path.exists(fullpath):
        return flask.make_response('/%s: File exists.' % path, 403)
    elif request.data == '' or request.data is None:
        os.mkdir(fullpath)
        return flask.make_response('', 201)
    else:
        encoding = request.args.get('encoding')
        if encoding == 'base64':
            data = request.data.decode('base64')
        else:
            data = request.data
        with open(fullpath, "wb") as dest_file:
            dest_file.write(data)
        return flask.make_response('', 201)

@app.route('/<path:path>', methods=['DELETE'])
def delete(path):
    path_components = path.split('/')
    if '.' in path_components or '..' in path_components:
        return flask.make_response("Path must be absolute.", 400)

    fullpath = '%s/%s' % (root_path, path)
    if os.path.exists(fullpath):
        if os.path.isdir(fullpath):
            if os.listdir(fullpath) == []:
                os.rmdir(fullpath)
                return flask.make_response('', 204)
            else:
                print os.listdir(fullpath)
                return flask.make_response('/%s: Directory is not empty.' % path, 403)
        else:
            os.remove(fullpath)
            return flask.make_response('', 204)
    else:
        return flask.make_response('/%s: No such file or directory.' % path, 404)
    

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument('--root-path', dest='root_path', action='store', help='Path to serve.')
    parser.add_argument('-d', '--debug', dest='debug', action='store_true', help='Run in debug mode.')
    parser.add_argument('host', action='store', nargs='?', help='Host to bind to.')
    parser.add_argument('port', action='store', type=int, nargs='?', help='Port to listen on.')

    args = parser.parse_args()

    if args.root_path is not None:
        root_path = args.root_path

    app.run(threaded=True, host=args.host, port=args.port, debug=args.debug)

