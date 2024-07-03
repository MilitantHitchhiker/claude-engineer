import argparse
from typing import List

def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Multi-agent web scraper for collecting search data")
    parser.add_argument("-q", "--queries", nargs="+", help="List of search queries to process")
    parser.add_argument("-n", "--num-agents", type=int, help="Number of scraper agents to use")
    parser.add_argument("-o", "--output", help="Output file name for search results")
    parser.add_argument("-m", "--max-results", type=int, help="Maximum number of results per query")
    return parser.parse_args()

def get_search_queries(args: argparse.Namespace) -> List[str]:
    if args.queries:
        return args.queries
    from config import DEFAULT_SEARCH_QUERIES
    return DEFAULT_SEARCH_QUERIES

def get_num_agents(args: argparse.Namespace) -> int:
    if args.num_agents:
        return args.num_agents
    from config import NUM_AGENTS
    return NUM_AGENTS

def get_output_file(args: argparse.Namespace) -> str:
    if args.output:
        return args.output
    from config import OUTPUT_FILE
    return OUTPUT_FILE

def get_max_results(args: argparse.Namespace) -> int:
    if args.max_results:
        return args.max_results
    from config import MAX_RESULTS_PER_QUERY
    return MAX_RESULTS_PER_QUERY