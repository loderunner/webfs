# webfs
A very simple filesystem with an HTTP REST API

# App Documentation

```
usage: app.py [-h] [--root-path ROOT_PATH] [-d] [host] [port]

positional arguments:
  host                  Host to bind to.
  port                  Port to listen on.

optional arguments:
  -h, --help            show this help message and exit
  --root-path ROOT_PATH
                        Path to serve.
  -d, --debug           Run in debug mode.
```

# API Documentation

## Directories

### Listing a directory's contents

```
GET /<path>
```

**Returns:** a JSON array with the names of files and directories contained in the directory designated by `<path>`

**Example:**

```
GET /Jack%20White-2014-Lazaretto HTTP/1.1
```

```
HTTP/1.0 200 OK
Content-Length: 574
Content-Type: application/json; charset=utf-8
Date: Fri, 27 Mar 2015 12:54:20 GMT
Server: Werkzeug/0.10.1 Python/2.7.6

[
    "01 - Three Women.flac", 
    "02 - Lazaretto.flac", 
    "03 - Temporary Ground.flac", 
    "04 - Would You Fight for My Love.flac", 
    "04 - Would You Fight for My Love.flac.jpg", 
    "05 - High Ball Stepper.flac", 
    "06 - Just One Drink.flac", 
    "07 - Alone in My Home.flac", 
    "08 - Entitlement.flac", 
    "08 - Entitlement.flac.jpg", 
    "09 - That Black Bat Licorice.flac", 
    "10 - I Think I Found the Culprit.flac", 
    "11 - Want and Able.flac",
    "Front.jpg",
    "Jack White - Lazaretto.m3u"
]
```

### Retrieving a directory's metadata

```
GET /<path>?stat
```

**Returns:** a JSON hash containing the following fields:

 * `file` - the name of the directory
 * `path` - the absolute path to the directory
 * `access_time` - time of last access (see `[man stat]`(http://linux.die.net/man/2/stat)
 * `change_time` - time of last status change (see `[man stat]`(http://linux.die.net/man/2/stat)
 * `modification_time` - time of last modification (see `[man stat]`(http://linux.die.net/man/2/stat)
 * `mimetype` - always `inode/directory`

**Example:**

```
GET /Jack%20White-2014-Lazaretto?stat HTTP/1.1
```

```
HTTP/1.0 200 OK
Content-Length: 193
Content-Type: application/json; charset=utf-8
Date: Fri, 27 Mar 2015 13:00:23 GMT
Server: Werkzeug/0.10.1 Python/2.7.6

{
    "access_time": 1427461205, 
    "change_time": 1417002013, 
    "file": "Jack White-2014-Lazaretto", 
    "mimetype": "inode/directory", 
    "modification_time": 1417002013, 
    "path": "/Jack White-2014-Lazaretto"
}
```

### Creating a directory

```
PUT /<path>
```

No HTTP body.

**Example:**

```
PUT /hello HTTP/1.1
Content-Length: 0
```

```
HTTP/1.0 201 CREATED
Content-Length: 0
Content-Type: text/html; charset=utf-8
Date: Fri, 27 Mar 2015 13:54:20 GMT
Server: Werkzeug/0.10.1 Python/2.7.6
```

### Deleting a directory

```
DELETE /<path>
```

The directory MUST be empty.

**Example:**

```
DELETE /hello HTTP/1.1
Content-Length: 0
```

```
HTTP/1.0 204 NO CONTENT
Content-Length: 0
Content-Type: text/html; charset=utf-8
Date: Fri, 27 Mar 2015 14:15:39 GMT
Server: Werkzeug/0.10.1 Python/2.7.6
```

## Files

### Retrieving a file

```
GET /<path>
```

**Returns:** the data in the file designated by `<path>`

**Example:**

```
GET /Jack%20White-2014-Lazaretto/Front.jpg HTTP/1.1
```

```
HTTP/1.0 200 OK
Cache-Control: public, max-age=43200
Content-Length: 232335
Content-Type: image/jpeg
Date: Fri, 27 Mar 2015 14:16:55 GMT
ETag: "flask-1417001049.0-232335-2421233012"
Expires: Sat, 28 Mar 2015 02:16:55 GMT
Last-Modified: Wed, 26 Nov 2014 11:24:09 GMT
Server: Werkzeug/0.10.1 Python/2.7.6



+-----------------------------+
| NOTE: binary data not shown |
+-----------------------------+
```

### Retrieving a file's metadata

```
GET /<path>?stat
```

**Returns:** a JSON hash containing the following fields:

 * `file` - the name of the file
 * `path` - the absolute path to the file
 * `size` - the size of the file (in bytes)
 * `access_time` - time of last access (see `[man stat]`(http://linux.die.net/man/2/stat)
 * `change_time` - time of last status change (see `[man stat]`(http://linux.die.net/man/2/stat)
 * `modification_time` - time of last modification (see `[man stat]`(http://linux.die.net/man/2/stat)
 * `mimetype` - the MIME type of the file

```
GET /Jack%20White-2014-Lazaretto/Front.jpg?stat HTTP/1.1
```

```
HTTP/1.0 200 OK
Content-Length: 198
Content-Type: application/json; charset=utf-8
Date: Fri, 27 Mar 2015 14:19:30 GMT
Server: Werkzeug/0.10.1 Python/2.7.6

{
    "access_time": 1427465831, 
    "change_time": 1417001049, 
    "file": "Front.jpg", 
    "mimetype": "image/jpeg", 
    "modification_time": 1417001049, 
    "path": "/Jack White-2014-Lazaretto/Front.jpg", 
    "size": 232335
}
```

### Creating a file

```
PUT /<path>
```

Contents of file in HTTP body as raw bytes.

**Example:**

```
PUT /Jack%20White-2014-Lazaretto/hello.jpg HTTP/1.1
Content-Length: 429383
Content-Type: image/jpeg



+-----------------------------+
| NOTE: binary data not shown |
+-----------------------------+
```

```
HTTP/1.0 201 CREATED
Content-Length: 0
Content-Type: text/html; charset=utf-8
Date: Fri, 27 Mar 2015 14:25:44 GMT
Server: Werkzeug/0.10.1 Python/2.7.6
```

### Deleting a file

```
DELETE /<path>
```

**Example:**

```
DELETE /Jack%20White-2014-Lazaretto/toto.jpg HTTP/1.1
Content-Length: 0
```

```
HTTP/1.0 204 NO CONTENT
Content-Length: 0
Content-Type: text/html; charset=utf-8
Date: Fri, 27 Mar 2015 14:27:13 GMT
Server: Werkzeug/0.10.1 Python/2.7.6
```
