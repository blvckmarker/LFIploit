import asyncio 
from aiohttp import *
from etc.colors import colors

count_requests = 0
total_requests = 0
async def make_request(url, path, client: ClientSession) -> ClientResponse:
    global count_requests
    print(colors.DARKCYAN + f'|> Current count of async requests: {count_requests}/{total_requests} ' + colors.END, end='\r')
    count_requests += 1
    async with client.get(url + path) as response:
        return await response.text()

tasks_running = True
async def time_count() -> None:
    print('\n')
    seconds = 0
    while tasks_running:
        print(colors.BLUE + f'|> [Await tasks] Time elapsed: {round(seconds, 1)} seconds' + colors.END, end='\r')
        seconds += 0.1
        await asyncio.sleep(0.1)


async def Brute(url, paths) -> list[ClientResponse]:
    global total_requests
    total_requests = len(paths)
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
