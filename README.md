# ไพ่เก้าเก Research (Gao Gae Strategy Research)

Research project on **เก้าเก (Gao Gae)**, a Thai 3-card betting game (poker-like, no fixed banker) — using combinatorics and Monte Carlo simulation to answer questions that, as far as this research has found, have not been answered rigorously in Thai or English before: which hands are actually strong, and how that depends on the dealing variant in play.

This README is written in English and Thai in the same file. Jump to: [English](#english) | [ภาษาไทย](#ภาษาไทย)

---

## English

### 1. Background

Gao Gae is commonly described as "pokdeng mixed with poker" — 52-card deck, no fixed dealer, players compete directly against each other, 3-card final hands, pot-based betting (ante + bet rounds, fold allowed). Unlike its closest documented relatives — **Three Card Poker** and **Teen Patti**, both of which have published mathematical strategy (e.g. the "Q-6-4" standing threshold for Three Card Poker) — Gao Gae has no rigorous published analysis. It also differs structurally from both in two important ways: (1) it's played multiway with no banker to qualify against, and (2) dealing mechanics vary by house/region, which changes the effective strength of any given hand.

### 2. Research scope

| # | Topic | Status |
|---|---|---|
| 1 | Survey of rules and variant landscape (dealing methods, hand-ranking order, payout mechanics) | - [x] Done — published as a standalone article |
| 2 | Exact combinatorics of hand rarity under the baseline ruleset | - [x] Done |
| 3 | Multiway equity / fold-or-call thresholds by number of opponents (2–9) | - [x] Prototype done for baseline dealing; full table pending |
| 4 | Effect of dealing mechanic on hand strength distribution | - [x] In progress — baseline, 4-discard-1, 5-discard-2, 6-discard-3 compared below; community-card variant still open |
| 5 | Betting game theory (bounded bet size, bluff frequency, Kuhn Poker-style reasoning) | - [ ] Planned |
| 6 | Behavioral tells (qualitative) | - [ ] Planned |

**Key design decision (from this stage of the project):** topics 3 and 4 must be combined, not treated separately. A fold threshold is only meaningful once the dealing variant is fixed, because the same nominal hand (e.g. "9 points, no pair") means something completely different depending on how many cards you got to choose from. The end goal is a single lookup table indexed by **(number of live opponents) × (dealing variant) → recommended fold/call threshold**.

### 3. Project structure

All simulation code lives in flat Python files (standard library only, no
pip installs needed) meant to be run with `python3 <file>.py`:

| File | What it is | What it's for |
|---|---|---|
| `gaogae_core.py` | Shared engine — not run directly | Hand classifier (`classify`), best-subset picker for discard variants (`best_subset`), deck builder, the Monte Carlo equity engine (`simulate_equity`), the shared `EXAMPLE_HANDS` list, and the shared table-printing/CSV-export helper. Every runner script below imports from this file. |
| `gaogae_sim_baseline.py` | Runner script | Equity simulation for the baseline dealing variant (deal 3 direct, or 2+1 — same final-hand distribution either way, since there's no discard). Opponents get 3 random cards each with no choice. |
| `gaogae_sim_discard1.py` | Runner script | Equity simulation for deal-4-discard-1: every opponent is dealt 4 cards and automatically keeps their best 3. |
| `gaogae_sim_discard2.py` | Runner script | Equity simulation for deal-5-discard-2: every opponent is dealt 5 cards and automatically keeps their best 3. |
| `gaogae_sim_discard3.py` | Runner script | Equity simulation for deal-6-discard-3: every opponent is dealt 6 cards and automatically keeps their best 3. Note: with 6 cards/opponent, the deck can't physically supply more than 8 opponents (49 // 6), so this script auto-caps and prints a notice instead of silently producing wrong results. |
| `README.md` | This file | Project scope, ruleset assumptions, findings, and file guide. |

Each runner script prints an equity table to the terminal (win/tie/equity % for every hand in `EXAMPLE_HANDS`, against 2 up to 9 opponents) and also writes a `gaogae_equity_<variant>.csv` with the same data broken out into separate win/tie/equity columns, for further analysis. All four runners accept `--trials N` (simulation precision vs. speed trade-off, default 60,000) and `--max-opponents N` (default 9).

To add your own hand: edit the `EXAMPLE_HANDS` dictionary near the bottom of `gaogae_core.py` — every runner script picks up the change automatically since they all import from the same place.

### 4. Ruleset assumptions used in all calculations below

Because house rules vary, every number in this document assumes one fixed ruleset (stated explicitly per the project's own working principle — always disclose which variant a number belongs to):

- Hand ranking, high to low: **ตอง (three of a kind) > สเตรทฟลัช (straight flush) > เซียน (three court cards J/Q/K) > เรียง (straight) > สี (flush) > แต้ม (point total 0–9)**
- J-Q-K non-flush ("เซียนเรียง") is a special top sub-rank within เซียน, above any pair-type เซียน (e.g. J-K-K)
- Within เซียน pair-type hands: higher pair rank wins (K > Q > J), then kicker
- Straights include both A-2-3 (ace low) and Q-K-A (ace high); 12 total 3-card sequences
- A counts as 1 point only (never 10/11) for the แต้ม category
- Within แต้ม: point total (0–9) is compared first; if tied, a pair ("คุม") wins; if pairs tie, higher pair rank wins
- No table-stakes conventions beyond a pot-based payout (winner takes the pot; no per-hand multiplier bonus, unlike the related game Pokdeng)

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

Takeaway: the more cards a player gets to choose from, the more the entire hand-strength distribution shifts upward — for *everyone at the table*, not just you. A "9 points, no pair" hand is a near-lock winner under the baseline deal but only a middling hand under deal-6-discard-3, since more than half the table will land a straight, flush, or better. Any equity/fold-threshold table computed under one dealing variant will give wrong advice under another.

**4.3 Multiway equity (baseline dealing variant only, example hands)**

Prototype Monte Carlo simulation showing win/tie probability ("equity") for a fixed hand against N random opponents (N = 2–9), baseline dealing only. Full write-up and chart produced earlier in this research thread; not reproduced here in full. Headline pattern: strong categories (เซียน, เรียง) stay above ~88% equity even against 9 opponents; แต้ม-only hands fall off sharply as opponent count rises, and fall off *faster* when they have no pair even at equal point totals — confirming the "คุม" tie-break rule has real practical weight, not just tie-breaking value.

### 6. Open items / next steps

- [ ] Extend the multiway equity simulation to run under each dealing variant separately (not just baseline) — opponents' hands must be generated through the same discard process, not treated as raw random 3-card draws
- [ ] Model the community-card variant (2 hole cards + 3 shared cards, pick best 2+1) — this is structurally different because hands become *correlated* across players rather than independent, and needs its own framework
- [ ] Convert equity numbers into an actual fold/call table using real pot-odds math, given the ante (40) and bet range (20–60) described in the base ruleset
- [ ] Cross-check the assumed ruleset (esp. hand-ranking order and A-high vs A-low tong convention) against a real playing group, since multiple conflicting house rules were found during the rules survey
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

### 2. ขอบเขตงานวิจัย

| # | หัวข้อ | สถานะ |
|---|---|---|
| 1 | สำรวจกติกาและรูปแบบที่พลิกแพลง (วิธีแจก, ลำดับไพ่, กลไกจ่ายเงิน) | - [x] เสร็จแล้ว — เผยแพร่เป็นบทความแยกต่างหาก |
| 2 | คำนวณความหายากของไพ่แต่ละหมวดอย่างละเอียด ภายใต้กติกาพื้นฐาน | - [x] เสร็จแล้ว |
| 3 | Equity แบบหลายคน / เกณฑ์หมอบ-สู้ ตามจำนวนคู่ต่อสู้ (2–9 คน) | - [x] ทำต้นแบบสำหรับการแจกไพ่พื้นฐานแล้ว ตารางเต็มยังไม่เสร็จ |
| 4 | ผลของกลไกการแจกไพ่ต่อการกระจายความใหญ่ของมือ | - [x] กำลังทำ — เทียบ baseline, 4ทิ้ง1, 5ทิ้ง2, 6ทิ้ง3 ไว้ด้านล่าง ส่วนแบบไพ่กองกลางยังไม่ได้ทำ |
| 5 | Game theory ของการเดิมพัน (ขอบเขตเดิมพันคงที่, ความถี่การบลัฟ, แนวคิดแบบ Kuhn Poker) | - [ ] ยังไม่เริ่ม |
| 6 | การอ่านหน้าตา/พฤติกรรม (เชิงคุณภาพ) | - [ ] ยังไม่เริ่ม |

**การตัดสินใจสำคัญของโปรเจกต์นี้:** หัวข้อ 3 กับ 4 ต้องทำรวมกัน แยกกันไม่ได้ เพราะเกณฑ์หมอบจะมีความหมายก็ต่อเมื่อรู้แล้วว่าเล่นกติกาแจกไพ่แบบไหน — ไพ่ชื่อเดียวกัน (เช่น "9 แต้มไม่มีคู่") มีความหมายต่างกันโดยสิ้นเชิงตามจำนวนใบที่ได้เลือก เป้าหมายสุดท้ายคือตารางเดียวที่ค้นตามแกน **(จำนวนคู่ต่อสู้ที่เหลือ) × (วิธีแจกไพ่) → เกณฑ์แนะนำหมอบ/สู้**

### 3. โครงสร้างโปรเจกต์

โค้ดจำลองทั้งหมดเป็นไฟล์ Python เดี่ยวๆ (ใช้ standard library ล้วน ไม่ต้อง pip install อะไรเพิ่ม) รันด้วยคำสั่ง `python3 <ชื่อไฟล์>.py`:

| ไฟล์ | คืออะไร | ใช้ทำอะไร |
|---|---|---|
| `gaogae_core.py` | Engine กลาง — ไม่ต้องรันเอง | ฟังก์ชันจัดหมวดไพ่ (`classify`), ฟังก์ชันเลือกชุดไพ่ที่ดีที่สุดสำหรับกติกาแบบทิ้งไพ่ (`best_subset`), ตัวสร้างสำรับไพ่, ตัวจำลอง equity แบบ Monte Carlo (`simulate_equity`), ลิสต์ไพ่ตัวอย่าง `EXAMPLE_HANDS` ที่ใช้ร่วมกันทุกไฟล์ และฟังก์ชันช่วยพิมพ์ตาราง/เซฟ CSV ทุกสคริปต์ด้านล่าง import จากไฟล์นี้ทั้งหมด |
| `gaogae_sim_baseline.py` | สคริปต์รัน | จำลอง equity สำหรับกติกาแจกพื้นฐาน (แจก 3 ตรง หรือ 2+1 — สองแบบให้ผลการกระจายมือสุดท้ายเหมือนกันเป๊ะ เพราะไม่มีการทิ้งไพ่เลย) คู่ต่อสู้ได้ไพ่สุ่ม 3 ใบตรงๆ ไม่มีทางเลือก |
| `gaogae_sim_discard1.py` | สคริปต์รัน | จำลอง equity สำหรับกติกาแจก 4 ทิ้ง 1: คู่ต่อสู้ทุกคนถูกแจก 4 ใบ แล้วเลือกเก็บ 3 ใบที่ดีที่สุดอัตโนมัติ |
| `gaogae_sim_discard2.py` | สคริปต์รัน | จำลอง equity สำหรับกติกาแจก 5 ทิ้ง 2: คู่ต่อสู้ทุกคนถูกแจก 5 ใบ แล้วเลือกเก็บ 3 ใบที่ดีที่สุดอัตโนมัติ |
| `gaogae_sim_discard3.py` | สคริปต์รัน | จำลอง equity สำหรับกติกาแจก 6 ทิ้ง 3: คู่ต่อสู้ทุกคนถูกแจก 6 ใบ แล้วเลือกเก็บ 3 ใบที่ดีที่สุดอัตโนมัติ หมายเหตุ: พอแจกคนละ 6 ใบ ไพ่ในสำรับจะไม่พอสำหรับคู่ต่อสู้เกิน 8 คน (49 // 6) สคริปต์นี้จะลดจำนวนอัตโนมัติและแจ้งเตือน แทนที่จะให้ผลลัพธ์ผิดแบบเงียบๆ |
| `README.md` | ไฟล์นี้ | ขอบเขตโปรเจกต์ สมมติฐานกติกา ผลลัพธ์ที่ได้ และคำอธิบายไฟล์ต่างๆ |

แต่ละสคริปต์รันแล้วจะพิมพ์ตาราง equity ออกทางหน้าจอ (win/tie/equity % ของทุกมือใน `EXAMPLE_HANDS` เทียบกับคู่ต่อสู้ 2-9 คน) และเซฟไฟล์ `gaogae_equity_<variant>.csv` ที่มีข้อมูลเดียวกันแยกคอลัมน์ win/tie/equity ไว้ให้ต่อยอดวิเคราะห์ได้ ทุกสคริปต์รับ `--trials N` (ปรับความแม่นยำ vs ความเร็ว, default 60,000) และ `--max-opponents N` (default 9)

ถ้าอยากเพิ่มไพ่ของตัวเอง แก้ไข dictionary `EXAMPLE_HANDS` ใกล้ท้ายไฟล์ `gaogae_core.py` ได้เลย ทุกสคริปต์จะเห็นการเปลี่ยนแปลงอัตโนมัติ เพราะ import จากไฟล์เดียวกันหมด

### 4. สมมติฐานกติกาที่ใช้ในการคำนวณทั้งหมดนี้

เนื่องจากกติกาแต่ละวงไม่เหมือนกัน ตัวเลขทุกตัวในเอกสารนี้อ้างอิงกติกาชุดเดียวที่กำหนดไว้ชัดเจน (ตามหลักการทำงานของโปรเจกต์นี้ — ต้องระบุเสมอว่าตัวเลขอิงกติกาแบบไหน):

- ลำดับไพ่จากใหญ่ไปเล็ก: **ตอง > สเตรทฟลัช > เซียน (J/Q/K สามใบ) > เรียง > สี > แต้ม (0–9)**
- J-Q-K ไม่ติดสี ("เซียนเรียง") เป็นระดับสูงสุดพิเศษภายในหมวดเซียน ใหญ่กว่าเซียนแบบมีคู่ (เช่น J-K-K)
- ภายในเซียนแบบมีคู่: คู่อันดับสูงกว่าชนะ (K > Q > J) แล้วจึงดูไพ่เดี่ยวที่เหลือ
- ไพ่เรียงนับทั้ง A-2-3 (เอซต่ำ) และ Q-K-A (เอซสูง) รวม 12 ชุด
- A นับ 1 แต้มเท่านั้น (ไม่นับ 10/11) สำหรับหมวดแต้ม
- ภายในหมวดแต้ม: เทียบแต้มรวม (0–9) ก่อน ถ้าเท่ากันคู่ ("คุม") ชนะ ถ้าคู่เท่ากันดูอันดับคู่ที่สูงกว่า
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

สรุป: ยิ่งได้เลือกไพ่จากใบที่มากขึ้น การกระจายความใหญ่ของมือทั้งกระดาน**ขยับขึ้นสำหรับทุกคนบนโต๊ะ ไม่ใช่แค่เรา** ไพ่ "9 แต้มไม่มีคู่" ที่แทบชนะเสมอในกติกาพื้นฐาน กลายเป็นแค่มือกลางๆ ในกติกาแจก 6 ทิ้ง 3 เพราะคนกว่าครึ่งโต๊ะจะได้เรียงหรือสีขึ้นไป ตารางเกณฑ์หมอบที่คำนวณจากกติกาหนึ่ง เอาไปใช้กับอีกกติกาหนึ่งจะให้คำแนะนำที่ผิด

**4.3 Equity แบบหลายคน (เฉพาะกติกาแจกพื้นฐาน ตัวอย่างบางมือ)**

ต้นแบบ Monte Carlo แสดงความน่าจะเป็นชนะ/เสมอ ("equity") ของไพ่ตัวอย่างเทียบกับคู่ต่อสู้สุ่ม N คน (N = 2–9) เฉพาะกติกาแจกพื้นฐาน มีกราฟและรายละเอียดเต็มอยู่ในบทสนทนางานวิจัยนี้แล้ว ไม่ขอย่อซ้ำที่นี่ สรุปสั้นๆ: ไพ่กลุ่มแรง (เซียน, เรียง) equity ยังเกิน ~88% แม้เจอ 9 คน ส่วนไพ่กลุ่มแต้มร่วงเร็วตามจำนวนคู่ต่อสู้ที่เพิ่ม และร่วงเร็วกว่าชัดเจนถ้าไม่มีคู่แม้แต้มรวมจะเท่ากัน — ยืนยันว่ากติกาคุมมีน้ำหนักจริงในทางปฏิบัติ ไม่ใช่แค่กฎตัดสินเสมอเฉยๆ

### 6. สิ่งที่ยังค้างอยู่ / ขั้นตอนถัดไป

- [ ] ขยาย simulation equity แบบหลายคน ให้รันแยกตามแต่ละกติกาการแจก (ไม่ใช่แค่ baseline) — ไพ่คู่ต่อสู้ต้องถูกสร้างผ่านกระบวนการทิ้งไพ่แบบเดียวกัน ไม่ใช่สุ่ม 3 ใบตรงๆ เหมือนเดิม
- [ ] สร้างโมเดลกติกาแบบไพ่กองกลาง (2 ใบส่วนตัว + 3 ใบกลาง เลือกดีที่สุด 2+1) — โครงสร้างต่างออกไปเพราะไพ่แต่ละคน**สัมพันธ์กัน**ไม่เป็นอิสระเหมือนกติกาอื่น ต้องมีกรอบคิดแยกต่างหาก
- [ ] แปลงตัวเลข equity เป็นตารางหมอบ/สู้จริง โดยใช้ pot odds กับกองกลาง (40) และช่วงเดิมพัน (20–60) ตามกติกาฐาน
- [ ] เช็คกติกาที่ตั้งสมมติฐานไว้ (โดยเฉพาะลำดับไพ่ และตอง 3 vs ตอง A) กับวงเล่นจริง เพราะตอนสำรวจกติกาเจอความขัดแย้งกันหลายจุด
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