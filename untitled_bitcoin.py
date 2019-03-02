#!/usr/bin/env python3

import http

def main():
    conn = http.client.HTTPSConnection('https://api.github.com/markdown')
    conn.request("GET", "/markdown")
    r1 = conn.getresponse()
    print(r1.read())


#-------------------------------------------------------------------------------
# PROGRAM ENTRY POINT
#-------------------------------------------------------------------------------
if __name__ == '__main__': main()

