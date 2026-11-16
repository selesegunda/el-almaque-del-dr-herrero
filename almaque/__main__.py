import argparse
import logging
from .collect import collect
from .store import merge
from .render import render


def main():
    parser = argparse.ArgumentParser(description='El almaque del Dr. Herrero')
    parser.add_argument('--days', type=int, default=14, help='PubMed indexing date lookback')
    parser.add_argument('--build-only', action='store_true', help='Render stored data without fetching')
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format='%(levelname)s %(message)s')
    if not args.build_only:
        records, issues, sources = collect(args.days)
        store, runs, current = merge(records, issues, sources)
        logging.info('Processed %d: new %d, updated %d, failed sources %d', len(records), current['new'], current['updated'], len(issues))
        if not sources:
            logging.error('No data sources worked. Archived data preserved, see incident log.')
    render()


if __name__ == '__main__':
    main()
