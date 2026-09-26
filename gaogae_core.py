"""
gaogae_core.py
==============
Shared engine for Gao Gae (Thai: เก้าเก), a Thai 3-card betting game:
hand classification, comparator logic, and a Monte Carlo multiway-equity
simulator.

Pure Python standard library only (random, itertools, collections) --
no pip installs needed.

RULESET USED (see project README for full discussion of why these were
chosen -- rules vary by house/region, this is one fixed, documented set):
  - Ranking, high to low: Tong > Straight flush > Sian > Straight (Riang)
    > Flush (See) > Point total (Tam)
  - Non-flush J-Q-K ("Sian Riang") is the top sub-rank within Sian
  - Within pair-type Sian hands: higher pair rank wins, then kicker
  - Straights include A-2-3 (ace low) through Q-K-A (ace high), 12
    sequences total
  - Ace counts as 1 point only (never 10/11) in the Tam (point) category
  - Within Tam: point total (0-9) is compared first; for equal points,
    a pair ("kum"/คุม) beats no pair, then pair/card ranks break ties

This file is imported by gaogae_sim_baseline.py / gaogae_sim_discard1.py /
gaogae_sim_discard2.py / gaogae_sim_discard3.py -- it is not meant to be
run directly.
"""

import random
from functools import lru_cache
from itertools import combinations

ORDER = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
SUITS = ['S', 'H', 'D', 'C']
SUIT_SYMBOL = {'S': '\u2660', 'H': '\u2665', 'D': '\u2666', 'C': '\u2663'}
RANK_HIGH_VAL = {'A': 14, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7,
                  '8': 8, '9': 9, '10': 10, 'J': 11, 'Q': 12, 'K': 13}
COURT = {'J', 'Q', 'K'}
CARD_INDEX = {
    (rank, suit): rank_index * len(SUITS) + suit_index
    for rank_index, rank in enumerate(ORDER)
    for suit_index, suit in enumerate(SUITS)
}

# Category names: English description with the Thai term kept for reference,
# since these are the actual names used at the table.
CATEGORY_NAME = {
    6: 'Tong (three of a kind)',
    5: 'Straight flush',
    4: 'Sian (three court cards J/Q/K)',
    3: 'Straight (Riang)',
    2: 'Flush (See)',
    1: 'Point total (Tam)',
}

# --- 12 possible 3-card straight rank-sequences (A low through A high) ---
_STRAIGHT_SEQS = []
for _i in range(len(ORDER) - 2):
    _STRAIGHT_SEQS.append(frozenset(ORDER[_i:_i + 3]))
_STRAIGHT_SEQS.append(frozenset(['Q', 'K', 'A']))  # ace-high wrap
STRAIGHT_SEQ_INDEX = {s: i for i, s in enumerate(_STRAIGHT_SEQS)}


def point_value(rank):
    """Point value of a single card (A=1, 10/J/Q/K=0, else face value)."""
    if rank == 'A':
        return 1
    if rank in ('J', 'Q', 'K', '10'):
        return 0
    return int(rank)


def build_deck():
    """Build a standard 52-card deck as a list of (rank, suit) tuples."""
    return [(r, s) for r in ORDER for s in SUITS]


def hand_str(hand):
    """Render a hand as readable text, e.g. K♠ K♥ J♦"""
    return ' '.join(f"{r}{SUIT_SYMBOL[s]}" for r, s in hand)


def classify(hand):
    """
    Classify a 3-card hand according to the agreed hierarchy. Returns a
    tuple that can be compared directly with Python's > < == operators --
    a larger tuple means a stronger hand.
    """
    if len(hand) != 3:
        raise ValueError('A final Gao Gae hand must contain exactly 3 cards')
    try:
        canonical_hand = tuple(sorted(hand, key=CARD_INDEX.__getitem__))
    except KeyError as exc:
        raise ValueError('Hand contains an invalid card') from exc
    if len(set(canonical_hand)) != 3:
        raise ValueError('A hand cannot contain duplicate physical cards')
    return _classify_cached(canonical_hand)


