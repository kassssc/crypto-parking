#!/usr/bin/env python3

import requests

def main():
	r = requests.get('https://blockchain.info/rawaddr/1F44zb39q6uRwkfDAHKTPqTFQQahSNoMdt')
	r_json = r.json()
	latest_transaction = r_json['txs'][0]['out'][1]['value']
	print(latest_transaction)

#-------------------------------------------------------------------------------
# PROGRAM ENTRY POINT
#-------------------------------------------------------------------------------
if __name__ == '__main__': main()

