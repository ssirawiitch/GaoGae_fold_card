# Full final-hand Win% tables

## What the number means

Each percentage answers one question: **after all players have selected their
final three cards, what is the probability that this hand is the single winner
against every opponent?**

- `Win%` is the strict probability of being the sole winner.
- Hands are compared by category and the documented rank/control rules first.
  If those are still equal, the suit of the control card breaks the tie in this
  order: **spades (♠) > hearts (♥) > diamonds (♦) > clubs (♣)**.
- Legal physical hands that coexist at showdown therefore cannot produce a
  live tie, and the pot is never split.
- For these showdown tables, `Win%` is also the hand's equity: every outcome
  contributes either the whole pot (1) or none of it (0).
- There is no pot size, call amount, equity split, or fold/play advice in these
  tables.
- Every player is assumed to select the strongest possible three-card subset
  according to `RULES.md`.

## Tables

There is one CSV and one colour-coded HTML table for each dealing rule:

1. baseline — deal 3 directly, or deal 2 then 1 with no discard;
2. deal 4, discard 1;
3. deal 5, discard 2; and
4. deal 6, discard 3.

The columns headed 3, 4, 5, and 6 players mean **total players at showdown**,
including the player holding the listed hand.

## Exact and simulated parts

The script exhaustively enumerates every possible set of cards dealt to one
player. This gives the exact marginal frequency of each final strength and
proves which strength rows can survive optimal discarding:

| Dealt per player | Possible dealt sets | Reachable final strengths |
|---:|---:|---:|
| 3 | 22,100 | 2,925 |
| 4 | 270,725 | 2,323 |
| 5 | 2,598,960 | 2,049 |
| 6 | 20,358,520 | 1,857 |

Win% is estimated from 10,000,000 random six-player rounds per dealing rule,
with six hero observations per round. That is 60,000,000 observed final hands
per rule. Results are reproducible from base seed `20260926`.

For a hero at a six-player table, suppose `L` of the other five hands are
strictly lower. Against `n` randomly selected opponents, the conditional win
contribution is `C(L,n) / C(5,n)`. This reuses each valid physical deal to
estimate 3–6 total-player tables without assuming that players' cards are
independent.

## How rows are grouped

A row is one complete comparison strength from `classify()`, including all
rank and control-card tiebreakers **and the suit of the control card**. Suit is
considered only after the category and rank-based controls are equal; it does
not change the category order.

For example, `9 points, A-K-8` is separated by the suit of its controlling ace,
so an ace of spades and an ace of hearts are different comparison rows. Suit
layouts of the other, non-control cards are still averaged when they do not
change the category or comparison result. This avoids duplicating rows for
irrelevant suits while retaining the suit information that determines the
winner. The same principle applies to the appropriate control card in every
other category.

In a discard variant, a row is conditioned on the selected final strength and
averages over the player's possible unused dealt cards as well. If the exact
discarded cards are known, they remove specific cards from the deck and can
shift the conditional Win% slightly; that more detailed information-state
calculation is outside these final-three-card tables.

## Precision warning

The HTML tables mark rows with fewer than 1,000 observations in orange. Such
rows are valid reachable strengths, but their simulated Win% is less precise
and should be treated as preliminary. The CSV includes both exact hand
frequency and observed sample count so uncertainty is visible rather than
hidden. In the current 10-million-round run, the counts are:

| Dealing rule | Rows below 1,000 | Minimum observations in one row |
|---|---:|---:|
| Deal 3 | 0 | 2,552 |
| Deal 4, discard 1 | 0 | 1,272 |
| Deal 5, discard 2 | 92 | 387 |
| Deal 6, discard 3 | 190 | 47 |

The 1,000-observation marker is a warning threshold, not a guarantee that
every unmarked percentage is exact. Precision should be judged from the sample
count in the current CSV, especially when comparing close percentages.

Run the research again with:

```bash
python3 gaogae_full_winrate.py --rounds 10000000 --output-dir full_winrate
```

Export the colour tables as paginated PNG images with:

```bash
python3 export_winrate_png.py
```

Each full table is limited to 500 data rows per PNG. Multi-page outputs use
suffixes such as `_page_01.png`. Category-only images contain duplicate rows
and are optional through `python3 export_winrate_png.py --mode categories`.
