import asyncio
import logging
import json
from scraper import Scraper
from cli import parse_arguments, get_search_queries, get_num_agents, get_output_file, get_max_results

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def main():
    args = parse_arguments()
    
    search_queries = get_search_queries(args)
    num_agents = get_num_agents(args)
    output_file = get_output_file(args)
    max_results = get_max_results(args)
    
    logging.info(f"Starting scraper with {num_agents} agents")
    logging.info(f"Search queries: {search_queries}")
    logging.info(f"Max results per query: {max_results}")
    
    scraper = Scraper(num_agents=num_agents, max_results=max_results)
    results = await scraper.run(search_queries)
    
    # Save results to file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    logging.info(f"Results saved to {output_file}")
    
    # Print summary
    for query, data in results.items():
        logging.info(f"Results for '{query}': {len(data)} items")

if __name__ == "__main__":
    asyncio.run(main())