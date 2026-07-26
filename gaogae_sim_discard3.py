"""
gaogae_sim_discard3.py
========================
Equity simulation for the Gao Gae dealing variant: deal 6 cards, discard 3
(keep the best 3 cards out of the 6 dealt).

Each opponent is also dealt 6 cards and automatically keeps their own best
3-card subset (assumes every opponent discards optimally).

Note: dealing 6 cards per player uses up cards fast, so the maximum number
of opponents that can actually be dealt from the 49 remaining cards (after
removing your own 3-card hand) is automatically capped at 8
(49 // 6 = 8), even if --max-opponents 9 is requested. The script will
print a notice when this cap kicks in.

Usage:
    python3 gaogae_sim_discard3.py
    python3 gaogae_sim_discard3.py --trials 100000
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
    args = parser.parse_args()

    print_and_save_table(
        variant_name='Deal 6, discard 3 (keep best 3)',
        opponent_deal_size=6,
        csv_path='gaogae_equity_discard3.csv',
        trials=args.trials,
        max_opponents=args.max_opponents,
    )