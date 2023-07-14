# !/usr/bin/python
import asyncio
import os
import json
from urllib.parse import urlparse
from colors import *
from aiohttp import *


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


async def lfi_check(url, paths) -> list[ClientResponse]:
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


async def main():
    pathInput = input('Paths dictionary path: ')
    raw_url = input('Url (e.g https://example.org/index.php?id=): ')
    out = input('Outfile name: ')

    url = urlparse(url)
    paths = open(pathInput).readlines()

    try:
        respones = await lfi_check(url, paths)
    except NameError:
        print(colors.RED + f'Error: {NameError} ' + colors.END)

    if os.path.isfile(out):
        clear = open(out, 'w')
        clear.close()

    with open(out, 'a') as a:
        for i, reponse in enumerate(respones):
            a.write(json.dumps({paths[i]: reponse}, indent=1))

    print('\n' + colors.BOLD + colors.OKGREEN +
          f'Responses from host:{host} dumped in ' + colors.PURPLE + out + colors.END  + ' file' + colors.END)

if __name__ == '__main__':
    asyncio.run(main())
