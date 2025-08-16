#!/usr/bin/env python3
"""
evaluate.py

A comprehensive word game hand analyzer that calculates the probability of drawing viable hands from a given tile distribution.

Usage:
    python evaluate.py <wordfile> [options]

Arguments:
    wordfile            Path to dictionary file (one word per line)

Options:
    --report_every      How many words to check before updating the progress message (defaults to 10_000; Under 1_000 will display no updates)
    --[j]son            Format output in json format (defaults to false)

Analysis process:
1. Loads word list and converts to letter frequency counters
2. Generates all possible 7-tile hands using backtracking algorithm
3. Checks each hand against word list for valid word formation
4. Accounts for blank tiles (wildcards) as automatic valid hands (all wild hands have a minimum of one valid two letter word available)
5. Calculates both raw counts and weighted probabilities
6. Reports percentage of hands that can form valid words

Output statistics:
- Total unique hand combinations analyzed
- Number of hands that can form valid words
- Number of "dead" hands with no word options
- Weighted analysis accounting for tile frequency distribution

Note: 
- Weighted results reflect probability based on English Scrabble's tile distribution (e.g., 12 E's vs 1 Z makes E-heavy hands more likely).
  For different games and editions LETTER_TILES and HAND_SIZE need to be adjusted accordingly
"""

import argparse, math, sys, time
from collections import Counter
from typing import Dict, List, Union

""" --------- variables --------- """
LETTER_TILES = {
    'A': 9, 'B': 2, 'C': 2, 'D': 4, 'E': 12, 'F': 2,
    'G': 3, 'H': 2, 'I': 9, 'J': 1, 'K': 1, 'L': 4,
    'M': 2, 'N': 6, 'O': 8, 'P': 2, 'Q': 1, 'R': 6,
    'S': 4, 'T': 6, 'U': 4, 'V': 2, 'W': 2, 'X': 1,
    'Y': 2, 'Z': 1, '?': 2, # ? is wild
}

HAND_SIZE = 7
TOTAL_HANDS = math.comb(sum(LETTER_TILES.values()), HAND_SIZE)  # 16_007_560_800 for scrabble

""" --------- helpers ---------- """
def load_word_counters(path: str) -> List[Counter]:
    """Load words from file and return as list of letter counters."""
    with open(path, encoding="utf-8") as f:
        words = [w.strip().upper() for w in f]
    return [Counter(word) for word in words]

def hand_has_word(hand: Counter, word_counters: List[Counter]) -> bool:
    """Check if hand can form any word from the word list."""
    return any(not (word_counter - hand) for word_counter in word_counters)

""" --------- analysis --------- """
def analysis(word_counters: List[Counter], progress_every: int = 10_000) -> dict[str, int]:
    letters = list(LETTER_TILES.items())
    fact = [math.factorial(i) for i in range(HAND_SIZE + 1)]

    stats = dict(valid=0, valid_w=0, dead=0, dead_w=0, total=0)
    hands_seen = 0
    t0 = time.perf_counter()

    def backtrack(idx: int, left: int, cur: Counter, weight: int):
        nonlocal hands_seen
        if left == 0:       # finished a 7 tile hand
            stats['total'] += 1
            hands_seen += 1
            if cur['?'] or hand_has_word(cur, word_counters):
                stats['valid'] += 1
                stats['valid_w'] += weight
            else:
                stats['dead'] += 1
                stats['dead_w'] += weight

            if progress_every > 1_000 and hands_seen % progress_every == 0:
                elapsed = time.perf_counter() - t0
                print(f"\r{hands_seen:,} hands checked | {stats['dead']:,} dead | {elapsed:,.1f}s taken", end='')
            return
            
        if idx == len(letters): # ran out of tile types (need to backtrack to where more available letters are)
            return

        letter, avail = letters[idx]
        for k in range(min(avail, left) + 1):
            # number of ways to pick those k tiles from the available copies
            next_weight = weight * math.comb(avail, k)
            cur[letter] += k
            backtrack(idx + 1, left - k, cur, next_weight)
            cur[letter] -= k

    backtrack(0, HAND_SIZE, Counter(), 1)
    return stats

""" ----------- main ----------- """
def main() -> None:
    parser = argparse.ArgumentParser(description = "Analyze Scrabble hands for valid word formation")
    parser.add_argument("wordfile", help = "Path to file containing word list (one word per line)")
    parser.add_argument('--report_every', type=int, default=10_000, help='how many words to check before updating the progress message (defaults to 10,000; 0 means no updates)')
    parser.add_argument('--json', '-j', action='store_true', help='Output results in json format')
    args = parser.parse_args()
    
    word_counters = load_word_counters(args.wordfile)
    print(f"Loaded {len(word_counters)} valid words", file = sys.stderr)
    
    stats = analysis(word_counters, args.report_every)
    
    if args.json:
        json_output = f'''{{
    "results": {{
        "total_hands": {stats['total']},
        "with_valid": {{
            "count": {stats['valid']},
            "percentage": {100 * stats['valid'] / stats['total']:.4f}
        }},
        "no_options": {{
            "count": {stats['dead']},
            "percentage": {100 * stats['dead'] / stats['total']:.4f}
        }}
    }},
    "weighted": {{
        "total_hands": {TOTAL_HANDS},
        "with_valid": {{
            "count": {stats['valid_w']},
            "percentage": {100 * stats['valid_w'] / TOTAL_HANDS:.4f}
        }},
        "no_options": {{
            "count": {stats['dead_w']},
            "percentage": {100 * stats['dead_w'] / TOTAL_HANDS:.4f}
        }}
    }}
}}'''

        print(json_output)
    else:
        print("\n------- Results --------")
        print(f"Total hands : {stats['total']:,}")
        print(f"With valid  : {stats['valid']:,} {100 * stats['valid'] / stats['total']:8.4f}%")
        print(f"No options  : {stats['dead']:,} {100 * stats['dead'] / stats['total']:8.4f}%")
        print("------- Weighted -------")
        print(f"Total hands : {TOTAL_HANDS:,}")
        print(f"With valid  : {stats['valid_w']:,} {100 * stats['valid_w'] / TOTAL_HANDS:8.4f}%")
        print(f"No options  : {stats['dead_w']:,} {100 * stats['dead_w'] / TOTAL_HANDS:8.4f}%")
        print("------------------------")
        
if __name__ == "__main__":
    main()