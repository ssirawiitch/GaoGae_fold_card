"""
gaogae_sim_discard2.py
========================
Equity simulation for the Gao Gae dealing variant: deal 5 cards, discard 2
(keep the best 3 cards out of the 5 dealt).

Each opponent is also dealt 5 cards and automatically keeps their own best
3-card subset (assumes every opponent discards optimally).

Usage:
    python3 gaogae_sim_discard2.py
    python3 gaogae_sim_discard2.py --trials 100000
"""

import argparse
from gaogae_core import print_and_save_table

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Gao Gae equity simulation - deal 5, discard 2')
    parser.add_argument('--trials', type=int, default=60000,
                         help='Number of simulation trials per hand (higher = more accurate '
                              'but slower, default 60000)')
    parser.add_argument('--max-opponents', type=int, default=9,
                         help='Maximum number of opponents to simulate (default 9)')
    args = parser.parse_args()

    print_and_save_table(
        variant_name='Deal 5, discard 2 (keep best 3)',
        opponent_deal_size=5,
        csv_path='gaogae_equity_discard2.csv',
        trials=args.trials,
        max_opponents=args.max_opponents,
    )