@lru_cache(maxsize=None)
def _classify_cached(hand):
    """Classify a validated, canonically ordered hand."""
    ranks = [c[0] for c in hand]

    suitset = set(c[1] for c in hand)
    rankset = set(ranks)
    is_flush = len(suitset) == 1
    is_tong = len(rankset) == 1
    fr = frozenset(rankset)
    is_straight = (len(rankset) == 3) and (fr in STRAIGHT_SEQ_INDEX)
    is_all_court = rankset.issubset(COURT)

    if is_tong:
        return (6, RANK_HIGH_VAL[ranks[0]])

    if is_straight and is_flush:
        return (5, STRAIGHT_SEQ_INDEX[fr])

    if is_all_court:
        if fr == frozenset(['J', 'Q', 'K']):
            return (4, 1, 0, 0)  # Sian Riang - top sub-rank within Sian
        pair_rank, kicker = _pair_and_kicker(ranks)
        return (4, 0, RANK_HIGH_VAL[pair_rank], RANK_HIGH_VAL[kicker])

    if is_straight:
        return (3, STRAIGHT_SEQ_INDEX[fr])

    if is_flush:
        sr = sorted([RANK_HIGH_VAL[r] for r in ranks], reverse=True)
        return (2, sr[0], sr[1], sr[2])

    # Tam (point total): compare points first, then control cards ("kum").
    # A pair beats no pair. Within either group, compare physical card ranks
    # high-to-low; A is high for this tiebreak even though it is worth 1 point.
    pts = sum(point_value(r) for r in ranks) % 10
    if len(rankset) == 2:
        pair_rank, kicker = _pair_and_kicker(ranks)
        return (1, pts, 1, RANK_HIGH_VAL[pair_rank], RANK_HIGH_VAL[kicker])
    high_cards = sorted((RANK_HIGH_VAL[r] for r in ranks), reverse=True)
    return (1, pts, 0, *high_cards)


def _pair_and_kicker(ranks):
    """Return (pair_rank, kicker_rank) for a three-card one-pair hand."""
    if ranks[0] == ranks[1]:
        return ranks[0], ranks[2]
    if ranks[0] == ranks[2]:
        return ranks[0], ranks[1]
    return ranks[1], ranks[0]


def best_subset(cards, k=3):
    """
    Pick the best possible k-card subset out of `cards` (used for
    deal-and-discard variants, e.g. deal 5 keep the best 3). If
    len(cards) == k this is equivalent to classify(cards) directly,
    since there is only one possible subset.
    """
    best = None
    for combo in combinations(cards, k):
        cat = classify(combo)
        if best is None or cat > best:
            best = cat
    return best


def showdown_share(my_cat, opponent_cats):
    """Return (outcome, pot_share) against a completed set of opponents.

    ``outcome`` is ``'win'``, ``'tie'``, or ``'loss'``. Exact top-ranked
    ties split the pot equally among all tied winners, so a three-way tie
    returns a share of 1/3 rather than the old fixed 1/2 approximation.
    """
    best_opp = max(opponent_cats)
    if my_cat > best_opp:
        return 'win', 1.0
    if my_cat < best_opp:
        return 'loss', 0.0
    tied_opponents = sum(cat == my_cat for cat in opponent_cats)
    return 'tie', 1.0 / (tied_opponents + 1)


