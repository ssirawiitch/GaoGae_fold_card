# ไพ่เก้าเก Research (Gao Gae Strategy Research)

Research project on **เก้าเก (Gao Gae)**, a Thai 3-card betting game (poker-like, no fixed banker) — using combinatorics and Monte Carlo simulation to answer questions that, as far as this research has found, have not been answered rigorously in Thai or English before: which hands are actually strong, and how that depends on the dealing variant in play.

This README is written in English and Thai in the same file. Jump to: [English](#english) | [ภาษาไทย](#ภาษาไทย)

---

## English

### 1. Background

Gao Gae is commonly described as "pokdeng mixed with poker" — 52-card deck, no fixed dealer, players compete directly against each other, 3-card final hands, pot-based betting (ante + bet rounds, fold allowed). Unlike its closest documented relatives — **Three Card Poker** and **Teen Patti**, both of which have published mathematical strategy (e.g. the "Q-6-4" standing threshold for Three Card Poker) — Gao Gae has no rigorous published analysis. It also differs structurally from both in two important ways: (1) it's played multiway with no banker to qualify against, and (2) dealing mechanics vary by house/region, which changes the effective strength of any given hand.

**Session and betting note:** This project models Gao Gae as a continuously played Thai social card game, not a fixed-stack poker tournament. In the play format studied here, players are not eliminated when a fixed stack runs out and funds/points are effectively replenishable, so the strategy objective is long-run expected value per decision rather than bankroll preservation, risk of ruin, or tournament survival. Bet size still matters for pot odds and fold/call value. The working table convention permits bets from **20 to 60 units**, but Gao Gae is governed by local house rules: other groups may use different limits, dealing methods, or betting flows. Future betting models should therefore expose these values as adjustable parameters rather than treat 20–60 as a universal rule.

### 2. Research scope

| # | Topic | Status |
|---|---|---|
| 1 | Survey of rules and variant landscape (dealing methods, hand-ranking order, payout mechanics) | - [x] Done — published as a standalone article |
| 2 | Exact combinatorics of hand rarity under the baseline ruleset | - [x] Done |
| 3 | Final-three-card Win% by dealing rule and total players (3–6) | - [x] Done — suit-aware 10-million-round tables generated and validated |
| 4 | Effect of dealing mechanic on hand strength distribution | - [x] In progress — baseline, 4-discard-1, 5-discard-2, 6-discard-3 compared below; community-card variant still open |
| 5 | Betting game theory (bounded bet size, bluff frequency, Kuhn Poker-style reasoning) | - [ ] Planned |
| 6 | Behavioral tells (qualitative) | - [ ] Planned |

**Current-stage decision:** first measure only the chance that a known final three-card hand wins, separately for each dealing rule and 3–6 total players. Pot size and fold/call decisions are deliberately postponed. A dealing rule must still be fixed because the same nominal hand (e.g. "9 points, no pair") has a very different Win% when opponents selected three cards from 3, 4, 5, or 6 dealt cards.

### 3. Project structure

All simulation code lives in flat Python files (standard library only, no
pip installs needed) meant to be run with `python3 <file>.py`:

| File | What it is | What it's for |
|---|---|---|
| `gaogae_core.py` | Shared engine — not run directly | Hand classifier (`classify`), best-subset picker for discard variants (`best_subset`), deck builder, the Monte Carlo winner-probability engine (legacy function name `simulate_equity`), the shared `EXAMPLE_HANDS` list, and the shared table-printing/CSV-export helper. Every runner script below imports from this file. |
| `gaogae_sim_baseline.py` | Runner script | Win-probability simulation for the baseline dealing variant (deal 3 direct, or 2+1 — same final-hand distribution either way, since there's no discard). Opponents get 3 random cards each with no choice. |
| `gaogae_sim_discard1.py` | Runner script | Win-probability simulation for deal-4-discard-1: every opponent is dealt 4 cards and automatically keeps their best 3. |
| `gaogae_sim_discard2.py` | Runner script | Win-probability simulation for deal-5-discard-2: every opponent is dealt 5 cards and automatically keeps their best 3. |
| `gaogae_sim_discard3.py` | Runner script | Win-probability simulation for deal-6-discard-3: every opponent is dealt 6 cards and automatically keeps their best 3. A 52-card deck supports at most 8 total players in this variant, so the script caps the table at 7 opponents. |
| `gaogae_full_winrate.py` | Full-table runner | Generates every reachable final-hand strength and Win% for 3–6 total players under all four dealing rules. It also exhaustively verifies which strengths can survive optimal discarding. |
| `export_winrate_png.py` | PNG exporter | Uses a locally installed Chrome/Chromium browser in headless mode to save paginated colour-table PNG images (at most 500 rows per image). |
| `full_winrate/` | Research output | Four CSV files, four colour-coded HTML tables, and PNG exports. Open `full_winrate/index.html`; methodology and limitations are in `full_winrate/METHODOLOGY.md`. |
| `RULES.md` | Working rules | English-language research rules, including confirmed hand ranking and the dealing methods still under evaluation. |
| `test_gaogae_core.py` | Automated tests | Regression tests for category order, A-A-A as the highest tong, Sian Riang, control-card suit comparisons, the absence of ties between disjoint physical hands, exact strength counts, and deck limits. |
| `README.md` | This file | Project scope, ruleset assumptions, findings, and file guide. |

Each runner script prints a winner-probability table for every hand in `EXAMPLE_HANDS` against 2 up to 9 opponents where physically possible and writes a `gaogae_equity_<variant>.csv`. The function and CSV retain the legacy word `equity` for compatibility, but under the confirmed one-winner rule `equity_pct` equals `win_pct` and `tie_pct` is always zero. All runners accept `--trials N`, `--max-opponents N`, `--seed N`, `--workers N`, and `--output PATH`. The CSV records its variant, trial count, deal size, and per-hand seed so a run can be reproduced.

The four small example-hand runners are asymmetric fixed-hand benchmarks. In a discard variant they do not condition the hero's unknown extra cards on the listed three-card hand remaining the hero's optimal selection. Use `gaogae_full_winrate.py` and the validated tables in `full_winrate/` for the symmetric final-hand Win% research; the example runners remain useful only for quick exploratory checks.

To add your own hand: edit the `EXAMPLE_HANDS` dictionary near the bottom of `gaogae_core.py` — every runner script picks up the change automatically since they all import from the same place.

### 4. Ruleset assumptions used in all calculations below

Because house rules vary, every number in this document assumes one fixed ruleset (stated explicitly per the project's own working principle — always disclose which variant a number belongs to):

- Hand ranking, high to low: **ตอง (three of a kind) > สเตรทฟลัช (straight flush) > เซียน (three court cards J/Q/K) > เรียง (straight) > สี (flush) > แต้ม (point total 0–9)**
- A-A-A is the highest three of a kind, followed by K-K-K down to 2-2-2
- J-Q-K non-flush ("เซียนเรียง") is a special top sub-rank within เซียน, above any pair-type เซียน (e.g. J-K-K)
- Within เซียน pair-type hands: higher pair rank wins (K > Q > J), then kicker
- Straights include both A-2-3 (ace low) and Q-K-A (ace high); 12 total 3-card sequences
- A counts as 1 point only (never 10/11) for the แต้ม category
- Points are considered only after confirming that a hand is not in any of the five higher categories
- Within แต้ม: compare point total first; for equal points, any pair ("คุม") beats no pair, pairs rank A > K > Q > J > 10 > ... > 2 and then use the kicker, while unpaired hands compare all cards from highest to lowest
- Only after all applicable category, rank, and control-card comparisons are equal, compare the control card's suit: **♠ Spades > ♥ Hearts > ♦ Diamonds > ♣ Clubs**. The control is the highest sequence card for a straight/straight flush (`3` in A-2-3 and `A` in Q-K-A), `K` for J-Q-K, the kicker for a pair-type hand, the highest-ranked card for an unpaired point hand, and the common suit for a flush. A Tong tie is physically impossible with one deck.
- Every physical showdown has exactly one winner, so there is no tied pot or split pot. In this winner-take-all model, Win% is both the probability of winning and the expected fraction of the pot (sometimes called equity); the two values are identical here.
- The session is modeled as continuous play with no binding fixed stack or elimination; bankroll and tournament-risk management are outside the current research scope
- The working house rule uses a minimum bet of 20 and a maximum bet of 60 units; these limits are table-specific and should remain configurable for applying the model to other groups
- No payout convention beyond the pot itself (winner takes the pot; no per-hand multiplier bonus, unlike the related game Pokdeng)

Change any of these and the numbers below shift — that's expected and is exactly why topic 1 (rule survey) matters.

### 5. Findings so far

**5.1 Baseline hand-rarity table** (all 22,100 possible 3-card hands from a 52-card deck, dealt directly with no discard):

| Category | Hands | Probability |
|---|---|---|
| ตอง | 52 | 0.235% |
| สเตรทฟลัช | 48 | 0.217% |
| เซียน | 204 | 0.923% |
| เรียง | 660 | 2.986% |
| สี | 1,096 | 4.959% |
| แต้ม | 20,040 | 90.679% |

Note: สเตรทฟลัช is mathematically rarer than ตอง (48 vs 52 hands), even though ตอง ranks higher in every source found. The likely explanation is that the ranking is tied to the number 9 (the hand ตอง-3 sums to 9, matching the game's name) rather than to strict rarity — unlike standard poker, where the ranking order is rarity-driven.

**5.2 Effect of dealing mechanic on hand strength** (Monte Carlo, 60,000–100,000 trials per variant; "discard" variants pick the best 3-card subset out of the cards dealt):

| Category | Baseline (deal 3 direct) | Deal 4, discard 1 | Deal 5, discard 2 | Deal 6, discard 3 |
|---|---|---|---|---|
| ตอง | 0.24% | 0.90% | 2.28% | 4.42% |
| สเตรทฟลัช | 0.21% | 0.83% | 2.07% | 4.03% |
| เซียน | 0.91% | 3.18% | 6.49% | 10.97% |
| เรียง | 2.89% | 9.70% | 19.25% | 29.17% |
| สี | 5.04% | 14.88% | 26.21% | 31.17% |
| แต้ม (no combo) | 90.71% | 70.51% | 43.70% | 20.24% |
| avg. point value *within* แต้ม-only hands | 4.49 | 7.40 | 8.39 | 8.76 |

Takeaway: the more cards a player gets to choose from, the more the entire hand-strength distribution shifts upward — for *everyone at the table*, not just you. A strong 9-point hand under the baseline deal becomes very weak under deal-6-discard-3, since more than half the table will land a straight, flush, or better. Any Win%/fold-threshold table computed under one dealing variant will give wrong advice under another.

**5.3 Multiway Win% across dealing variants (example hands)**

The example-hand runners apply the confirmed control-suit rule and always produce one physical winner. Their obsolete saved outputs from before that rule were removed; the validated full tables in section 5.4 are now the current numerical source. In this model, reported Win% and the legacy `equity_pct` field are identical; there is no separate tie component.

**5.4 Full final-hand Win% tables (3–6 total players)**

The suit-aware catalog has **2,925** distinct final-hand strength rows under direct deal-3. Exhaustive optimal-selection enumeration leaves **2,323** reachable rows under deal-4-discard-1, **2,049** under deal-5-discard-2, and **1,857** under deal-6-discard-3. The runner regenerates and checks these catalogs before every simulation.

Rows distinguish the suit only when it is the confirmed control suit. Suits that cannot affect the comparison remain averaged together, so the table does not create separate rows for every physical three-card combination. The current files use **10,000,000 six-player rounds per dealing rule**, or **60,000,000 observed final hands per rule**. Validation found no rows below 1,000 observations for deal 3 or deal 4, 92 such rows for deal 5, and 190 for deal 6; the HTML tables mark them in orange. No pot or fold decision is involved at this stage.

### 6. Open items / next steps

- [x] Build the example-hand multiway Win% prototype under all four non-community dealing variants
- [x] Extend the 10 examples into full Win% table generation for all reachable final hands, split by dealing rule and 3–6 total players
- [x] Regenerate and validate the full 10-million-round outputs with the confirmed control-suit rule; flag low-sample rows in the tables
- [ ] Model the community-card variant (2 hole cards + 3 shared cards, pick best 2+1) — this is structurally different because hands become *correlated* across players rather than independent, and needs its own framework
- [ ] Convert Win% into a fold/call table using pot-odds math under the working base pot/ante (40) and bet range (20–60), with both exposed as parameters for other house rules
- [ ] Finalize the still-open house rules in `RULES.md`, especially dealing choice and betting flow
- [ ] Basic bluffing/betting game theory pass, using Kuhn Poker as a simplified theoretical analogue

### 7. Sources consulted (rules survey)

- thaiplayingcard.com — เก้าเก rules overview
- oneball986434189.wordpress.com — game description
- pantip.com/topic/30600900, /topic/33951845 — player discussions on dealing/discard variants
- soccersuck.com — thread with two conflicting hand-ranking orders
- dvdgame.online forums — thread with a third hand-ranking order and the ตอง-3-vs-ตอง-A debate
- casinotouring.org — English-language "Gao Gae" overview
- th.wikipedia.org/wiki/ป๊อกเด้ง, muayacademy.com — Pokdeng payout multiplier system (for comparison)
- panswed.blogspot.com — hand-ranking source matching the ruleset used here
- wizardofodds.com — Three Card Poker / Teen Patti published mathematical strategy (comparative reference)
- arXiv paper on skill-vs-chance quantification in Teen Patti (comparative reference)

---

## ภาษาไทย

### 1. ที่มา

ไพ่เก้าเกมักถูกอธิบายว่าเป็น "ป๊อกเด้งผสมโป๊กเกอร์" — ใช้ไพ่สำรับ 52 ใบ ไม่มีเจ้ามือตายตัว ผู้เล่นแข่งกันตรงๆ ไพ่สุดท้ายมี 3 ใบ เดิมพันแบบกองกลาง (ลงกอง + เดิมพันเป็นรอบ หมอบได้) ต่างจากเกมใกล้เคียงที่มีคนวิจัยจริงจังแล้วอย่าง **Three Card Poker** และ **Teen Patti** (ทั้งคู่มีกลยุทธ์คณิตศาสตร์ตีพิมพ์แล้ว เช่นเกณฑ์ "ยืนไพ่ Q-6-4" ของ Three Card Poker) เก้าเกยังไม่มีงานวิเคราะห์เชิงคณิตศาสตร์อย่างจริงจังมาก่อน และยังต่างจากทั้งสองเกมนี้ในเชิงโครงสร้าง 2 จุด คือ (1) เล่นกันหลายคนไม่มีเจ้ามือให้ผ่านเกณฑ์ และ (2) วิธีแจกไพ่เปลี่ยนไปตามวงเล่น/ภูมิภาค ซึ่งเปลี่ยนความใหญ่ที่แท้จริงของไพ่แต่ละมือ

**หมายเหตุเรื่องรูปแบบวงและการเดิมพัน:** งานนี้มองเก้าเกเป็นเกมไพ่ไทยที่เล่นต่อเนื่องในวงสังคม ไม่ใช่การแข่งขันโป๊กเกอร์แบบมี stack ตายตัว ในรูปแบบวงที่ศึกษา ผู้เล่นไม่ได้ตกรอบเมื่อเงินหรือแต้มกองหนึ่งหมด และสามารถเติมเพื่อเล่นต่อได้ จึงวัดกลยุทธ์จาก Expected Value ระยะยาวของแต่ละการตัดสินใจเป็นหลัก โดยยังไม่เน้นการคุมพอร์ต, ความเสี่ยงเงินหมด หรือการเอาตัวรอดในทัวร์นาเมนต์ อย่างไรก็ตามขนาดเดิมพันยังสำคัญต่อ pot odds และการตัดสินใจหมอบ/สู้ วงที่ใช้เป็นฐานกำหนดเดิมพันขั้นต่ำ **20** และสูงสุด **60** หน่วย แต่เก้าเกใช้กติกาประจำวง วิธีแจก ขอบเขตเดิมพัน และลำดับการเล่นจึงอาจต่างกันได้ โมเดลการเดิมพันขั้นต่อไปควรกำหนดค่าเหล่านี้ให้ปรับได้ เพื่อประยุกต์ใช้กับวงอื่นโดยไม่ถือว่า 20–60 เป็นกติกาสากล

### 2. ขอบเขตงานวิจัย

| # | หัวข้อ | สถานะ |
|---|---|---|
| 1 | สำรวจกติกาและรูปแบบที่พลิกแพลง (วิธีแจก, ลำดับไพ่, กลไกจ่ายเงิน) | - [x] เสร็จแล้ว — เผยแพร่เป็นบทความแยกต่างหาก |
| 2 | คำนวณความหายากของไพ่แต่ละหมวดอย่างละเอียด ภายใต้กติกาพื้นฐาน | - [x] เสร็จแล้ว |
| 3 | Win% ของไพ่ 3 ใบสุดท้าย แยกวิธีแจกและผู้เล่นรวม 3–6 คน | - [x] เสร็จแล้ว — สร้างและตรวจผล 10 ล้านรอบตามกติกาดอกใหม่แล้ว |
| 4 | ผลของกลไกการแจกไพ่ต่อการกระจายความใหญ่ของมือ | - [x] กำลังทำ — เทียบ baseline, 4ทิ้ง1, 5ทิ้ง2, 6ทิ้ง3 ไว้ด้านล่าง ส่วนแบบไพ่กองกลางยังไม่ได้ทำ |
| 5 | Game theory ของการเดิมพัน (ขอบเขตเดิมพันคงที่, ความถี่การบลัฟ, แนวคิดแบบ Kuhn Poker) | - [ ] ยังไม่เริ่ม |
| 6 | การอ่านหน้าตา/พฤติกรรม (เชิงคุณภาพ) | - [ ] ยังไม่เริ่ม |

**ข้อตกลงของงานรอบนี้:** วัดเฉพาะโอกาสที่ไพ่ 3 ใบสุดท้ายซึ่งเรารู้แล้วจะชนะ แยกตามวิธีแจกและจำนวนผู้เล่นรวม 3–6 คน ยังไม่นำขนาดกองกลางมาตัดสินหมอบ/สู้ อย่างไรก็ตามต้องแยกวิธีแจก เพราะไพ่ชื่อเดียวกัน (เช่น 9 แต้มไม่มีคู่) มี Win% ต่างกันมาก เมื่อคู่แข่งเลือก 3 ใบจากไพ่ที่แจก 3, 4, 5 หรือ 6 ใบ

### 3. โครงสร้างโปรเจกต์

โค้ดจำลองทั้งหมดเป็นไฟล์ Python เดี่ยวๆ (ใช้ standard library ล้วน ไม่ต้อง pip install อะไรเพิ่ม) รันด้วยคำสั่ง `python3 <ชื่อไฟล์>.py`:

| ไฟล์ | คืออะไร | ใช้ทำอะไร |
|---|---|---|
| `gaogae_core.py` | Engine กลาง — ไม่ต้องรันเอง | ฟังก์ชันจัดหมวดไพ่ (`classify`), ฟังก์ชันเลือกชุดไพ่ที่ดีที่สุดสำหรับกติกาแบบทิ้งไพ่ (`best_subset`), ตัวสร้างสำรับไพ่, ตัวจำลองโอกาสเป็นผู้ชนะแบบ Monte Carlo (ชื่อฟังก์ชันเดิมคือ `simulate_equity`), ลิสต์ไพ่ตัวอย่าง `EXAMPLE_HANDS` ที่ใช้ร่วมกันทุกไฟล์ และฟังก์ชันช่วยพิมพ์ตาราง/เซฟ CSV ทุกสคริปต์ด้านล่าง import จากไฟล์นี้ทั้งหมด |
| `gaogae_sim_baseline.py` | สคริปต์รัน | จำลองโอกาสชนะสำหรับกติกาแจกพื้นฐาน (แจก 3 ตรง หรือ 2+1 — สองแบบให้ผลการกระจายมือสุดท้ายเหมือนกันเป๊ะ เพราะไม่มีการทิ้งไพ่เลย) คู่ต่อสู้ได้ไพ่สุ่ม 3 ใบตรงๆ ไม่มีทางเลือก |
| `gaogae_sim_discard1.py` | สคริปต์รัน | จำลองโอกาสชนะสำหรับกติกาแจก 4 ทิ้ง 1: คู่ต่อสู้ทุกคนถูกแจก 4 ใบ แล้วเลือกเก็บ 3 ใบที่ดีที่สุดอัตโนมัติ |
| `gaogae_sim_discard2.py` | สคริปต์รัน | จำลองโอกาสชนะสำหรับกติกาแจก 5 ทิ้ง 2: คู่ต่อสู้ทุกคนถูกแจก 5 ใบ แล้วเลือกเก็บ 3 ใบที่ดีที่สุดอัตโนมัติ |
| `gaogae_sim_discard3.py` | สคริปต์รัน | จำลองโอกาสชนะสำหรับกติกาแจก 6 ทิ้ง 3: คู่ต่อสู้ทุกคนถูกแจก 6 ใบ แล้วเลือกเก็บ 3 ใบที่ดีที่สุดอัตโนมัติ ไพ่ 52 ใบรองรับผู้เล่นรวมสูงสุด 8 คน จึงจำลองคู่ต่อสู้ได้ไม่เกิน 7 คน |
| `gaogae_full_winrate.py` | สคริปต์ตารางเต็ม | สร้างอันดับไพ่สุดท้ายที่เกิดได้จริงทั้งหมดและ Win% สำหรับผู้เล่นรวม 3–6 คน ภายใต้วิธีแจกทั้งสี่แบบ พร้อมไล่ครบทุกชุดเพื่อตรวจว่าอันดับใดสามารถเหลืออยู่หลังเลือกไพ่ดีที่สุดได้จริง |
| `export_winrate_png.py` | สคริปต์สร้าง PNG | ใช้ Chrome/Chromium ที่ติดตั้งอยู่ในเครื่องแบบ headless เพื่อบันทึกตารางสีเป็นภาพ PNG แบบแบ่งหน้า (ไม่เกิน 500 แถวต่อภาพ) |
| `full_winrate/` | ผลการวิจัย | CSV 4 ไฟล์ ตาราง HTML ทำสี 4 ไฟล์ และภาพ PNG เปิดดูจาก `full_winrate/index.html`; วิธีคำนวณและข้อจำกัดอยู่ใน `full_winrate/METHODOLOGY.md` |
| `RULES.md` | กติกาทดลอง | กติกาภาษาอังกฤษที่ใช้ในงานวิจัย รวมทั้งลำดับไพ่ที่ยืนยันแล้วและวิธีแจกที่ยังอยู่ระหว่างทดลอง |
| `test_gaogae_core.py` | ชุดทดสอบ | ตรวจลำดับหมวด, AAA สูงสุด, เซียนเรียง, ดอกของตัวคุม, การไม่มีผลเสมอระหว่างไพ่จริงที่ไม่ซ้ำกัน, จำนวนระดับไพ่แบบ exact และข้อจำกัดจำนวนไพ่ |
| `README.md` | ไฟล์นี้ | ขอบเขตโปรเจกต์ สมมติฐานกติกา ผลลัพธ์ที่ได้ และคำอธิบายไฟล์ต่างๆ |

แต่ละสคริปต์จะพิมพ์ตารางโอกาสเป็นผู้ชนะของทุกมือใน `EXAMPLE_HANDS` และเซฟ `gaogae_equity_<variant>.csv` ชื่อฟังก์ชันและคอลัมน์ยังใช้คำว่า `equity` เพื่อให้เข้ากับไฟล์เดิม แต่เมื่อยืนยันว่ามีผู้ชนะคนเดียว `equity_pct` จะเท่ากับ `win_pct` และ `tie_pct` เป็นศูนย์เสมอ รองรับ `--trials N`, `--max-opponents N`, `--seed N`, `--workers N` และ `--output PATH` ภายใน CSV บันทึกวิธีแจก จำนวนรอบ และ seed ของแต่ละมือไว้ให้รันซ้ำได้

สคริปต์ไพ่ตัวอย่างทั้งสี่เป็น benchmark แบบตรึงไพ่ 3 ใบของเราไว้ ในกติกาทิ้งไพ่ สคริปต์เหล่านี้ไม่ได้บังคับว่าไพ่ส่วนเกินที่ไม่รู้ของเราต้องไม่สร้างชุดที่ใหญ่กว่าไพ่ 3 ใบที่ระบุ จึงควรใช้ `gaogae_full_winrate.py` และตารางที่ตรวจผ่านใน `full_winrate/` สำหรับคำถาม Win% ของไพ่สุดท้ายแบบสมมาตร ส่วนสคริปต์ตัวอย่างเหมาะกับการทดลองคร่าวๆ เท่านั้น

ถ้าอยากเพิ่มไพ่ของตัวเอง แก้ไข dictionary `EXAMPLE_HANDS` ใกล้ท้ายไฟล์ `gaogae_core.py` ได้เลย ทุกสคริปต์จะเห็นการเปลี่ยนแปลงอัตโนมัติ เพราะ import จากไฟล์เดียวกันหมด

### 4. สมมติฐานกติกาที่ใช้ในการคำนวณทั้งหมดนี้

เนื่องจากกติกาแต่ละวงไม่เหมือนกัน ตัวเลขทุกตัวในเอกสารนี้อ้างอิงกติกาชุดเดียวที่กำหนดไว้ชัดเจน (ตามหลักการทำงานของโปรเจกต์นี้ — ต้องระบุเสมอว่าตัวเลขอิงกติกาแบบไหน):

- ลำดับไพ่จากใหญ่ไปเล็ก: **ตอง > สเตรทฟลัช > เซียน (J/Q/K สามใบ) > เรียง > สี > แต้ม (0–9)**
- ตอง A-A-A ใหญ่ที่สุด ตามด้วย K-K-K ไล่ลงไปถึง 2-2-2
- J-Q-K ไม่ติดสี ("เซียนเรียง") เป็นระดับสูงสุดพิเศษภายในหมวดเซียน ใหญ่กว่าเซียนแบบมีคู่ (เช่น J-K-K)
- ภายในเซียนแบบมีคู่: คู่อันดับสูงกว่าชนะ (K > Q > J) แล้วจึงดูไพ่เดี่ยวที่เหลือ
- ไพ่เรียงนับทั้ง A-2-3 (เอซต่ำ) และ Q-K-A (เอซสูง) รวม 12 ชุด
- A นับ 1 แต้มเท่านั้น (ไม่นับ 10/11) สำหรับหมวดแต้ม
- จะนับแต้มต่อเมื่อมือไม่เข้าห้าหมวดที่สูงกว่าเท่านั้น
- ภายในหมวดแต้ม: เทียบแต้มรวมก่อน ถ้าเท่ากันมือมีคู่ ("คุม") ชนะมือไม่มีคู่ คู่เรียง A > K > Q > J > 10 > ... > 2 แล้วดูไพ่ใบที่เหลือ ส่วนมือไม่มีคู่ให้ไล่เทียบไพ่จากสูงไปต่ำ
- เมื่อหมวด อันดับไพ่ และการเทียบตัวคุมทุกอย่างเท่ากันแล้วเท่านั้น จึงเทียบดอกของไพ่ตัวคุมตามลำดับ **♠ โพดำ > ♥ โพแดง > ♦ ข้าวหลามตัด > ♣ ดอกจิก** ตัวคุมของเรียง/สเตรทฟลัชคือไพ่สูงสุดของชุด (`3` สำหรับ A-2-3 และ `A` สำหรับ Q-K-A), เซียน J-Q-K ใช้ `K`, มือมีคู่ใช้ไพ่เดี่ยว, มือแต้มไม่มีคู่ใช้ไพ่อันดับสูงสุด และสีใช้ดอกร่วมของมือ ส่วนตองไม่สามารถเสมอกันจริงได้เมื่อใช้ไพ่หนึ่งสำรับ
- การเปิดไพ่จริงมีผู้ชนะเพียงคนเดียว จึงไม่มีการเสมอหรือแบ่งกอง ในโมเดลแบบผู้ชนะรับกองทั้งหมดนี้ Win% คือทั้งโอกาสเป็นผู้ชนะและสัดส่วนกองเฉลี่ยที่บางครั้งเรียกว่า equity ดังนั้นสองค่านี้เท่ากัน
- จำลองเป็นวงเล่นต่อเนื่อง ไม่มี fixed stack ที่เป็นข้อจำกัดและไม่มีการตกรอบ จึงยังไม่รวมการคุมพอร์ตหรือความเสี่ยงแบบทัวร์นาเมนต์ในขอบเขตงาน
- กติกาวงที่ใช้เป็นฐานกำหนดเดิมพันขั้นต่ำ 20 และสูงสุด 60 หน่วย แต่เป็นกติกาประจำวงและต้องปรับค่าได้เมื่อนำโมเดลไปใช้กับวงอื่น
- ไม่มีระบบจ่ายพิเศษอื่นนอกจากกองกลาง (ผู้ชนะกวาดกองไปทั้งหมด ไม่มีโบนัสทวีคูณแบบป๊อกเด้ง)

ถ้าเปลี่ยนข้อไหนในนี้ ตัวเลขด้านล่างจะเปลี่ยนตาม — เป็นเรื่องที่คาดไว้แล้ว และเป็นเหตุผลที่หัวข้อ 1 (สำรวจกติกา) สำคัญ

### 5. ผลที่ได้จนถึงตอนนี้

**5.1 ตารางความหายากพื้นฐาน** (ไพ่ 3 ใบทั้งหมดที่เป็นไปได้ 22,100 มือ จากการแจกตรงไม่มีทิ้งไพ่):

| หมวด | จำนวนมือ | ความน่าจะเป็น |
|---|---|---|
| ตอง | 52 | 0.235% |
| สเตรทฟลัช | 48 | 0.217% |
| เซียน | 204 | 0.923% |
| เรียง | 660 | 2.986% |
| สี | 1,096 | 4.959% |
| แต้ม | 20,040 | 90.679% |

หมายเหตุ: สเตรทฟลัชหายากกว่าตองจริงทางคณิตศาสตร์ (48 เทียบกับ 52 มือ) แม้ทุกแหล่งข้อมูลที่พบจะให้ตองใหญ่กว่า คำอธิบายที่น่าจะเป็นไปได้มากที่สุดคือ ลำดับไพ่ผูกกับเลข 9 (ตอง-3 รวมแต้มได้ 9 ตรงกับชื่อเกม) มากกว่าอิงความหายากล้วนๆ ต่างจากโป๊กเกอร์สากลที่ลำดับไพ่อิงความหายากเป็นหลัก

**5.2 ผลของกลไกการแจกไพ่ต่อความใหญ่ของมือ** (Monte Carlo 60,000–100,000 รอบต่อกติกา; กติกาแบบ "ทิ้งไพ่" คือเลือกชุด 3 ใบที่ดีที่สุดจากไพ่ที่แจกมา):

| หมวด | Baseline (แจก 3 ตรง) | แจก 4 ทิ้ง 1 | แจก 5 ทิ้ง 2 | แจก 6 ทิ้ง 3 |
|---|---|---|---|---|
| ตอง | 0.24% | 0.90% | 2.28% | 4.42% |
| สเตรทฟลัช | 0.21% | 0.83% | 2.07% | 4.03% |
| เซียน | 0.91% | 3.18% | 6.49% | 10.97% |
| เรียง | 2.89% | 9.70% | 19.25% | 29.17% |
| สี | 5.04% | 14.88% | 26.21% | 31.17% |
| แต้ม (ไม่ติดคอมโบ) | 90.71% | 70.51% | 43.70% | 20.24% |
| แต้มเฉลี่ย เฉพาะกลุ่มแต้มล้วน | 4.49 | 7.40 | 8.39 | 8.76 |

สรุป: ยิ่งได้เลือกไพ่จากใบที่มากขึ้น การกระจายความใหญ่ของมือทั้งกระดาน**ขยับขึ้นสำหรับทุกคนบนโต๊ะ ไม่ใช่แค่เรา** ไพ่ 9 แต้มที่แข็งในกติกาพื้นฐานจะอ่อนลงมากในกติกาแจก 6 ทิ้ง 3 เพราะคนกว่าครึ่งโต๊ะจะได้เรียงหรือสีขึ้นไป ตาราง Win% หรือเกณฑ์หมอบที่คำนวณจากกติกาหนึ่ง เอาไปใช้กับอีกกติกาหนึ่งจะให้คำแนะนำที่ผิด

**5.3 Win% แบบหลายคนแยกตามวิธีแจก (ตัวอย่างบางมือ)**

สคริปต์ไพ่ตัวอย่างใช้กติกาดอกของตัวคุมที่ยืนยันล่าสุดแล้ว และไพ่จริงทุกโต๊ะจะมีผู้ชนะหนึ่งคน ไฟล์ผลตัวอย่างเก่าที่สร้างก่อนเพิ่มกติกานี้ถูกลบออกแล้ว โดยใช้ตารางเต็มที่ตรวจผ่านในหัวข้อ 5.4 เป็นแหล่งตัวเลขปัจจุบัน ภายใต้โมเดลใหม่ Win% กับคอลัมน์เดิม `equity_pct` มีค่าเท่ากัน และไม่มีส่วนของผลเสมอแยกต่างหาก

**5.4 ตาราง Win% เต็มของไพ่ 3 ใบสุดท้าย (ผู้เล่นรวม 3–6 คน)**

แคตตาล็อกที่แยกดอกตัวคุมมีระดับไพ่สุดท้าย **2,925 แถว** สำหรับแจก 3 ตรง เมื่อตรวจแบบ exact และเลือกไพ่ที่ดีที่สุด จะเหลือระดับที่เกิดได้จริง **2,323 แถว** สำหรับแจก 4 ทิ้ง 1, **2,049 แถว** สำหรับแจก 5 ทิ้ง 2 และ **1,857 แถว** สำหรับแจก 6 ทิ้ง 3 โดยสคริปต์จะสร้างและตรวจแคตตาล็อกเหล่านี้ใหม่ก่อนจำลองทุกครั้ง

แต่ละแถวจะแยกดอกเฉพาะเมื่อดอกนั้นเป็นดอกของตัวคุมตามกติกา ส่วนดอกที่ไม่มีผลต่อการเปรียบเทียบจะยังถูกรวมเฉลี่ยอยู่ จึงไม่จำเป็นต้องสร้างหนึ่งแถวต่อไพ่จริงทั้ง 22,100 ชุด ผลปัจจุบันใช้ **10,000,000 โต๊ะ 6 คนต่อวิธีแจก** หรือ **60,000,000 ตัวอย่างไพ่สุดท้ายต่อวิธี** จากการตรวจพบว่าแจก 3 และแจก 4 ไม่มีแถวต่ำกว่า 1,000 ตัวอย่าง แจก 5 มี 92 แถว และแจก 6 มี 190 แถว ซึ่งตาราง HTML ทำเครื่องหมายสีส้มไว้ ขั้นนี้ยังไม่เกี่ยวกับเงินกองกลางหรือการหมอบ

### 6. สิ่งที่ยังค้างอยู่ / ขั้นตอนถัดไป

- [x] สร้างต้นแบบ Win% ของไพ่ตัวอย่างครบทั้งสี่วิธีแจกที่ไม่ใช้ไพ่กลางแล้ว
- [x] ขยายจากไพ่ตัวอย่าง 10 มือเป็นตัวสร้างตาราง Win% เต็ม แยกวิธีแจกและผู้เล่นรวม 3–6 คน
- [x] รันและตรวจตารางเต็ม 10 ล้านรอบใหม่ด้วยกติกาดอกของตัวคุม พร้อมทำเครื่องหมายแถวตัวอย่างน้อยในตาราง
- [ ] สร้างโมเดลกติกาแบบไพ่กองกลาง (2 ใบส่วนตัว + 3 ใบกลาง เลือกดีที่สุด 2+1) — โครงสร้างต่างออกไปเพราะไพ่แต่ละคน**สัมพันธ์กัน**ไม่เป็นอิสระเหมือนกติกาอื่น ต้องมีกรอบคิดแยกต่างหาก
- [ ] แปลง Win% เป็นตารางหมอบ/สู้จริง โดยใช้ pot odds กับกองกลาง/ค่าเริ่มต้น 40 และช่วงเดิมพัน 20–60 ตามกติกาฐาน พร้อมทำให้ค่าทั้งหมดปรับได้สำหรับวงอื่น
- [ ] สรุปกติกาที่ยังเปิดอยู่ใน `RULES.md` โดยเฉพาะวิธีแจกและลำดับเดิมพัน
- [ ] ทำ game theory เบื้องต้นเรื่องการเดิมพัน/บลัฟ โดยใช้ Kuhn Poker เป็นกรอบทฤษฎีอย่างง่ายเทียบเคียง

### 7. แหล่งข้อมูลที่ใช้ (ช่วงสำรวจกติกา)

- thaiplayingcard.com — ภาพรวมกติกาเก้าเก
- oneball986434189.wordpress.com — คำอธิบายเกม
- pantip.com/topic/30600900, /topic/33951845 — กระทู้ถกเรื่องวิธีแจก/ทิ้งไพ่
- soccersuck.com — กระทู้ที่มีลำดับไพ่ขัดแย้งกัน 2 แบบ
- dvdgame.online forums — กระทู้ที่มีลำดับไพ่แบบที่ 3 และดีเบตตอง3 vs ตองเอ
- casinotouring.org — ภาพรวมเก้าเกเป็นภาษาอังกฤษ ("Gao Gae")
- th.wikipedia.org/wiki/ป๊อกเด้ง, muayacademy.com — ระบบจ่ายทวีคูณของป๊อกเด้ง (ใช้เทียบเคียง)
- panswed.blogspot.com — แหล่งลำดับไพ่ที่ตรงกับกติกาที่ใช้ในเอกสารนี้
- wizardofodds.com — กลยุทธ์คณิตศาสตร์ของ Three Card Poker / Teen Patti (ใช้เทียบเคียง)
- เปเปอร์ arXiv เรื่องการวัด skill-vs-chance ของ Teen Patti (ใช้เทียบเคียง)
