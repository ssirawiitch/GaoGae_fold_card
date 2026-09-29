"""Build full final-hand win-rate tables for four modeled 9-Bets deal sizes.

The simulation deals a complete six-player table.  Every player keeps the
best three cards allowed by the selected modeled deal size.  For each resulting hand
strength, it estimates the probability of beating 2, 3, 4, or 5 randomly
selected opponents (3--6 total players).

Only an outright win is counted.  The confirmed control-suit rule
(Spades > Hearts > Diamonds > Clubs) makes an exact tie impossible between
physical hands that can coexist at showdown.

Outputs, for each modeled deal size:
  * a CSV with one row per distinct final-hand strength; and
  * a colour-coded HTML table containing the same win percentages.

Example:
    python3 gaogae_full_winrate.py --rounds 10000000 --output-dir full_winrate
"""

import argparse
import csv
import html
import math
import random
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path

from gaogae_core import (
    CATEGORY_NAME,
    ORDER,
    RANK_HIGH_VAL,
    SUIT_FROM_HIGH_VAL,
    SUIT_SYMBOL,
    build_deck,
    classify,
)


VARIANTS = (
    ('baseline', 'd3 final three cards (showdown-only): deal 3 / deal 2+1', 3),
    ('discard1', 'Deal 4, discard 1', 4),
    ('discard2', 'Deal 5, discard 2', 5),
    ('discard3', 'Deal 6, discard 3', 6),
)

TOTAL_PLAYERS = (3, 4, 5, 6)
MAX_OPPONENTS = max(TOTAL_PLAYERS) - 1
BASE_SEED = 20260926
EXPECTED_REACHABLE_STRENGTHS = {
    3: 2925,
    4: 2323,
    5: 2049,
    6: 1857,
}


def build_strength_catalog():
    """Return all strength keys, labels, combination counts, and fast lookup."""
    deck = build_deck()
    counts = Counter()
    example = {}
    strength_by_mask = {}

    for card_indexes in combinations(range(len(deck)), 3):
        hand = tuple(deck[index] for index in card_indexes)
        strength = classify(hand)
        counts[strength] += 1
        example.setdefault(strength, hand)
        mask = sum(1 << index for index in card_indexes)
        strength_by_mask[mask] = strength

    strengths = sorted(counts, reverse=True)
    details = {
        strength: {
            'label': strength_label(strength),
            'category': CATEGORY_NAME[strength[0]],
            'physical_hands': counts[strength],
            'example': example[strength],
        }
        for strength in strengths
    }
    return strengths, details, strength_by_mask


def _rank_name(value):
    return {14: 'A', 13: 'K', 12: 'Q', 11: 'J'}.get(value, str(value))


def _straight_name(index):
    sequences = [ORDER[i:i + 3] for i in range(len(ORDER) - 2)]
    sequences.append(['Q', 'K', 'A'])
    return '-'.join(sequences[index])


def _suit_symbol(value):
    return SUIT_SYMBOL[SUIT_FROM_HIGH_VAL[value]]


def strength_label(strength):
    """Create a compact, human-readable label for a classify() tuple."""
    category = strength[0]
    if category == 6:
        rank = _rank_name(strength[1])
        return f'Tong {rank}-{rank}-{rank}'
    if category == 5:
        return f'Straight flush {_straight_name(strength[1])} {_suit_symbol(strength[2])}'
    if category == 4:
        if strength[1] == 1:
            return f'Sian J-Q-K, control K{_suit_symbol(strength[4])}'
        return (f'Sian pair {_rank_name(strength[2])}, '
                f'kicker {_rank_name(strength[3])}{_suit_symbol(strength[4])}')
    if category == 3:
        sequence = _straight_name(strength[1])
        control_rank = 'A' if sequence == 'Q-K-A' else sequence.split('-')[-1]
        return (f'Straight {sequence}, control '
                f'{control_rank}{_suit_symbol(strength[2])}')
    if category == 2:
        ranks = '-'.join(_rank_name(value) for value in strength[1:4])
        return f'Flush {ranks} {_suit_symbol(strength[4])}'

    points = strength[1]
    if strength[2] == 1:
        return (f'{points} points, pair {_rank_name(strength[3])}, '
                f'kicker {_rank_name(strength[4])}{_suit_symbol(strength[5])}')
    ranks = '-'.join(_rank_name(value) for value in strength[3:6])
    return (f'{points} points, {ranks}, control '
            f'{_rank_name(strength[3])}{_suit_symbol(strength[6])}')


