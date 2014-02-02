#!/usr/bin/env python
# coding: utf-8
# Copyright 2013 Abram Hindle, Mircea Caciula
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib
from urlparse import urlparse

def help():
    print "httpclient.py [GET/POST] [URL]\n"

class HTTPRequest(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

    def __str__(self):
      return "Code: " + str(self.code) + "\nBody: " + self.body 

class HTTPClient(object):
    host = ""
    port = 80
    path = ""

    def parseURL(self, url):
        parsedurl = urlparse(url)

        self.host = parsedurl.netloc
        self.path = parsedurl.path

        if (":" in self.host):
          splitstring = self.host.rsplit(":")

          self.host = splitstring[0]
          self.port = int(splitstring[1])

        if (self.path == "") :
          self.path = "/"

    def connect(self, request):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((self.host, self.port))
        sock.sendall(request)

        return self.recvall(sock)

    def get_code(self, data):
        return int(data.rsplit(" ")[1])

    def get_headers(self,data):
        return data.rsplit("\r\n\r\n")[0]

    def get_body(self, data):
        return data.rsplit("\r\n\r\n")[1]

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return str(buffer)

    def GET(self, url, args=None):
        self.parseURL(url)

        request = "GET %s HTTP/1.1\r\nHost: %s:%s\r\nAccept: */*\r\nConnection: close\r\n\r\n" % (self.path, self.host, self.port)

        data = self.connect(request)

        code = self.get_code(data)
        body = self.get_body(data)

        return HTTPRequest(code, body)

    def POST(self, url, args=None):
        self.parseURL(url)
        query = ""

        if (args != None):
          query = urllib.urlencode(args)

        request = "POST %s HTTP/1.1\r\nHost: %s:%s\r\nAccept: */*\r\nContent-Length: %s\r\nContent-Type: application/x-www-form-urlencoded\r\n\r\n%s\r\n\r\n" % (self.path, self.host, self.port, len(query), query)

        data = self.connect(request)

        code = self.get_code(data)
        body = self.get_body(data)

        return HTTPRequest(code, body)

    def command(self, url, command="GET", args=None):
        self.parseURL(url)

        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"

    #if the syntax is httpclient.py [GET/POST] [URL] then sys.argv[1] is
    #the command and sys.argv[2] is the URL, not the other way around
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print client.command( sys.argv[2], sys.argv[1] )
    else:
        print client.command( command, sys.argv[1] )    
