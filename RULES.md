# Gao Gae Working Rules

> **Status: research draft — not a final house ruleset.**
>
> This document records the rules currently used or proposed for this
> project. Gao Gae is a folk game with substantial house-rule variation.
> The dealing method, betting details, and treatment of an exact tie are
> still being evaluated and must be agreed before play.

## 1. Game overview

- Use one standard 52-card deck without jokers.
- There is no fixed banker. Players compete directly for a common pot.
- Each player finishes with a three-card hand.
- Players may bet or fold during the hand.
- A player wins the pot either by making every other player fold or by
  showing the highest-ranked hand at showdown.
- There are no Pok Deng-style hand multipliers. The winner claims the pot.

The ante, minimum and maximum bet, betting order, permitted actions, and
number of raises have not yet been fixed for this research ruleset.

## 2. Dealing methods under evaluation

No single dealing method has been selected as the official method. The
project currently intends to compare all four variants below. Every player
at a table must use the same variant during a hand.

### Variant A — staged deal (2 + 1)

1. Deal two private cards to every player.
2. Conduct a betting round.
3. Deal one additional private card to every remaining player.
4. Conduct a final betting round.
5. The remaining players proceed to showdown with their three cards.

### Variant B — deal 4, discard 1

1. Deal four private cards to every player.
2. Each player discards exactly one card and keeps three.
3. The discarded card is out of play and cannot be dealt to another player
   during that hand.
4. The timing of discarding relative to the betting round or rounds is not
   yet fixed.

### Variant C — deal 5, discard 2

1. Deal five private cards to every player.
2. Each player discards exactly two cards and keeps three.
3. The discarded cards are out of play and cannot be dealt to another
   player during that hand.
4. The timing of discarding relative to the betting round or rounds is not
   yet fixed.

With one 52-card deck and no community cards, this variant can accommodate
at most ten players in total.

### Variant D — deal 6, discard 3

1. Deal six private cards to every player.
2. Each player discards exactly three cards and keeps three.
3. The discarded cards are out of play and cannot be dealt to another
   player during that hand.
4. The timing of discarding relative to the betting round or rounds is not
   yet fixed.

With one 52-card deck and no community cards, this variant can accommodate
at most eight players in total (one player plus at most seven opponents).

## 3. Card rank

For comparisons outside a straight, cards rank:

**A > K > Q > J > 10 > 9 > 8 > 7 > 6 > 5 > 4 > 3 > 2**

An Ace is high when comparing individual cards, pairs, and three of a kind.
For point calculation only, an Ace is worth one point.

Suits have no rank.

## 4. Hand ranking

Hands rank from highest to lowest as follows:

1. **Three of a Kind (Tong)**
2. **Straight Flush**
3. **Sian**
4. **Straight (Riang)**
5. **Flush (See)**
6. **Points (Taem)**

A hand is assigned to the highest category it qualifies for.

**Always determine the hand category before calculating points.** Points
are never used to compare Three of a Kind, Straight Flush, Sian, Straight,
or Flush hands. Any hand in a higher category beats every hand in a lower
category, regardless of either hand's point total.

### 4.1 Three of a Kind (Tong)

Three cards of the same rank, for example `9-9-9`.

Compare the rank of the three cards. **A-A-A is the highest possible Three
of a Kind**, followed by K-K-K, Q-Q-Q, and so on down to 2-2-2.

### 4.2 Straight Flush

Three consecutive cards of the same suit.

The allowed sequences are:

`A-2-3`, `2-3-4`, ..., `10-J-Q`, `J-Q-K`, `Q-K-A`

`A-2-3` is the lowest sequence and `Q-K-A` is the highest. Compare Straight
Flushes by their sequence. Suits do not break a tie.

### 4.3 Sian

Any three face cards made only from J, Q, and K; ranks may repeat. The hand
must not already qualify as Three of a Kind or a Straight Flush.

- A non-flush `J-Q-K`, called **Sian Riang**, is the highest Sian hand. It
  beats every pair-type Sian hand, including `J-K-K`.
- Other Sian hands contain a pair, such as `K-K-Q` or `Q-Q-J`.
- Among pair-type Sian hands, compare the pair first and then the remaining
  card. For example, `K-K-J` beats `Q-Q-K`, and `K-K-Q` beats `K-K-J`.

A suited `J-Q-K` is a Straight Flush, not Sian. `J-J-J`, `Q-Q-Q`, and
`K-K-K` are Three of a Kind.

### 4.4 Straight (Riang)

Three consecutive cards that are not all of the same suit.

The allowed sequences and their order are the same as for a Straight Flush:
`A-2-3` is lowest and `Q-K-A` is highest. Suits do not break a tie.

A non-flush `J-Q-K` is classified as Sian Riang rather than a regular
Straight.

### 4.5 Flush (See)

Three cards of the same suit that do not form a Straight Flush.

Compare the cards from highest to lowest. If the highest cards tie, compare
the second-highest cards, followed by the third-highest cards. Suits do not
break a tie.

### 4.6 Points (Taem)

Only a hand that does not qualify for any of the five higher categories is a
Points hand. Point totals do not affect the ranking of a combination hand.

Card values for calculating points are:

- A = 1 point
- 2 through 9 = face value
- 10, J, Q, and K = 0 points

Add the three card values and keep only the final digit (modulo 10). Point
totals therefore range from 0 to 9, with 9 being the highest.

Examples:

- `8-K-A` = 8 + 0 + 1 = **9 points**
- `9-9-A` = 9 + 9 + 1 = 19 = **9 points**
- `5-Q-K` = **5 points**
- `10-J-K` = **0 points**

## 5. The control-card tiebreak for Points hands

This section applies only to Points hands. First compare their point totals.
Apply the control-card tiebreak only when two or more Points hands have the
same point total; it is not used to reorder the five higher hand categories.

1. A hand containing a pair beats a hand without a pair.
2. If both hands contain a pair, compare the rank of the pair using
   `A > K > Q > J > 10 > ... > 2`. A pair of Aces is the highest control
   pair. If the pairs have the same rank, compare the remaining card.
3. If neither hand contains a pair, sort each hand by card rank from highest
   to lowest and compare the cards in order: highest card, then second-highest
   card, then third-highest card.
4. Suits do not break a tie.

For example, `9-9-A` beats `8-K-A`: both hands have 9 points, but the pair of
Nines is a control pair and any control pair beats an unpaired hand.

The method for resolving an exact tie after all three card ranks have been
compared — such as splitting the pot or carrying it forward — has not yet
been fixed for live play. Until that house rule is finalized, the research
simulation calculates equity by splitting the pot equally among all tied
winners.

## 6. Items still to be agreed

- Which of the four dealing methods will be the main ruleset, if any.
- When players discard in the deal-4, deal-5, and deal-6 variants.
- The ante, betting limits, betting order, and allowed betting actions.
- Whether an exact tie splits the pot or uses another house procedure.
- The minimum and maximum number of players for normal play.

