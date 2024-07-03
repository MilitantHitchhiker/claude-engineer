import asyncio
import logging
from agent import Agent
from typing import List, Dict, Any
from config import NUM_AGENTS, MAX_RESULTS_PER_QUERY, BLACKLIST_DOMAINS
from utils import remove_duplicates, filter_results

class Scraper:
    def __init__(self, num_agents: int = NUM_AGENTS, max_results: int = MAX_RESULTS_PER_QUERY):
        self.num_agents = num_agents
        self.max_results = max_results
        self.agents = [Agent(i) for i in range(num_agents)]
        self.task_queue = asyncio.Queue()
        self.results = {}

    async def run(self, search_queries: List[str]) -> Dict[str, List[Dict[str, Any]]]:
        logging.info(f"Starting scraper with {self.num_agents} agents")
        for query in search_queries:
            await self.task_queue.put(query)

        agent_tasks = [asyncio.create_task(agent.work(self.task_queue, self.results))
                       for agent in self.agents]

        await self.task_queue.join()

        for task in agent_tasks:
            task.cancel()

        await asyncio.gather(*agent_tasks, return_exceptions=True)

        # Process and filter results
        for query, results in self.results.items():
            filtered_results = filter_results(results, BLACKLIST_DOMAINS)
            unique_results = remove_duplicates(filtered_results)
            self.results[query] = unique_results[:self.max_results]

        logging.info("Scraping completed")
        return self.results