def best_strength(card_indexes, deal_size, strength_by_mask):
    """Return the best strength from integer card indexes."""
    if deal_size == 3:
        mask = ((1 << card_indexes[0]) | (1 << card_indexes[1]) |
                (1 << card_indexes[2]))
        return strength_by_mask[mask]

    best = None
    for a, b, c in combinations(card_indexes, 3):
        strength = strength_by_mask[(1 << a) | (1 << b) | (1 << c)]
        if best is None or strength > best:
            best = strength
    return best


def exact_final_strength_counts(deal_size, strength_by_mask):
    """Count every possible dealt hand by the strength of its best three.

    Besides supplying an exact final-hand frequency, this tells us which of
    the direct three-card strengths can actually survive optimal discards.
    """
    counts = Counter()
    for card_indexes in combinations(range(52), deal_size):
        counts[best_strength(card_indexes, deal_size, strength_by_mask)] += 1
    return counts


def simulate_variant(deal_size, rounds, seed, strength_by_mask, progress_every=0):
    """Simulate final strengths and strict wins for 3--6 total players.

    A six-player deal supplies six conditional hero observations per round.
    If L of the other five hands are lower, the chance that n randomly chosen
    opponents are all lower is C(L,n)/C(5,n).  This gives the exact 3/4/5-player
    sub-table average without discarding useful observations.
    """
    if rounds <= 0:
        raise ValueError('rounds must be positive')
    if deal_size not in (3, 4, 5, 6):
        raise ValueError('deal_size must be 3, 4, 5, or 6')

    rng = random.Random(seed)
    deck_indexes = tuple(range(52))
    cards_needed = 6 * deal_size
    sample_counts = Counter()
    win_sums = defaultdict(lambda: [0.0] * len(TOTAL_PLAYERS))
    denominators = [math.comb(MAX_OPPONENTS, players - 1)
                    for players in TOTAL_PLAYERS]

    for round_index in range(1, rounds + 1):
        dealt = rng.sample(deck_indexes, cards_needed)
        table = [
            best_strength(
                dealt[start:start + deal_size], deal_size, strength_by_mask
            )
            for start in range(0, cards_needed, deal_size)
        ]

        for hero_index, hero_strength in enumerate(table):
            lower = sum(
                opponent_strength < hero_strength
                for index, opponent_strength in enumerate(table)
                if index != hero_index
            )
            sample_counts[hero_strength] += 1
            sums = win_sums[hero_strength]
            for column, players in enumerate(TOTAL_PLAYERS):
                opponents = players - 1
                if lower >= opponents:
                    sums[column] += math.comb(lower, opponents) / denominators[column]

        if progress_every and round_index % progress_every == 0:
            print(f'  {round_index:,}/{rounds:,} rounds', flush=True)

    return sample_counts, win_sums


def result_rows(strengths, details, sample_counts, win_sums, rounds,
                variant_key, variant_name, deal_size, seed, exact_counts):
    """Create one row for each final strength reachable under this modeled deal size."""
    total_observations = rounds * 6
    total_deals = math.comb(52, deal_size)
    rows = []
    for strength in strengths:
        possible_deals = exact_counts[strength]
        if not possible_deals:
            continue
        samples = sample_counts[strength]
        row = {
            'variant': variant_key,
            'variant_name': variant_name,
            'cards_dealt_per_player': deal_size,
            'rounds': rounds,
            'seed': seed,
            'category': details[strength]['category'],
            'hand': details[strength]['label'],
            'strength_key': repr(strength),
            'physical_3card_hands': details[strength]['physical_hands'],
            'dealt_hands_ending_at_strength': possible_deals,
            'exact_final_hand_frequency_pct': round(
                possible_deals / total_deals * 100, 8
            ),
            'observed_final_hands': samples,
            'simulated_final_hand_frequency_pct': (
                round(samples / total_observations * 100, 6) if samples else 0.0
            ),
        }
        for column, players in enumerate(TOTAL_PLAYERS):
            value = win_sums[strength][column] / samples * 100 if samples else None
            row[f'win_{players}_players_pct'] = (
                round(value, 4) if value is not None else ''
            )
        rows.append(row)
    return rows


