#!/usr/bin/env python
# Plays MPV when instructed to by a chrome extension =]

import sys
import argparse
import subprocess
import json
import re
import os
from typing import Union

from fastapi import FastAPI
from fastapi.responses import JSONResponse
app = FastAPI()


@app.get("/")
async def read_items(check_if_hdr_url: str | None = None, play_url: str | None = None, cast_url: str | None = None, fairuse_url: str | None = None, mpv_args: list | None = [], ytdl_args: list | None = [], location: str | None = '~/Downloads/'):
    results = {}
    if check_if_hdr_url:
        urls = check_if_hdr_url
        try:
            
            pipe = subprocess.Popen(['yt-dlp', urls, '-J'] , stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            output = pipe.stdout.read()
        
            if ("\"dynamic_range\": \"HDR10\"" in output.decode()):
                print("Video has HDR")
                results = {"type": "hdr_check_result", "url": urls, "dynamic_range": "HDR10"}
            else:
                print("Video is SDR")
                results = {"type": "hdr_check_result", "url": urls, "dynamic_range": "SDR"}

        except FileNotFoundError as e:
            missing_bin('mpv')

    elif play_url:
            urls = play_url
            if urls.startswith('magnet:') or urls.endswith('.torrent'):
                try:
                    pipe = subprocess.Popen(['peerflix', '-k',  urls, '--', '--force-window'] + mpv_args)
                except FileNotFoundError as e:
                    missing_bin('peerflix')
            else:
                try:
                    
                    pipe = subprocess.Popen(['mpv', urls, '--force-window'] + mpv_args)
                                 
                except FileNotFoundError as e:
                    missing_bin('mpv')
            results = {"status": "playing..."}
    elif cast_url:
        urls = cast_url
        if urls.startswith('magnet:') or urls.endswith('.torrent'):
            print(" === WARNING: Casting torrents not yet fully supported!")
            try:
                with subprocess.Popen(['mkchromecast', '--video',
                            '--source-url', 'http://localhost:8888']):
                    pass
            except FileNotFoundError as e:
                missing_bin('mkchromecast')
            pipe.terminate()
        else:
            try:
                pipe = subprocess.Popen(['mkchromecast', '--video', '-y', urls])
            except FileNotFoundError as e:
                missing_bin('mkchromecast')
        results = {"status": "casting..."}

    elif fairuse_url:
        urls = fairuse_url
        if "%" not in location:
            location += "%(title)s.%(ext)s"
        print("downloading ", urls, "to", location)
        if urls.startswith('magnet:') or urls.endswith('.torrent'):
            msg = " === ERROR: Downloading torrents not yet supported!"
            print(msg)
            raise HTTPException(status_code=404, detail=msg)
        else:
            try:
                pipe = subprocess.Popen(['youtube-dl', urls, '-o', location] +
                                ytdl_args)
            except FileNotFoundError as e:
                missing_bin('youtube-dl')
            results = {"status": "downloading..."}
    else:
        raise HTTPException(status_code=404)

        
    return JSONResponse(content=results)

def missing_bin(bin):
    print("======================")
    print(f"ERROR: {bin.upper()} does not appear to be installed correctly! please ensure you can launch '{bin}' in the terminal.")
    print("======================")

"""
class Handler(BaseHTTPServer.BaseHTTPRequestHandler, CompatibilityMixin):
    def respond(self, code, body=None):
        self.send_response(code)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        if body:
            self.send_body(body)

    def do_GET(self):
        try:
            url = urlparse.urlparse(self.path)
            query = urlparse.parse_qs(url.query)
        except:
            query = {}
        if query.get('mpv_args'):
            print("MPV ARGS:", query.get('mpv_args'))
        if "check_if_hdr_url" in query:
            urls = str(query["check_if_hdr_url"][0])
            try:
            
                pipe = subprocess.Popen(['yt-dlp', urls, '-J'] , stdout=subprocess.PIPE, stderr=subprocess.PIPE)

                output = pipe.stdout.read()
            
                if ("\"dynamic_range\": \"HDR10\"" in output.decode()):
                    print("Video has HDR")
                    self.respond(200, json.dumps({"type": "hdr_check_result", "url": urls, "dynamic_range": "HDR10"}))
                else:
                    print("Video is SDR")
                    self.respond(200, json.dumps({"type": "hdr_check_result", "url": urls, "dynamic_range": "SDR"}))

            except FileNotFoundError as e:
                missing_bin('mpv')
        elif "play_url" in query:
            urls = str(query["play_url"][0])
            if urls.startswith('magnet:') or urls.endswith('.torrent'):
                try:
                    pipe = subprocess.Popen(['peerflix', '-k',  urls, '--', '--force-window'] +
                                 query.get("mpv_args", []))
                except FileNotFoundError as e:
                    missing_bin('peerflix')
            else:
                try:
                    
                    pipe = subprocess.Popen(['mpv', urls, '--force-window'] +
                                 query.get("mpv_args", []))
                                 
                except FileNotFoundError as e:
                    missing_bin('mpv')
            self.respond(200, "playing...")
        elif "cast_url" in query:
            urls = str(query["cast_url"][0])
            if urls.startswith('magnet:') or urls.endswith('.torrent'):
                print(" === WARNING: Casting torrents not yet fully supported!")
                try:
                    with subprocess.Popen(['mkchromecast', '--video',
                                '--source-url', 'http://localhost:8888']):
                        pass
                except FileNotFoundError as e:
                    missing_bin('mkchromecast')
                pipe.terminate()
            else:
                try:
                    pipe = subprocess.Popen(['mkchromecast', '--video', '-y', urls])
                except FileNotFoundError as e:
                    missing_bin('mkchromecast')
            self.respond(200, "casting...")

        elif "fairuse_url" in query:
            urls = str(query["fairuse_url"][0])
            location = query.get("location", ['~/Downloads/'])[0]
            if "%" not in location:
                location += "%(title)s.%(ext)s"
            print("downloading ", urls, "to", location)
            if urls.startswith('magnet:') or urls.endswith('.torrent'):
                msg = " === ERROR: Downloading torrents not yet supported!"
                print(msg)
                self.respond(400, msg)
            else:
                try:
                    pipe = subprocess.Popen(['youtube-dl', urls, '-o', location] +
                                 query.get('ytdl_args', []))
                except FileNotFoundError as e:
                    missing_bin('youtube-dl')
                self.respond(200, "downloading...")
        else:
            self.respond(400)


def missing_bin(bin):
    print("======================")
    print(f"ERROR: {bin.upper()} does not appear to be installed correctly! please ensure you can launch '{bin}' in the terminal.")
    print("======================")


def start():
    parser = argparse.ArgumentParser(description='Plays MPV when instructed to by a browser extension.', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--port',   type=int,  default=7531, help='The port to listen on.')
    parser.add_argument('--public', action='store_true',     help='Accept traffic from other computers.')
    args = parser.parse_args()
    hostname = '0.0.0.0' if args.public else 'localhost'
    httpd = BaseHTTPServer.HTTPServer((hostname, args.port), Handler)
    print("serving on {}:{}".format(hostname, args.port))
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print(" shutting down...")
        httpd.shutdown()


if __name__ == '__main__':
    start()

"""