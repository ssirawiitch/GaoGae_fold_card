"""Render the generated Gao Gae HTML win-rate tables as full-length PNGs.

This uses an installed Chrome/Chromium browser in headless mode, so the PNG
looks the same as the colour-coded HTML table and no plotting package is
required.

Run after ``gaogae_full_winrate.py``:

    python3 export_winrate_png.py

By default it writes four full-length images, category-sized images, and one
quick comparison image to ``full_winrate/png/``.
"""

import argparse
import csv
import html
import os
import shutil
import subprocess
from collections import defaultdict
from pathlib import Path
from urllib.parse import quote

from gaogae_full_winrate import heat_color, write_html


VARIANTS = (
    ('baseline', 'Deal 3 / 2+1'),
    ('discard1', 'Deal 4, discard 1'),
    ('discard2', 'Deal 5, discard 2'),
    ('discard3', 'Deal 6, discard 3'),
)
CATEGORY_SLUG = {
    'Tong (three of a kind)': 'tong',
    'Straight flush': 'straight_flush',
    'Sian (three court cards J/Q/K)': 'sian',
    'Straight (Riang)': 'straight',
    'Flush (See)': 'flush',
    'Point total (Tam)': 'points',
}
SUMMARY_HANDS = (
    'Tong A-A-A',
    'Tong K-K-K',
    'Straight flush Q-K-A',
    'Sian J-Q-K',
    'Straight 10-J-Q',
    'Flush K-9-4',
    '9 points, pair 9, kicker A',
    '9 points, A-K-8',
)
PROJECT_DIR = Path(__file__).resolve().parent
STATIC_BROWSER_CANDIDATES = (
    '/mnt/c/Program Files/Google/Chrome/Application/chrome.exe',
    '/mnt/c/Program Files (x86)/Microsoft/Edge/Application/msedge.exe',
    '/usr/bin/google-chrome',
    '/usr/bin/chromium',
    '/usr/bin/chromium-browser',
)


def find_browser(explicit=None):
    if explicit:
        path = Path(explicit)
        if not path.is_file():
            raise FileNotFoundError(f'Browser not found: {path}')
        return path
    candidates = list(STATIC_BROWSER_CANDIDATES)
    if os.name == 'nt':
        program_files = os.environ.get('PROGRAMFILES')
        program_files_x86 = os.environ.get('PROGRAMFILES(X86)')
        local_app_data = os.environ.get('LOCALAPPDATA')
        if program_files:
            candidates.extend((
                str(Path(program_files) / 'Google/Chrome/Application/chrome.exe'),
                str(Path(program_files) / 'Microsoft/Edge/Application/msedge.exe'),
            ))
        if program_files_x86:
            candidates.extend((
                str(Path(program_files_x86) / 'Google/Chrome/Application/chrome.exe'),
                str(Path(program_files_x86) / 'Microsoft/Edge/Application/msedge.exe'),
            ))
        if local_app_data:
            candidates.extend((
                str(Path(local_app_data) / 'Google/Chrome/Application/chrome.exe'),
                str(Path(local_app_data) / 'Microsoft/Edge/Application/msedge.exe'),
            ))

    for command in ('chrome', 'google-chrome', 'chromium', 'chromium-browser',
                    'msedge'):
        discovered = shutil.which(command)
        if discovered:
            candidates.append(discovered)

    for candidate in candidates:
        path = Path(candidate)
        if path.is_file():
            return path
    raise FileNotFoundError(
        'Chrome/Chromium was not found. Pass its path with --browser.'
    )


def is_windows_executable(path):
    return path.suffix.lower() == '.exe'


def windows_path(path):
    """Return a native Windows path, translating /mnt/c when under WSL."""
    if os.name == 'nt':
        return str(path.resolve())
    resolved = path.resolve().as_posix()
    parts = resolved.split('/')
    if len(parts) < 4 or parts[1] != 'mnt' or len(parts[2]) != 1:
        raise ValueError(f'Cannot translate this path for Windows: {resolved}')
    drive = parts[2].upper()
    remainder = '\\'.join(parts[3:])
    return f'{drive}:\\{remainder}'


def browser_file_url(path, browser):
    if os.name == 'nt':
        return path.resolve().as_uri()
    if is_windows_executable(browser):
        native = windows_path(path).replace('\\', '/')
        return 'file:///' + quote(native, safe='/:')
    return path.resolve().as_uri()


def browser_output_path(path, browser):
    if os.name == 'nt':
        return str(path.resolve())
    return windows_path(path) if is_windows_executable(browser) else str(path.resolve())


def csv_row_count(path):
    with path.open(encoding='utf-8-sig', newline='') as source:
        return sum(1 for _row in csv.DictReader(source))


def read_csv_rows(path):
    with path.open(encoding='utf-8-sig', newline='') as source:
        rows = list(csv.DictReader(source))
    for row in rows:
        row['observed_final_hands'] = int(row['observed_final_hands'])
    return rows


