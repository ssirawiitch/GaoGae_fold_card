"""
gaogae_sim_baseline.py
=======================
Equity simulation for the BASELINE Gao Gae dealing variant:
  - Deal 3 cards directly, or deal 2 + bet + deal 1 more (these two give
    the exact same final-hand distribution, since there is no card
    selection at all -- they only differ in when betting information
    becomes available, not in the final hand itself)
  - Each opponent is dealt 3 random cards directly, with no choice

Usage:
    python3 gaogae_sim_baseline.py
    python3 gaogae_sim_baseline.py --trials 100000
"""

import argparse
from gaogae_core import print_and_save_table

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Gao Gae equity simulation - baseline dealing')
    parser.add_argument('--trials', type=int, default=60000,
                         help='Number of simulation trials per hand (higher = more accurate '
                              'but slower, default 60000)')
    parser.add_argument('--max-opponents', type=int, default=9,
                         help='Maximum number of opponents to simulate (default 9)')
    args = parser.parse_args()

    print_and_save_table(
        variant_name='Baseline (deal 3 direct / 2+1, no card selection)',
        opponent_deal_size=3,
        csv_path='gaogae_equity_baseline.csv',
        trials=args.trials,
        max_opponents=args.max_opponents,
    )