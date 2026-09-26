# PNG exports

- `winrate_summary_6_players.png` — quick one-page comparison.
- `winrate_baseline.png` — full deal-3 / 2+1 table.
- `winrate_discard1.png` — full deal-4-discard-1 table.
- `winrate_discard2.png` — full deal-5-discard-2 table.
- `winrate_discard3.png` — full deal-6-discard-3 table.
- `baseline/`, `discard1/`, `discard2/`, and `discard3/` — the same results
  split into six shorter images: `tong`, `straight_flush`, `sian`, `straight`,
  `flush`, and `points`.

The full images are intentionally very tall. Use the category images when
reading on screen or sending individual sections.

Regenerate every PNG with:

```bash
python3 export_winrate_png.py
```
