#!/usr/bin/env python

from flask import Flask, request, current_app, stream_with_context, Response
from argparse import ArgumentParser
from json import dumps as json
from werkzeug.wsgi import wrap_file

import os
import sys
import flask
import filecache
import magic
import re

app = Flask(__name__)
root_path = os.getcwd()

def validate_ranges(ranges, content_length):
    return all([int(r[0]) <= int(r[1]) for r in ranges]) and all([int(x) < content_length for subrange in ranges for x in subrange])

@app.route('/', defaults={'path': ''}, methods=['GET', 'HEAD'])
@app.route('/<path:path>', methods=['GET', 'HEAD'])
def get(path):
    path_components = path.split('/')
    if '.' in path_components or '..' in path_components:
        return flask.make_response("Path must be absolute.", 400)

    fullpath = '%s/%s' % (root_path, path)

    mime = magic.from_file(fullpath, mime=True)
    if mime is None:
        mime = 'application/octet-stream'
    else:
        mime = mime.replace(' [ [', '')

    if os.path.exists(fullpath):
        if (request.args.get('stat') is not None):
            stat = os.stat(fullpath)
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
            stat = os.stat(fullpath)
            f = filecache.open_file(fullpath)
            r = request.headers.get('Range')
            m = re.match('bytes=((\d+-\d+,)*(\d+-\d*))', r) if r is not None else None
            if r is None or m is None:
                f.seek(0)
                def stream_data():
                    while True:
                        d = f.read(8192)
                        if len(d) > 0:
                            yield d
                        else:
                            break
                res = Response(stream_with_context(stream_data()), 200, mimetype=mime, direct_passthrough=True)
                res.headers['Content-Length'] = stat.st_size
            else:
                ranges = [x.split('-') for x in m.group(1).split(',')]
                if validate_ranges(ranges, stat.st_size):
                    content_length = 0
                    for rng in ranges:
                        if rng[1] == '':
                            content_length = content_length + stat.st_size - int(rng[0]) + 1
                        else:
                            content_length = content_length + int(rng[1]) - int(rng[0]) + 1
                    def stream_data():
                        for r in ranges:
                            f.seek(int(r[0]))
                            if r[1] == '':
                                while True:
                                    d = f.read(8192)
                                    if len(d) > 0:
                                        yield d
                                    else:
                                        break
                            else:
                                for s in [min(8192, int(r[1]) - i + 1) for i in range(int(r[0]), int(r[1]), 8192)]:
                                    d = f.read(s)
                                    yield d


                    res = Response(stream_with_context(stream_data()), 206, mimetype=mime, direct_passthrough=True)
                    res.headers['Content-Length'] = content_length
                    res.headers['Content-Range'] = 'bytes %s-%s/%d' % (ranges[0][0], ranges[0][1], stat.st_size)
                else:
                    res = flask.make_response('', 416)
            # res.headers['Accept-Ranges'] = 'bytes'
            return res
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

    app.run(host=args.host, port=args.port, debug=args.debug)

