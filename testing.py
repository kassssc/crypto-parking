#!/usr/bin/env python3

import sys, threading
def main():
    global flag
    flag = False
    wait_for_flag()

def wait_for_flag():
    global flag

    T = threading.Thread(target=forked_thread)
    T.start()

    while True:
        if flag:
            flag_detected()
            break

    print("done!")

def forked_thread():
    global flag

    while True:
        key = input("Hit x for main thread to stop: ")
        if key == 'x':
            flag = True
            break

def flag_detected():
    global flag
    print("Flag interrupt detected")
    print(flag)

#-------------------------------------------------------------------------------
# PROGRAM ENTRY POINT
#-------------------------------------------------------------------------------
if __name__ == '__main__': main()

