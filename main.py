################################################################################
'''
Crypto Parking: Automated bitcoin parking lot
File name: main.py
Author(s): Kass Chupongstimun, kchupong@ucsd.edu
           John So, jyso@ucsd.edu
'''
################################################################################

#!/usr/bin/env python3

from crypto_parking import CryptoParking

def main():
		''' main method of program '''

    print("Crypto Parking Lot")

    # instantiate application and start
    app = CryptoParking()
    app.start()

#-------------------------------------------------------------------------------
# PROGRAM ENTRY POINT
#-------------------------------------------------------------------------------
if __name__ == '__main__': main()
