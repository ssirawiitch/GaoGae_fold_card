# Full final-hand Win% tables

## What the number means

Each percentage answers one question: **after all players have selected their
final three cards, what is the probability that this hand strength beats every
opponent outright?**

- `Win%` counts only an outright win.
- An exact tie is not counted as a win.
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
| 3 | 22,100 | 741 |
| 4 | 270,725 | 593 |
| 5 | 2,598,960 | 523 |
| 6 | 20,358,520 | 478 |

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
control-card tiebreakers. Physical suit combinations with the same comparison
strength are averaged together. For example, the `9 points, A-K-8` row groups
all non-flush suit layouts of those ranks. This is deliberate: suits have no
order in the working rules, although their removal from the deck can cause
small blocker differences between exact physical hands.

## Precision warning

The HTML tables mark rows with fewer than 1,000 observations in orange. In the
10,000,000-round run, every deal-3, deal-4, and deal-5 row exceeds that mark;
23 extremely rare deal-6 rows remain below it (the smallest has 314 samples).
Those rows are valid but preliminary estimates. The CSV includes both exact
hand frequency and observed sample count so uncertainty is visible rather than
hidden.

Run the research again with:

```bash
python3 gaogae_full_winrate.py --rounds 10000000 --output-dir full_winrate
```

Export the colour tables as full-length and category-sized PNG images with:

```bash
python3 export_winrate_png.py
```
