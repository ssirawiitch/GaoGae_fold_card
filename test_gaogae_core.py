import math
import unittest
from collections import Counter, defaultdict
from itertools import combinations

from gaogae_core import (
    CATEGORY_NAME,
    best_subset,
    build_deck,
    classify,
    showdown_share,
    simulate_equity,
)
from gaogae_full_winrate import (
    best_strength,
    build_strength_catalog,
    exact_final_strength_counts,
    simulate_variant,
    strength_label,
)


class HandRankingTests(unittest.TestCase):
    def test_category_order(self):
        tong = [('2', 'S'), ('2', 'H'), ('2', 'D')]
        straight_flush = [('Q', 'S'), ('K', 'S'), ('A', 'S')]
        sian = [('J', 'S'), ('Q', 'H'), ('K', 'D')]
        straight = [('10', 'S'), ('J', 'H'), ('Q', 'D')]
        flush = [('A', 'C'), ('9', 'C'), ('4', 'C')]
        points = [('8', 'S'), ('K', 'H'), ('A', 'D')]
        ordered = [tong, straight_flush, sian, straight, flush, points]
        self.assertEqual(
            [classify(hand)[0] for hand in ordered],
            [6, 5, 4, 3, 2, 1],
        )

    def test_aces_are_highest_tong(self):
        aces = [('A', 'S'), ('A', 'H'), ('A', 'D')]
        kings = [('K', 'S'), ('K', 'H'), ('K', 'D')]
        threes = [('3', 'S'), ('3', 'H'), ('3', 'D')]
        self.assertGreater(classify(aces), classify(kings))
        self.assertGreater(classify(kings), classify(threes))

    def test_sian_riang_beats_pair_type_sian(self):
        sian_riang = [('J', 'S'), ('Q', 'H'), ('K', 'D')]
        king_pair = [('J', 'S'), ('K', 'H'), ('K', 'D')]
        self.assertGreater(classify(sian_riang), classify(king_pair))

    def test_control_pair_beats_unpaired_hand_at_equal_points(self):
        pair_nines = [('9', 'S'), ('9', 'H'), ('A', 'D')]
        ace_high = [('8', 'S'), ('K', 'H'), ('A', 'D')]
        self.assertGreater(classify(pair_nines), classify(ace_high))

    def test_pair_aces_are_highest_control_pair(self):
        pair_aces = [('A', 'S'), ('A', 'H'), ('7', 'D')]
        pair_kings = [('K', 'S'), ('K', 'H'), ('9', 'D')]
        self.assertEqual(classify(pair_aces)[1], 9)
        self.assertEqual(classify(pair_kings)[1], 9)
        self.assertGreater(classify(pair_aces), classify(pair_kings))

    def test_pair_kicker_breaks_equal_pair_and_point_tie(self):
        king_kicker = [('9', 'S'), ('9', 'H'), ('K', 'D')]
        queen_kicker = [('9', 'D'), ('9', 'C'), ('Q', 'H')]
        self.assertEqual(classify(king_kicker)[1], classify(queen_kicker)[1])
        self.assertGreater(classify(king_kicker), classify(queen_kicker))

    def test_unpaired_high_cards_break_equal_point_tie(self):
        ace_king_high = [('8', 'S'), ('K', 'H'), ('A', 'D')]
        ace_queen_high = [('8', 'H'), ('Q', 'D'), ('A', 'C')]
        king_high = [('9', 'S'), ('Q', 'H'), ('K', 'D')]
        self.assertEqual(classify(ace_king_high)[1], 9)
        self.assertEqual(classify(ace_queen_high)[1], 9)
        self.assertEqual(classify(king_high)[1], 9)
        self.assertGreater(classify(ace_king_high), classify(ace_queen_high))
        self.assertGreater(classify(ace_queen_high), classify(king_high))

    def test_control_card_suit_breaks_equal_rank_tie(self):
        ace_spade = [('9', 'S'), ('9', 'H'), ('A', 'S')]
        ace_heart = [('9', 'D'), ('9', 'C'), ('A', 'H')]
        ace_diamond = [('9', 'S'), ('9', 'C'), ('A', 'D')]
        ace_club = [('9', 'H'), ('9', 'D'), ('A', 'C')]
        ordered = [ace_spade, ace_heart, ace_diamond, ace_club]
        self.assertEqual([classify(hand)[1] for hand in ordered], [9] * 4)
        self.assertEqual(
            [classify(hand)[-1] for hand in ordered],
            [4, 3, 2, 1],
        )
        for higher, lower in zip(ordered, ordered[1:]):
            self.assertGreater(classify(higher), classify(lower))

    def test_ace_two_three_uses_three_as_suit_control(self):
        three_spade = [('A', 'C'), ('2', 'D'), ('3', 'S')]
        three_heart = [('A', 'D'), ('2', 'C'), ('3', 'H')]
        self.assertGreater(classify(three_spade), classify(three_heart))

    def test_queen_king_ace_uses_ace_as_suit_control(self):
        ace_spade = [('Q', 'H'), ('K', 'D'), ('A', 'S')]
        ace_heart = [('Q', 'D'), ('K', 'C'), ('A', 'H')]
        self.assertGreater(classify(ace_spade), classify(ace_heart))

    def test_sian_uses_king_or_kicker_as_suit_control(self):
        jqk_king_spade = [('J', 'C'), ('Q', 'D'), ('K', 'S')]
        jqk_king_heart = [('J', 'D'), ('Q', 'C'), ('K', 'H')]
        self.assertGreater(classify(jqk_king_spade), classify(jqk_king_heart))

        pair_k_kicker_spade = [('K', 'H'), ('K', 'D'), ('J', 'S')]
        pair_k_kicker_heart = [('K', 'S'), ('K', 'C'), ('J', 'H')]
        self.assertGreater(
            classify(pair_k_kicker_spade),
            classify(pair_k_kicker_heart),
        )

    def test_flush_categories_use_their_control_suit(self):
        straight_flush_spades = [('7', 'S'), ('8', 'S'), ('9', 'S')]
        straight_flush_hearts = [('7', 'H'), ('8', 'H'), ('9', 'H')]
        self.assertGreater(
            classify(straight_flush_spades),
            classify(straight_flush_hearts),
        )

        flush_spades = [('A', 'S'), ('9', 'S'), ('4', 'S')]
        flush_hearts = [('A', 'H'), ('9', 'H'), ('4', 'H')]
        self.assertGreater(classify(flush_spades), classify(flush_hearts))

    def test_unpaired_points_use_highest_card_suit_only(self):
        ace_heart = [('A', 'H'), ('K', 'C'), ('8', 'D')]
        ace_diamond_with_king_spade = [('A', 'D'), ('K', 'S'), ('8', 'C')]
        self.assertGreater(
            classify(ace_heart),
            classify(ace_diamond_with_king_spade),
        )

    def test_rank_priority_precedes_control_suit(self):
        higher_straight_club = [('8', 'H'), ('9', 'D'), ('10', 'C')]
        lower_straight_spade = [('7', 'C'), ('8', 'D'), ('9', 'S')]
        self.assertGreater(
            classify(higher_straight_club),
            classify(lower_straight_spade),
        )

    def test_best_subset_uses_control_suit(self):
        cards = [('9', 'C'), ('9', 'D'), ('A', 'S'), ('A', 'H')]
        expected = classify([('9', 'C'), ('9', 'D'), ('A', 'S')])
        self.assertEqual(best_subset(cards), expected)

    def test_disjoint_physical_hands_never_have_equal_strength(self):
        groups = defaultdict(list)
        deck = build_deck()
        for indexes in combinations(range(len(deck)), 3):
            hand = tuple(deck[index] for index in indexes)
            groups[classify(hand)].append(frozenset(indexes))
        for hands in groups.values():
            for first, second in combinations(hands, 2):
                self.assertFalse(first.isdisjoint(second))

    def test_exact_baseline_category_counts(self):
        counts = Counter(
            CATEGORY_NAME[classify(hand)[0]]
            for hand in combinations(build_deck(), 3)
        )
        self.assertEqual(
            counts,
            {
                'Tong (three of a kind)': 52,
                'Straight flush': 48,
                'Sian (three court cards J/Q/K)': 204,
                'Straight (Riang)': 660,
                'Flush (See)': 1096,
                'Point total (Tam)': 20040,
            },
        )


