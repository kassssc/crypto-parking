################################################################################
'''
Crypto Parking: Automated bitcoin parking lot
File name: main.py
Description:
Author(s): Kass Chupongstimun, kchupong@ucsd.edu
           John So, jyso@ucsd.edu
'''
################################################################################

#!/usr/bin/env python3

from crypto_parking import CryptoParking

def main():
    print("Crypto Parking Lot")

    app = CryptoParking()
    app.start()

#-------------------------------------------------------------------------------
# PROGRAM ENTRY POINT
#-------------------------------------------------------------------------------
if __name__ == '__main__': main()