def write_csv(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', newline='', encoding='utf-8-sig') as output:
        writer = csv.DictWriter(
            output, fieldnames=list(rows[0]), lineterminator='\n'
        )
        writer.writeheader()
        writer.writerows(rows)


def heat_color(value):
    """Map 0--100 to red--yellow--green using an HSL background colour."""
    hue = max(0.0, min(120.0, float(value) * 1.2))
    return f'hsl({hue:.1f} 72% 82%)'


def write_html(path, rows, variant_name, rounds, seed):
    """Write one readable colour table for a dealing variant."""
    table_rows = []
    last_category = None
    for row in rows:
        category = row['category']
        category_cell = html.escape(category) if category != last_category else ''
        last_category = category
        win_cells = []
        for players in TOTAL_PLAYERS:
            value = row[f'win_{players}_players_pct']
            if value == '':
                win_cells.append('<td class="missing">N/A</td>')
            else:
                win_cells.append(
                    f'<td class="pct" style="background:{heat_color(value)}">'
                    f'{float(value):.2f}%</td>'
                )
        low_sample = ' class="low-sample"' if row['observed_final_hands'] < 1000 else ''
        table_rows.append(
            f'<tr{low_sample}><td class="category">{category_cell}</td>'
            f'<td>{html.escape(row["hand"])}</td>'
            + ''.join(win_cells)
            + f'<td class="count">{row["observed_final_hands"]:,}</td></tr>'
        )

    document = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>9-Bets win rate — {html.escape(variant_name)}</title>
<style>
  body {{ font: 14px/1.35 system-ui, sans-serif; margin: 24px; color: #172033; }}
  h1 {{ margin-bottom: 6px; }}
  .note {{ max-width: 980px; color: #475569; }}
  table {{ border-collapse: separate; border-spacing: 0; width: 100%; }}
  th, td {{ border-right: 1px solid #cbd5e1; border-bottom: 1px solid #cbd5e1;
            padding: 7px 9px; }}
  th:first-child, td:first-child {{ border-left: 1px solid #cbd5e1; }}
  thead th {{ position: sticky; top: 0; background: #172033; color: white;
              border-top: 1px solid #172033; z-index: 2; }}
  td.category {{ font-weight: 650; min-width: 175px; }}
  td.pct, td.count {{ text-align: right; font-variant-numeric: tabular-nums; }}
  tr.low-sample td:first-child {{ border-left: 4px solid #f59e0b; }}
  td.missing {{ background: #e5e7eb; text-align: center; color: #64748b; }}
  tbody tr:hover td {{ outline: 2px solid #334155; outline-offset: -2px; }}
</style>
</head>
<body>
<h1>{html.escape(variant_name)}</h1>
<p class="note">Strict Win% after every player has selected their final three cards.
The control-card suit (♠ &gt; ♥ &gt; ♦ &gt; ♣) resolves otherwise equal hands,
so every physical showdown has one winner. Simulated {rounds:,} six-player
rounds (seed {seed}), reusing each deal to estimate tables of 3–6 total players.
Only final strengths that can actually remain after optimal discarding are shown.
Rows with fewer than 1,000 observed final hands have an orange marker and
should be treated as preliminary.</p>
<table>
<thead><tr><th>Category</th><th>Final hand strength</th>
<th>3 players</th><th>4 players</th><th>5 players</th><th>6 players</th>
<th>Observed samples</th></tr></thead>
<tbody>{''.join(table_rows)}</tbody>
</table>
</body>
</html>'''
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(document, encoding='utf-8')


def write_index(path, generated):
    links = ''.join(
        f'<li><a href="{html.escape(html_name)}">{html.escape(title)}</a></li>'
        for title, html_name in generated
    )
    document = f'''<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>9-Bets full win-rate tables</title>
<style>body {{ font: 16px/1.5 system-ui,sans-serif; max-width: 850px;
margin: 40px auto; padding: 0 20px; color: #172033; }} li {{ margin: 10px 0; }}</style>
</head><body><h1>9-Bets full final-hand win-rate tables</h1>
<p>Choose a modeled deal size. d3 combines deal 3 and deal 2+1 only for showdown-only results; betting and folding are excluded.</p>
<ul>{links}</ul>
<p><a href="png/winrate_summary_6_players.png">Quick comparison PNG (6 players)</a><br>
<a href="png/README.md">Full-table PNG files and export options</a></p>
<p><a href="METHODOLOGY.md">Methodology, definitions, and limitations</a></p>
</body></html>'''
    path.write_text(document, encoding='utf-8')


def parse_args():
    parser = argparse.ArgumentParser(
        description='Generate full 9-Bets final-hand strict win-rate tables for four modeled deal sizes.'
    )
    parser.add_argument('--rounds', type=int, default=10000000,
                        help='Six-player rounds per variant (default 10,000,000)')
    parser.add_argument('--seed', type=int, default=BASE_SEED,
                        help=f'Base random seed (default {BASE_SEED})')
    parser.add_argument('--output-dir', default='full_winrate',
                        help='Directory for CSV and HTML output')
    parser.add_argument('--variant', choices=['all'] + [v[0] for v in VARIANTS],
                        default='all', help='Run one variant or all (default all)')
    parser.add_argument('--progress-every', type=int, default=100000,
                        help='Print progress every N rounds; 0 disables it')
    return parser.parse_args()


def main():
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    strengths, details, strength_by_mask = build_strength_catalog()
    variants = VARIANTS if args.variant == 'all' else tuple(
        variant for variant in VARIANTS if variant[0] == args.variant
    )
    generated = []

    print(f'{len(strengths):,} distinct final-hand strength rows')
    variant_seed_index = {key: index for index, (key, _name, _size) in enumerate(VARIANTS)}
    for key, name, deal_size in variants:
        variant_seed = args.seed + variant_seed_index[key] * 1000003
        print(f'\n{name}: {args.rounds:,} rounds (seed={variant_seed})', flush=True)
        print('  enumerating exact reachable final strengths...', flush=True)
        exact_counts = exact_final_strength_counts(deal_size, strength_by_mask)
        expected_strengths = EXPECTED_REACHABLE_STRENGTHS[deal_size]
        if len(exact_counts) != expected_strengths:
            raise RuntimeError(
                f'Exact catalog check failed for deal size {deal_size}: '
                f'expected {expected_strengths} strengths, got {len(exact_counts)}'
            )
        expected_deals = math.comb(52, deal_size)
        if sum(exact_counts.values()) != expected_deals:
            raise RuntimeError(
                f'Exact deal-count check failed for deal size {deal_size}: '
                f'expected {expected_deals}, got {sum(exact_counts.values())}'
            )
        print(f'  {len(exact_counts)}/{len(strengths)} strengths are reachable', flush=True)
        sample_counts, win_sums = simulate_variant(
            deal_size, args.rounds, variant_seed, strength_by_mask,
            progress_every=args.progress_every,
        )
        rows = result_rows(
            strengths, details, sample_counts, win_sums, args.rounds,
            key, name, deal_size, variant_seed, exact_counts,
        )
        csv_name = f'winrate_{key}.csv'
        html_name = f'winrate_{key}.html'
        write_csv(output_dir / csv_name, rows)
        write_html(output_dir / html_name, rows, name, args.rounds, variant_seed)
        generated.append((name, html_name))
        observed = sum(sample_counts[strength] > 0 for strength in exact_counts)
        low_sample = sum(0 < sample_counts[strength] < 1000
                         for strength in exact_counts)
        print(f'  wrote {csv_name} and {html_name}; '
              f'observed {observed}/{len(exact_counts)} reachable rows, '
              f'{low_sample} below 1,000 samples', flush=True)

    write_index(output_dir / 'index.html', generated)
    print(f'\nOpen {output_dir / "index.html"}')


if __name__ == '__main__':
    main()