class EquityTests(unittest.TestCase):
    def test_showdown_share_has_one_winner_for_physical_hands(self):
        mine = classify([('9', 'S'), ('9', 'H'), ('A', 'S')])
        lower_same_ranks = classify([('9', 'D'), ('9', 'C'), ('A', 'H')])
        lower_points = classify([('8', 'S'), ('K', 'H'), ('A', 'D')])
        self.assertEqual(
            showdown_share(mine, [lower_same_ranks, lower_points]),
            ('win', 1.0),
        )

    def test_showdown_share_rejects_equal_comparison_keys(self):
        strength = classify([('9', 'S'), ('9', 'H'), ('A', 'S')])
        with self.assertRaises(ValueError):
            showdown_share(strength, [strength])

    def test_deal_six_caps_at_seven_opponents(self):
        hand = [('3', 'S'), ('3', 'H'), ('3', 'D')]
        results, effective_max = simulate_equity(
            hand,
            opponent_deal_size=6,
            max_opponents=9,
            trials=1,
            seed=1,
        )
        self.assertEqual(effective_max, 7)
        self.assertEqual(max(results), 7)


class FullWinRateTableTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.strengths, cls.details, cls.lookup = build_strength_catalog()

    def test_strength_catalog_has_2925_ordered_rows(self):
        self.assertEqual(len(self.strengths), 2925)
        self.assertEqual(self.strengths, sorted(self.strengths, reverse=True))
        self.assertEqual(strength_label((6, 14)), 'Tong A-A-A')
        self.assertEqual(strength_label((4, 0, 13, 12, 4)),
                         'Sian pair K, kicker Q♠')

    def test_exact_deal_four_reachable_strength_count(self):
        counts = exact_final_strength_counts(4, self.lookup)
        self.assertEqual(len(counts), 2323)
        self.assertEqual(sum(counts.values()), math.comb(52, 4))

    def test_strict_win_rate_never_increases_with_more_players(self):
        samples, win_sums = simulate_variant(
            deal_size=3,
            rounds=100,
            seed=123,
            strength_by_mask=self.lookup,
        )
        for strength, count in samples.items():
            rates = [value / count for value in win_sums[strength]]
            self.assertEqual(rates, sorted(rates, reverse=True))


if __name__ == '__main__':
    unittest.main()
