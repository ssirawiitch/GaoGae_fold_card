"""
gaogae_sim_discard3.py
========================
Equity simulation for the Gao Gae dealing variant: deal 6 cards, discard 3
(keep the best 3 cards out of the 6 dealt).

Each opponent is also dealt 6 cards and automatically keeps their own best
3-card subset (assumes every opponent discards optimally).

Note: dealing 6 cards per player uses up cards fast. One 52-card deck can
serve at most 8 total players, so the simulation is capped at 7 opponents
after accounting for the hero's own 6 dealt cards. The script prints a
notice when this cap applies.

Usage:
    python3 gaogae_sim_discard3.py
    python3 gaogae_sim_discard3.py --trials 100000
    python3 gaogae_sim_discard3.py --trials 1000000 --workers 4 --seed 20260926
"""

import argparse
from gaogae_core import print_and_save_table

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Gao Gae equity simulation - deal 6, discard 3')
    parser.add_argument('--trials', type=int, default=60000,
                         help='Number of simulation trials per hand (higher = more accurate '
                              'but slower, default 60000)')
    parser.add_argument('--max-opponents', type=int, default=9,
                         help='Maximum number of opponents to simulate (auto-reduced if the '
                              'deck runs short, default 9)')
    parser.add_argument('--seed', type=int, default=20260926,
                         help='Base random seed for reproducible output (default 20260926)')
    parser.add_argument('--workers', type=int, default=1,
                         help='Number of hands to simulate in parallel (default 1)')
    parser.add_argument('--output', default='gaogae_equity_discard3.csv',
                         help='Output CSV path')
    args = parser.parse_args()

    print_and_save_table(
        variant_name='Deal 6, discard 3 (keep best 3)',
        opponent_deal_size=6,
        csv_path=args.output,
        trials=args.trials,
        max_opponents=args.max_opponents,
        seed=args.seed,
        workers=args.workers,
    )