def simulate_equity(my_hand, opponent_deal_size, max_opponents=9, trials=60000, seed=None):
    """
    Simulate the equity of my_hand (your final, already-decided 3-card
    hand) against N opponents (N = 2..max_opponents), where each opponent
    is dealt opponent_deal_size cards and keeps their own best 3-card
    subset (best_subset).

    opponent_deal_size:
        3 = baseline dealing (deal 3 direct / 2+1, no card selection)
        4 = deal 4, discard 1
        5 = deal 5, discard 2
        6 = deal 6, discard 3

    Modeling assumption: my_hand is a fixed, already-selected final hand.
    In discard variants, the identities of your extra dealt-and-discarded
    cards are unknown to this benchmark and are marginalized over the
    undealt cards. Opponents still select their best 3 cards optimally.

    Deck-size constraint: the hero and every opponent receive the same
    number of cards. For a large opponent_deal_size (e.g. 6), the number of
    opponents is capped using the full 52-card deal (this function returns
    effective_max_opponents so the caller knows how many were simulated).

    Returns: (results, effective_max_opponents)
      results = {n: {'win_pct':.., 'tie_pct':.., 'equity_pct':..}, ...}
    """
    if opponent_deal_size < 3:
        raise ValueError('opponent_deal_size must be at least 3')
    if max_opponents < 2:
        raise ValueError('max_opponents must be at least 2')
    if trials <= 0:
        raise ValueError('trials must be positive')

    rng = random.Random(seed)

    full_deck = build_deck()
    remaining_base = [c for c in full_deck if c not in my_hand]
    my_cat = classify(my_hand)

    # Every player, including the hero, receives opponent_deal_size cards.
    # This matters for deal-6: one deck supports 8 total players, hence no
    # more than 7 opponents (not the 8 allowed by the old 49 // 6 formula).
    physical_max_opponents = (len(full_deck) // opponent_deal_size) - 1
    effective_max = min(max_opponents, physical_max_opponents)

    wins = {n: 0 for n in range(2, effective_max + 1)}
    ties = {n: 0 for n in range(2, effective_max + 1)}
    equity_sums = {n: 0.0 for n in range(2, effective_max + 1)}

    for _ in range(trials):
        deck = remaining_base[:]
        rng.shuffle(deck)
        opp_cats = []
        idx = 0
        for _opp in range(effective_max):
            block = deck[idx: idx + opponent_deal_size]
            idx += opponent_deal_size
            opp_cats.append(best_subset(block, 3))

        higher_seen = False
        tied_opponents = 0
        for n, opp_cat in enumerate(opp_cats, start=1):
            if opp_cat > my_cat:
                higher_seen = True
            elif opp_cat == my_cat:
                tied_opponents += 1

            if n < 2 or higher_seen:
                continue
            if tied_opponents:
                ties[n] += 1
                equity_sums[n] += 1.0 / (tied_opponents + 1)
            else:
                wins[n] += 1
                equity_sums[n] += 1.0

    results = {}
    for n in range(2, effective_max + 1):
        w, t = wins[n], ties[n]
        results[n] = {
            'win_pct': w / trials * 100,
            'tie_pct': t / trials * 100,
            'equity_pct': equity_sums[n] / trials * 100,
        }
    return results, effective_max


# Example hands spanning every category, shared by all runner scripts so
# results are directly comparable across dealing variants.
# Edit/add your own hands here -- format: (rank, suit), suit in S/H/D/C
EXAMPLE_HANDS = {
    'Three of a kind - 3s (tong)':      [('3', 'S'), ('3', 'H'), ('3', 'D')],
    'Straight flush 7-8-9 (sf)':        [('7', 'S'), ('8', 'S'), ('9', 'S')],
    'Sian straight J-Q-K (sian riang)': [('J', 'S'), ('Q', 'H'), ('K', 'D')],
    'Sian pair of Kings (sian)':        [('K', 'S'), ('K', 'H'), ('J', 'D')],
    'Straight 10-J-Q (riang)':          [('10', 'S'), ('J', 'H'), ('Q', 'D')],
    'Flush K-9-4 (see)':                [('K', 'S'), ('9', 'S'), ('4', 'S')],
    'Point 9 with a pair (tam)':        [('9', 'S'), ('9', 'H'), ('A', 'D')],
    'Point 9 no pair (tam)':            [('8', 'S'), ('K', 'H'), ('A', 'D')],
    'Point 5 no pair (tam)':            [('5', 'S'), ('Q', 'H'), ('K', 'D')],
    'Point 0 bust (tam)':               [('10', 'S'), ('J', 'H'), ('K', 'D')],
}


def _simulate_hand_job(job):
    """Worker entry point used by print_and_save_table."""
    index, name, hand, opponent_deal_size, max_opponents, trials, seed = job
    hand_seed = None if seed is None else seed + index
    results, effective_max = simulate_equity(
        hand,
        opponent_deal_size,
        max_opponents=max_opponents,
        trials=trials,
        seed=hand_seed,
    )
    return name, hand, results, effective_max, hand_seed


def print_and_save_table(variant_name, opponent_deal_size, csv_path,
                          trials=60000, max_opponents=9, seed=20260926,
                          workers=1):
    """Run every hand in EXAMPLE_HANDS, print a results table, and save a CSV."""
    import csv as csv_module

    if workers < 1:
        raise ValueError('workers must be at least 1')

    print(f"=== {variant_name} (opponents dealt {opponent_deal_size} card(s) each, "
          f"trials={trials:,}, seed={seed}, workers={workers}) ===\n", flush=True)

    all_rows = []
    header_n = None

    jobs = [
        (index, name, hand, opponent_deal_size, max_opponents, trials, seed)
        for index, (name, hand) in enumerate(EXAMPLE_HANDS.items())
    ]
    if workers == 1:
        completed = map(_simulate_hand_job, jobs)
    else:
        from concurrent.futures import ProcessPoolExecutor

        executor = ProcessPoolExecutor(max_workers=workers)
        completed = executor.map(_simulate_hand_job, jobs)

    for name, hand, res, eff_max, hand_seed in completed:
        if eff_max < max_opponents and header_n is None:
            print(f"[NOTE] With {opponent_deal_size} card(s) dealt per opponent, only "
                  f"{eff_max} opponents can actually be dealt from the remaining deck "
                  f"(requested {max_opponents}, not enough cards left)\n")

        opp_ns = sorted(res.keys())
        if header_n is None:
            header_n = opp_ns
            header = f"{'Hand':<32}" + ''.join(f"{'vs ' + str(n):>10}" for n in opp_ns)
            print(header)
            print('-' * len(header))

        row_txt = f"{name:<32}" + ''.join(f"{res[n]['equity_pct']:>9.1f}%" for n in opp_ns)
        print(row_txt, flush=True)

        row = {
            'variant': variant_name,
            'opponent_deal_size': opponent_deal_size,
            'trials': trials,
            'seed': hand_seed,
            'hand': name,
            'hand_cards': hand_str(hand),
        }
        for n in opp_ns:
            row[f'equity_vs_{n}'] = round(res[n]['equity_pct'], 2)
            row[f'win_vs_{n}'] = round(res[n]['win_pct'], 2)
            row[f'tie_vs_{n}'] = round(res[n]['tie_pct'], 2)
        all_rows.append(row)

    if all_rows:
        fieldnames = list(all_rows[0].keys())
        with open(csv_path, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv_module.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_rows)
        print(f"\nDetailed results saved to: {csv_path}")

    if workers != 1:
        executor.shutdown()
