import asyncio
import aiohttp
import logging
from typing import Dict, Any, List
from utils import parse_search_results
from config import SEARCH_ENGINE_URL, USER_AGENT, REQUEST_DELAY, REQUEST_TIMEOUT, MAX_RETRIES

class Agent:
    def __init__(self, agent_id: int):
        self.agent_id = agent_id

    async def work(self, task_queue: asyncio.Queue, results: Dict[str, Any]):
        while True:
            try:
                query = await task_queue.get()
                logging.info(f"Agent {self.agent_id} processing query: {query}")
                search_results = await self.search_with_retry(query)
                results[query] = search_results
                task_queue.task_done()
                await asyncio.sleep(REQUEST_DELAY)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logging.error(f"Agent {self.agent_id} encountered an error: {e}")
                task_queue.task_done()

    async def search_with_retry(self, query: str) -> List[Dict[str, str]]:
        for attempt in range(MAX_RETRIES):
            try:
                return await self.search(query)
            except Exception as e:
                logging.warning(f"Agent {self.agent_id} attempt {attempt + 1} failed for query '{query}': {e}")
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
        logging.error(f"Agent {self.agent_id} all attempts failed for query '{query}'")
        return []

    async def search(self, query: str) -> List[Dict[str, str]]:
        headers = {'User-Agent': USER_AGENT}
        async with aiohttp.ClientSession(headers=headers) as session:
            url = SEARCH_ENGINE_URL.format(query=query)
            async with session.get(url, timeout=REQUEST_TIMEOUT) as response:
                if response.status == 200:
                    content = await response.text()
                    return parse_search_results(content)
                else:
                    logging.warning(f"Agent {self.agent_id} received status code {response.status} for query: {query}")
                    return []

    def __str__(self):
        return f"Agent-{self.agent_id}"