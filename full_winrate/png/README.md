# PNG exports

- `winrate_summary_6_players.png` — quick one-page comparison.
- `winrate_<variant>_page_01.png`, `_page_02.png`, and so on — complete tables
  for `baseline`, `discard1`, `discard2`, and `discard3` when they require more
  than one page.

Every PNG contains at most 500 data rows, keeping its height within practical
browser screenshot limits. Page counts can change when the strength catalogue
or simulation output changes, so they are intentionally not hard-coded here.

Rows distinguish the confirmed control suit when it affects the winner:
**♠ > ♥ > ♦ > ♣** after category, rank, and other control comparisons are
equal. Non-control suits that cannot affect the result may be averaged into the
same row. This rule produces one live winner, so the displayed strict Win% is
also showdown equity; there is no tie split.

Regenerate the checked-in full tables and summary with:

```bash
python3 export_winrate_png.py
```

Category-only PNGs duplicate subsets of the full tables, so they are not kept
in the project by default. Generate them temporarily when useful with:

```bash
python3 export_winrate_png.py --mode categories
```

Use `--mode all` to generate both sets. The exporter removes stale PNGs in the
selected export scope before writing the new page set.
