#!/usr/bin/env python3
"""
word-processor.py

A robust Scrabble word processor that filters and optimizes word lists.

Usage:
    python3 word-processor.py <input_file> <output_file> [options]

Options:
    --include-letter LETTER    Include words with specific letter (default: exclude O)
    --exclude-letter LETTER    Exclude words with specific letter
    --min-length N             Minimum word length (default: 1)
    --max-length N             Maximum word length (default: 7)
    --verbose                  Enable verbose output
    --help                     Show this help message

Processing steps:
1. Filters words by letter inclusion/exclusion rules
2. Converts to canonical form (sorted letters)
3. Removes duplicates
4. Removes canonical supersets (words contained in others)
5. Validates against Scrabble tile constraints
6. Sorts and outputs results
"""

import sys
import argparse
from collections import Counter
from typing import Set, List, Tuple
from pathlib import Path


class ScrabbleProcessor:
    """Processes word lists for Scrabble optimization."""
    
    # English Scrabble tile distribution (excluding blanks)
    TILE_COUNTS = {
        'A':  9, 'B': 2, 'C': 2, 'D': 4, 'E': 12, 'F': 2, 'G': 3,
        'H':  2, 'I': 9, 'J': 1, 'K': 1, 'L': 4, 'M': 2, 'N': 6,
        'O':  8, 'P': 2, 'Q': 1, 'R': 6, 'S': 4, 'T': 6, 'U': 4,
        'V':  2, 'W': 2, 'X': 1, 'Y': 2, 'Z': 1
    }
    
    def __init__(self, exclude_letters: Set[str] = None, include_letters: Set[str] = None,
                 min_length: int = 1, max_length: int = None, verbose: bool = False):
        """Initialize processor with filtering options."""
        self.exclude_letters = exclude_letters or {'O'}
        self.include_letters = include_letters or set()
        self.min_length = min_length
        self.max_length = max_length
        self.verbose = verbose
        
    def is_valid_word(self, word: str) -> bool:
        """Check if word meets length and letter requirements."""
        if len(word) < self.min_length:
            return False
        if self.max_length and len(word) > self.max_length:
            return False
        
        word_upper = word.upper()
        
        # Check exclusion rules
        if any(letter in word_upper for letter in self.exclude_letters):
            return False
            
        # Check inclusion rules (if any specified)
        if self.include_letters and not any(letter in word_upper for letter in self.include_letters):
            return False
            
        return True
    
    def is_scrabble_valid(self, canonical_word: str) -> bool:
        """Check if canonical word can be formed with Scrabble tiles."""
        letter_counts = Counter(canonical_word)
        return all(
            letter_counts[letter] <= self.TILE_COUNTS.get(letter, 0)
            for letter in letter_counts
        )
    
    def extract_words(self, file_path: str) -> Set[str]:
        """Extract and canonicalize words from input file."""
        canonical_words = set()
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                for line_num, line in enumerate(f, 1):
                    if not line.strip():
                        continue
                        
                    # Extract first word from line (handles various formats)
                    word = line.split()[0].strip().upper()
                    
                    if not word.isalpha():
                        if self.verbose:
                            print(f"Skipping non-alphabetic word at line {line_num}: {word}")
                        continue
                    
                    if self.is_valid_word(word):
                        canonical_form = ''.join(sorted(word))
                        canonical_words.add(canonical_form)
                        
        except FileNotFoundError:
            print(f"Error: Input file '{file_path}' not found", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"Error reading file: {e}", file=sys.stderr)
            sys.exit(1)
            
        return canonical_words
    
    def remove_supersets(self, canonical_words: List[str]) -> List[str]:
        """Remove words that are supersets of other words."""
        # Sort by length for efficient superset checking
        sorted_words = sorted(canonical_words, key=len)
        counters = [Counter(word) for word in sorted_words]
        filtered_words = []
        
        for i, (word, word_counter) in enumerate(zip(sorted_words, counters)):
            is_superset = False
            
            # Check if current word is a superset of any previous word
            for j in range(i):
                other_counter = counters[j]
                if all(word_counter[letter] >= count for letter, count in other_counter.items()):
                    is_superset = True
                    break
            
            if not is_superset and self.is_scrabble_valid(word):
                filtered_words.append(word)
                
        return filtered_words
    
    def process_file(self, input_file: str, output_file: str) -> Tuple[int, int, int]:
        """Process input file and write results to output file."""
        if self.verbose:
            print(f"Processing '{input_file}'...")
            
        # Extract and canonicalize words
        canonical_words = self.extract_words(input_file)
        
        if self.verbose:
            print(f"Found {len(canonical_words)} unique canonical forms")
            
        # Remove supersets and apply Scrabble validation
        filtered_words = self.remove_supersets(list(canonical_words))
        
        # Write output
        try:
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(sorted(filtered_words)) + '\n')
                
        except Exception as e:
            print(f"Error writing output file: {e}", file=sys.stderr)
            sys.exit(1)
            
        return len(canonical_words), len(filtered_words), len(canonical_words) - len(filtered_words)


def create_parser() -> argparse.ArgumentParser:
    """Create command line argument parser."""
    parser = argparse.ArgumentParser(
        description="Process word lists for Scrabble optimization",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Basic usage (excludes words with 'O')
    python3 word-processor.py words.txt output.txt
    
    # Include words with 'Q' instead of excluding 'O'
    python3 word-processor.py words.txt output.txt --include-letter Q
    
    # Exclude multiple letters
    python3 word-processor.py words.txt output.txt --exclude-letter O --exclude-letter Z
    
    # Filter by length
    python3 word-processor.py words.txt output.txt --min-length 3 --max-length 7
        """
    )
    
    parser.add_argument('input_file', help='Input word list file')
    parser.add_argument('output_file', help='Output file for processed words')
    parser.add_argument('--include-letter', action='append', dest='include_letters',
                       help='Include only words containing this letter (can be used multiple times)')
    parser.add_argument('--exclude-letter', action='append', dest='exclude_letters',
                       help='Exclude words containing this letter (can be used multiple times)')
    parser.add_argument('--min-length', type=int, default=1,
                       help='Minimum word length (default: 1)')
    parser.add_argument('--max-length', type=int, default=7,
                       help='Maximum word length (default: 7)')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose output')
    
    return parser


def main():
    """Main entry point."""
    parser = create_parser()
    args = parser.parse_args()
    
    # Handle default behavior (exclude 'O' if no other filters specified)
    exclude_letters = set()
    if args.exclude_letters:
        exclude_letters = {letter.upper() for letter in args.exclude_letters}
    elif not args.include_letters:
        exclude_letters = {'O'}  # Default behavior
    
    include_letters = set()
    if args.include_letters:
        include_letters = {letter.upper() for letter in args.include_letters}
    
    # Create processor
    processor = ScrabbleProcessor(
        exclude_letters=exclude_letters,
        include_letters=include_letters,
        min_length=args.min_length,
        max_length=args.max_length,
        verbose=args.verbose
    )
    
    # Process file
    total_words, kept_words, removed_words = processor.process_file(
        args.input_file, args.output_file
    )
    
    # Print summary
    print(f"Processing complete:")
    print(f"  Input: {total_words} unique canonical forms")
    print(f"  Output: {kept_words} Scrabble-valid, non-superset words")
    print(f"  Removed: {removed_words} words ({removed_words/total_words*100:.1f}%)")
    print(f"  Results written to '{args.output_file}'")


if __name__ == "__main__":
    main()