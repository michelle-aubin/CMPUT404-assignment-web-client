#!/usr/bin/env python3
# coding: utf-8
# Copyright 2020, Michelle Aubin, Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
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
from urllib.parse import urlparse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    agent = "httpclient/1.0"
    accept = "*/*"
    conn = "close"

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        data = data.split('\r\n')
        code = int(data[0].split()[1])
        return code

    def get_headers(self,data):
        return data.split('\r\n\r\n')[0].split('\r\n')[1:]

    def get_body(self, data):
        return data.split('\r\n\r\n')[-1]
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

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
        return buffer.decode('utf-8')

    def GET(self, url, args=None):
        url = urlparse(url)
        host = url.hostname
        port = url.port if url.port else 80
        port_str = f":{port}" if port else ''
        path = url.path if url.path else '/'
        self.connect(host, port)

        request = (
            f"GET {path} HTTP/1.1\r\n"
            f"Host: {host}{port_str}\r\n"
            f"User-Agent: {self.agent}\r\n"
            f"Accept: {self.accept}\r\n"
            f"Connection: {self.conn}\r\n"
            f"\r\n"
        )
        print("---Request---")
        print(request)
        self.sendall(request)

        response = self.recvall(self.socket)
        print("---Response---")
        print(response)
        code = self.get_code(response)
        body = self.get_body(response)
        self.close()
        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        url = urlparse(url)
        host = url.hostname
        port = url.port if url.port else 80
        port_str = f":{port}" if port else ''
        path = url.path if url.path else '/'
        post_body = self.build_post_body(args)
        self.connect(host, port)

        request = (
            f"POST {path} HTTP/1.1\r\n"
            f"Host: {host}{port_str}\r\n"
            f"User-Agent: {self.agent}\r\n"
            f"Accept: {self.accept}\r\n"
            f"Connection: {self.conn}\r\n"
            f"Content-Type: application/x-www-form-urlencoded\r\n"
            f"Content-Length: {len(post_body.encode())}\r\n"
            f"\r\n"
            f"{post_body}"
        )
        print("---Request---")
        print(request)
        self.sendall(request)

        response = self.recvall(self.socket)
        print("---Response---")
        print(response)
        code = self.get_code(response)
        body = self.get_body(response)
        self.close()
        return HTTPResponse(code, body)

    def build_post_body(self, args=None):
        if args:
            return '&'.join(f"{k}={v}" for k, v in args.items())
        else:
            return ''

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