def render_png(browser, html_path, png_path, profile_path, width, height):
    png_path.parent.mkdir(parents=True, exist_ok=True)
    command = [
        str(browser),
        '--headless=new',
        '--disable-gpu',
        '--hide-scrollbars',
        '--no-first-run',
        '--no-default-browser-check',
        '--force-device-scale-factor=1',
        f'--window-size={width},{height}',
        f'--user-data-dir={browser_output_path(profile_path, browser)}',
        f'--screenshot={browser_output_path(png_path, browser)}',
        browser_file_url(html_path, browser),
    ]
    completed = subprocess.run(
        command,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    if completed.returncode != 0 or not png_path.is_file():
        raise RuntimeError(
            f'Browser PNG export failed for {html_path.name}:\n{completed.stdout}'
        )


def write_summary_html(path, all_rows):
    """Write a compact comparison of representative hands for six players."""
    lookup = {
        variant: {row['hand']: row for row in rows}
        for variant, rows in all_rows.items()
    }
    header = ''.join(
        f'<th>{html.escape(label)}</th>' for _key, label in VARIANTS
    )
    body = []
    for hand in SUMMARY_HANDS:
        cells = []
        for key, _label in VARIANTS:
            row = lookup[key].get(hand)
            if row is None:
                cells.append('<td class="missing">N/A</td>')
                continue
            value = float(row['win_6_players_pct'])
            cells.append(
                f'<td class="pct" style="background:{heat_color(value)}">'
                f'{value:.2f}%</td>'
            )
        body.append(f'<tr><td>{html.escape(hand)}</td>{"".join(cells)}</tr>')

    document = f'''<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Gao Gae Win% quick comparison</title>
<style>
body {{ font: 18px/1.4 system-ui,sans-serif; margin: 38px; color: #172033; }}
h1 {{ margin: 0 0 8px; }} p {{ color: #475569; margin: 0 0 24px; }}
table {{ border-collapse: collapse; width: 100%; }}
th {{ background: #172033; color: white; }}
th,td {{ border: 1px solid #cbd5e1; padding: 14px 16px; }}
td:first-child {{ font-weight: 650; }}
td.pct {{ text-align: right; font-weight: 700; font-variant-numeric: tabular-nums; }}
td.missing {{ background:#e5e7eb; text-align:center; }}
</style></head><body>
<h1>Gao Gae strict Win% — quick comparison</h1>
<p>Six total players. Exact ties do not count as wins. Full tables include 3–6 players.</p>
<table><thead><tr><th>Final hand</th>{header}</tr></thead>
<tbody>{''.join(body)}</tbody></table></body></html>'''
    path.write_text(document, encoding='utf-8')


def parse_args():
    parser = argparse.ArgumentParser(
        description='Save the four generated Gao Gae win-rate tables as PNG.'
    )
    parser.add_argument('--input-dir', default=str(PROJECT_DIR / 'full_winrate'),
                        help='Directory containing generated HTML/CSV tables')
    parser.add_argument('--output-dir', default=str(PROJECT_DIR / 'full_winrate/png'),
                        help='Directory for PNG files')
    parser.add_argument('--browser', help='Chrome/Chromium executable path')
    parser.add_argument('--width', type=int, default=1400,
                        help='PNG width in pixels (default 1400)')
    parser.add_argument('--mode', choices=('all', 'full', 'categories'), default='all',
                        help='Export all images, only full tables, or category/summary '
                             'images (default all)')
    return parser.parse_args()


def main():
    args = parse_args()
    input_dir = Path(args.input_dir).resolve()
    output_dir = Path(args.output_dir).resolve()
    browser = find_browser(args.browser)
    profile_path = output_dir / '.chrome-png-profile'
    source_path = output_dir / '.png-source'
    all_rows = {}

    try:
        for variant, _short_name in VARIANTS:
            html_path = input_dir / f'winrate_{variant}.html'
            csv_path = input_dir / f'winrate_{variant}.csv'
            if not html_path.is_file() or not csv_path.is_file():
                raise FileNotFoundError(
                    f'Missing {html_path.name} or {csv_path.name}; '
                    'run gaogae_full_winrate.py first.'
                )
            rows = read_csv_rows(csv_path)
            all_rows[variant] = rows

            if args.mode in ('all', 'full'):
                # Current HTML rows are approximately 34 px high. Extra space
                # covers margins, title, explanatory note, and table header.
                height = 230 + 34 * (len(rows) + 1)
                png_path = output_dir / f'winrate_{variant}.png'
                print(f'{variant}: {len(rows)} rows -> '
                      f'{args.width}x{height}px', flush=True)
                render_png(
                    browser, html_path, png_path, profile_path,
                    width=args.width, height=height,
                )
                print(f'  wrote {png_path}', flush=True)

            if args.mode in ('all', 'categories'):
                grouped = defaultdict(list)
                for row in rows:
                    grouped[row['category']].append(row)
                for category, category_rows in grouped.items():
                    slug = CATEGORY_SLUG[category]
                    category_html = source_path / f'{variant}_{slug}.html'
                    category_html.parent.mkdir(parents=True, exist_ok=True)
                    title = f'{rows[0]["variant_name"]} — {category}'
                    write_html(
                        category_html,
                        category_rows,
                        title,
                        int(rows[0]['rounds']),
                        int(rows[0]['seed']),
                    )
                    height = 230 + 34 * (len(category_rows) + 1)
                    png_path = output_dir / variant / f'{slug}.png'
                    render_png(
                        browser, category_html, png_path, profile_path,
                        width=args.width, height=height,
                    )
                print(f'  wrote {len(grouped)} category images to '
                      f'{output_dir / variant}', flush=True)

        if args.mode in ('all', 'categories'):
            summary_html = source_path / 'summary.html'
            source_path.mkdir(parents=True, exist_ok=True)
            write_summary_html(summary_html, all_rows)
            summary_png = output_dir / 'winrate_summary_6_players.png'
            render_png(
                browser, summary_html, summary_png, profile_path,
                width=args.width, height=720,
            )
            print(f'wrote {summary_png}', flush=True)
    finally:
        if profile_path.exists():
            shutil.rmtree(profile_path)
        if source_path.exists():
            shutil.rmtree(source_path)


if __name__ == '__main__':
    main()
