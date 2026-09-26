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
    python3 gaogae_sim_baseline.py --trials 1000000 --workers 4 --seed 20260926
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
    parser.add_argument('--seed', type=int, default=20260926,
                         help='Base random seed for reproducible output (default 20260926)')
    parser.add_argument('--workers', type=int, default=1,
                         help='Number of hands to simulate in parallel (default 1)')
    parser.add_argument('--output', default='gaogae_equity_baseline.csv',
                         help='Output CSV path')
    args = parser.parse_args()

    print_and_save_table(
        variant_name='Baseline (deal 3 direct / 2+1, no card selection)',
        opponent_deal_size=3,
        csv_path=args.output,
        trials=args.trials,
        max_opponents=args.max_opponents,
        seed=args.seed,
        workers=args.workers,
    )
