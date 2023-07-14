#!/usr/bin/env python

import asyncio
import os
import json
import re
from src.client import *
from etc.colors import *
import argparse
from etc.arg_types import arg_types

def IsValidArg(arg : str, type : arg_types):
    if type is arg_types.URL:
        return len(re.findall('https?://.+/(.+\/)*.+(\..+)?\?.+=', arg)) > 0
    if type is arg_types.DICTIONARY:
        return os.path.isfile(arg)

async def main():
    # pathInput = input('|< Paths dictionary path (empty to default): ')
    # raw_url = input('|< URL (e.g https://example.org/index.php?id=): ')
    # output = input('|< Output filename (empty to default)): ')

    parser = argparse.ArgumentParser(description='Brutforce specify URL for LFI vulnerability',
                                     epilog='[EXAMPLE: python lfiploit.py -u https://udav.corp/downloads?v= --out myout --dict /root/lfidick.dict --json]')
    parser.add_argument('--url', '-u', dest='url', required=True, help='URL which should end with <VARIABLE>\'=\'' +
                         ', e.g https://example.com/index.php?id=')
    parser.add_argument('--json', '-j', dest='json', action='store_true', help='Dump responses as JSON')
    parser.add_argument('--out', '-o', dest='out', help='Path to output file')
    parser.add_argument('--dict', '-d', dest='dict', default=os.curdir + '/dict/lfi_dict', help='Path to custom dictionary (emtpy to default)')
    args = parser.parse_args()

    url = args.url
    dict_path = args.dict 

    print(colors.YELLOW + '|> [*] Validate args ' + colors.END, end="-> ")
    if not IsValidArg(url, arg_types.URL):
        print(colors.RED + f'Input parameter URL doesn\'t match the pattern.\n|> Keep this grammar: ' + colors.END +
               colors.GREEN + r'http[s]://<host>/{<path>/}<endpoint>?<param>= ' + colors.END +
               colors.RED + '\n|> See EBNF notation (https://en.wikipedia.org/wiki/Extended_Backus%E2%80%93Naur_form), mzfck' + colors.END)
        exit(0)
    if not IsValidArg(dict_path, arg_types.DICTIONARY):
        print(colors.RED + f'Cannot find dictionary in ' + colors.END + colors.PURPLE + dict_path + colors.END)
        exit(0)

    print(colors.GREEN + 'OK' + colors.END)
    dump_json = args.json
    outfile_path = args.out

    dict = open(dict_path).readlines()

    try:
        responses = await Brute(url, dict)
    except Exception as exc:
        print(colors.RED + f'|> Error: {exc} ' + colors.END)
        exit(0)

    if outfile_path is None:
        for reponse in responses:
            print(reponse)
        print(colors.GREEN + "|> Exit")
    else:
        if os.path.isfile(outfile_path):
            opt = input(colors.YELLOW + f'\n|> ' + colors.END + colors.PURPLE + outfile_path + colors.END + 
                     colors.YELLOW + ' already exists. Do you want to truncate them?[y/n] ' + colors.END)
        if opt == 'y':
            clear = open(outfile_path, 'w')
            clear.close()
    
        with open(outfile_path, 'a') as a:
            if dump_json:            
                for i, response in enumerate(responses):
                    a.write(json.dumps({dict[i] : response}, indent=1) + '\n')
            else:
                for response in responses:
                    a.write(response)

        print('\n' + colors.GREEN +
              f'|> Responses from url:`{url}` dumped in ' + 
            colors.PURPLE + outfile_path + colors.END +  colors.GREEN + ' file')

if __name__ == '__main__':
    asyncio.run(main())
