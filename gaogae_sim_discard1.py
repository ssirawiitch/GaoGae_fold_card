"""
gaogae_sim_discard1.py
========================
Equity simulation for the Gao Gae dealing variant: deal 4 cards, discard 1
(keep the best 3 cards out of the 4 dealt).

Each opponent is also dealt 4 cards and automatically keeps their own best
3-card subset (assumes every opponent discards optimally).

Usage:
    python3 gaogae_sim_discard1.py
    python3 gaogae_sim_discard1.py --trials 100000
"""

import argparse
from gaogae_core import print_and_save_table

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Gao Gae equity simulation - deal 4, discard 1')
    parser.add_argument('--trials', type=int, default=60000,
                         help='Number of simulation trials per hand (higher = more accurate '
                              'but slower, default 60000)')
    parser.add_argument('--max-opponents', type=int, default=9,
                         help='Maximum number of opponents to simulate (default 9)')
    args = parser.parse_args()

    print_and_save_table(
        variant_name='Deal 4, discard 1 (keep best 3)',
        opponent_deal_size=4,
        csv_path='gaogae_equity_discard1.csv',
        trials=args.trials,
        max_opponents=args.max_opponents,
    )