#!/usr/bin/env python3
"""
boggle-evaluator.py
A comprehensive Boggle grid evaluator that finds optimal grids for maximum scoring.

Usage:
    python boggle-evaluator.py <wordfile> [options]

Arguments:
    wordfile                   Path to word list file (one word per line)

Options:
    --[s]ize SIZE           Select the boggle variant to test: standard, big (default: standard) 
    --[i]terations N        Number of optimization iterations (default: 10,000)
    --[m]ethod METHOD       Optimization method: random, hillclimb, both (default: both)
    --[v]erbose             Enable verbose output
    --seed N                Random seed for reproducible results

Processing steps:
1. Loads word list
2. Generates or optimizes Boggle grids using specified method
3. Evaluates grids by finding all valid words using DFS traversal
4. Scores words using standard Boggle point system
5. Reports best grid configuration and achievable score

Optimization methods:
- Random search: Generates many random grids and selects the best
- Hill climbing: Iteratively improves grids through local letter substitutions
- Both: Runs random search first, then hill climbing from best result

Scoring system (standard Boggle):
- 3-4 letters: 1 point
- 5 letters: 2 points
- 6 letters: 3 points
- 7 letters: 5 points
- 8+ letters: 11 points
"""

import argparse, random, itertools
from collections import defaultdict, deque
from typing import List, Set, Tuple, Dict

class BoggleEvaluator:
    def __init__(self, word_list: List[str], arg_size: str, verbose: bool = False):
        self.size = 5 if arg_size == 'big' else 4
        self.verbose = verbose
        self.word_set = set(word_list)
        self.word_trie = self.make_trie(word_list)
        
        # Standard Boggle scoring (words must be 3+ letters, 8+ letters score 11 points)
        self.scoring = {
            3: 1, 4: 1, 5: 2, 6: 3, 7: 5, 8: 11
        }
        
        # Official Boggle dice sets (post 1987)
        self.dice = [
            'AAAFRS', 'AAEEEE', 'AAFIRS', 'ADENNN', 'AEEEEM',
            'AEEGMU', 'AEGMNN', 'AFIRSY', 'BJKQXZ', 'CCENST',
            'CEIILT', 'CEILPT', 'CEIPST', 'DDHNOT', 'DHHLOR',
            'DHLNOR', 'EIIITT', 'EMOTTT', 'ENSSSU', 'FIPRSY',
            'GORRVW', 'HIPRRY', 'NOOTUW', 'OOOTTU', 'AAEEEE'
        ] if arg_size == 'big' else [
            'AAEEGN', 'ABBJOO', 'ACHOPS', 'AFFKPS',
            'AOOTTW', 'CIMOTU', 'DEILRX', 'DELRVY',
            'DISTTY', 'EEGHNW', 'EEINSU', 'EHRTVW',
            'EIOSST', 'ELRTTY', 'HIMNUQ', 'HLNNRZ'
        ]
        
    def get_neighbors(self, row: int, col: int) -> List[Tuple[int, int]]:
        """Get all valid neighboring positions (including diagonals)"""
        neighbors = []
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                nr, nc = row + dr, col + dc
                if (dr == 0 and dc == 0) or not (0 <= nr < self.size) or not (0 <= nc < self.size):
                    continue
                neighbors.append((nr, nc))
        return neighbors

    def dfs(self, grid: List[List[str]], row: int, col: int, path: str, found_words: Dict[str, int] = {}) -> Dict[str, int]:
        # Bail if we've got no hope of a word
        if not self.in_trie(path):
            return found_words

        # Check if current path is a valid word
        if len(path) >= 3 and path in self.word_set:
            if path not in found_words:
                found_words[path] = self.scoring.get(len(path), 11)
        
        # Explore neighbors
        neighbors = self.get_neighbors(row, col)
        for nr, nc in self.get_neighbors(row, col):
            new_path = path + grid[nr][nc]
            found_words = self.dfs(grid, nr, nc, new_path, found_words)
        
        return found_words
    
    def find_words_in_grid(self, grid: List[List[str]]) -> Dict[str, int]:
        """Find all valid words in the grid using DFS"""
        found_words = {}
        
        # Start DFS from each position
        for i in range(self.size):
            for j in range(self.size):
                self.dfs(grid, i, j, grid[i][j], found_words)
        
        return found_words
    
    def calculate_grid_score(self, grid: List[List[str]]) -> Tuple[int, Dict[str, int]]:
        """Calculate total score for a grid"""
        found_words = self.find_words_in_grid(grid)
        total_score = sum(found_words.values())
        return total_score, found_words
    
    def generate_random_grid(self, verbose: bool = False) -> Tuple[List[List[str]], List[str]]:
        """Generate a random Boggle grid using dice with fixed faces"""
        dice = self.dice[:]
        random.shuffle(dice)

        letters = [random.choice(die) for die in dice]
        grid = [
            letters[i * self.size:(i + 1) * self.size]
            for i in range(self.size)
        ]

        return grid, dice
    
    def optimize_grid_random_search(self, iterations: int = 1000) -> Tuple[List[List[str]], List[str], int, Dict[str, int]]:
        """Find optimal grid using random search"""
        best_grid = None
        best_dice = self.dice
        best_score = 0
        best_words = {}
        
        for i in range(iterations):
            grid, best_dice = self.generate_random_grid()
            score, words = self.calculate_grid_score(grid)
            
            if score > best_score:
                best_score = score
                best_grid = [row[:] for row in grid]
                best_words = words.copy()
                
            if (self.verbose and i + 1) % 100 == 0:
                print(f'Iteration {i + 1}/{iterations}, Best score so far: {best_score}')
        
        return best_grid, best_dice, best_score, best_words
    
    def optimize_grid_hill_climbing(self, initial_grid: List[List[str]] = None, initial_dice: List[str] = None, iterations: int = 10_000) -> Tuple[List[List[str]], int, Dict[str, int]]:
        """Optimize grid using hill climbing (local search)"""
        if initial_grid is None:
            current_grid, current_dice = self.generate_random_grid()
        else:
            current_grid = [row[:] for row in initial_grid]
            current_dice = initial_dice
        
        current_score, current_words = self.calculate_grid_score(current_grid)
        best_grid = [row[:] for row in current_grid]
        best_score = current_score
        best_words = current_words.copy()
                
        for iteration in range(iterations):
            # Try to improve the grid a bit
            improved = False
            
            for i in range(self.size):
                for j in range(self.size):
                    original_letter = current_grid[i][j]
                    
                    # Reroll some dice
                    for _ in range(5):
                        new_letter = random.choice(current_dice[i + (j * self.size)])
                        if new_letter != original_letter:
                            current_grid[i][j] = new_letter
                            score, words = self.calculate_grid_score(current_grid)
                            
                            if score > current_score:
                                current_score = score
                                current_words = words
                                improved = True
                                
                                if score > best_score:
                                    best_score = score
                                    best_grid = [row[:] for row in current_grid]
                                    best_words = words.copy()
                                break

                    if not improved:
                        current_grid[i][j] = original_letter
            
            if (iteration + 1) % 500 == 0:
                if (self.verbose):
                    if (iteration + 1) > 500:
                        print(f'\033[13F')
                    self.print_grid(current_grid)
                    print(f'Iteration {iteration + 1}/{iterations}, Best score: {best_score}, Current: {current_score}')
                if (iteration + 1) % 1000 == 0: # Mix things up a bit and try starting from a different grid
                    current_grid, current_dice = self.generate_random_grid()
        
        return best_grid, best_score, best_words
    
    def print_grid(self, grid: List[List[str]]):
        """Pretty print a grid"""
        print('+' + '-' * (self.size * 4 - 1) + '+')
        for row in grid:
            print('| ' + ' | '.join(row) + ' |')
            print('+' + '-' * (self.size * 4 - 1) + '+')
    
    def print_results(self, grid: List[List[str]], score: int, words: Dict[str, int]):
        """Print evaluation results"""
        print(f'Grid Score: {score}')
        print(f'Words Found: {len(words)}')
        if (grid is not None):
            print(f'Grid:')
            self.print_grid(grid)

        if(score > 0):
            print(f'Found Words (sorted by score):')
            sorted_words = sorted(words.items(), key=lambda x: (-x[1], x[0]))
            for word, word_score in sorted_words:
                print(f'  {word}: {word_score} points')

    # Make a basic trie out of the word list
    def make_trie(self, words: List[str]) -> dict:
        trie = dict()
        for word in words:
            step = trie
            for letter in word:
                step = step.setdefault(letter, {})
            step['_end_'] = '_end_'
        return trie

    # Check the trie for a given path
    def in_trie(self, path) -> bool:
        current_dict = self.word_trie
        for letter in path:
            if letter not in current_dict:
                return False
            current_dict = current_dict[letter]
        return True

# Load the word list out of a file
def load_word_list(filename: str) -> List[str]:
    """Load word list from file"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return [line.strip().upper() for line in f if line.strip()]
    except FileNotFoundError:
        print(f'Error: Word list file <{filename}> not found', file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f'Error reading word list file: {e}', file=sys.stderr)
        sys.exit(1)

""" ----------- main ----------- """
def main() -> None:
    parser = argparse.ArgumentParser(
        description='Boggle grid evaluator that finds optimal grids for maximum scoring',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python boggle-evaluator.py words.txt
  python boggle-evaluator.py words.txt --size big --iterations 500 --method hillclimb
  python boggle-evaluator.py words.txt --verbose --seed 42
        """
    )
    
    parser.add_argument('wordfile', help='Word list file (one word per line)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose output')
    parser.add_argument('--size', '-s', choices=['standard', 'big'], default='standard', help='boggle size (default: standard)')
    parser.add_argument('--iterations', '-i', type=int, default=10_000, help='Number of optimization iterations (default: 10,000)')
    parser.add_argument('--method', '-m', choices=['random', 'hillclimb', 'both'], default='both', help='Optimization method (default: both)')
    parser.add_argument('--seed', type=int, help='Random seed for reproducible results')
    
    args = parser.parse_args()
    
    # Set random seed if provided
    if args.seed:
        random.seed(args.seed)
    
    # Load word list
    words = load_word_list(args.wordfile)
    
    # Initialize evaluator
    evaluator = BoggleEvaluator(words, args.size, verbose=args.verbose)
    
    # Print header if not verbose mode
    if args.verbose:
        if args.size == 'big':
            print(f'Grid size: 5x5')
        else:
            print(f'Grid size: 4x4')
        print(f'Word list: {len(words)} words')
        print(f'Method: {args.method}')
        print(f'Iterations: {args.iterations}')
        if args.seed:
            print(f'Random seed: {args.seed}')
    
    best_grid = None
    best_score = 0
    best_words = {}
    best_method = ''
    
    # Run optimization based on method
    if args.method in ['random', 'both']:
        if args.verbose:
            print(f'\nRunning random search optimization ({args.iterations} iterations)...')
        
        grid, dice, score, words_found = evaluator.optimize_grid_random_search(iterations=args.iterations)
        
        if score > best_score:
            best_grid, best_score, best_words, best_method = grid, score, words_found, 'random_search'
        
        if args.verbose:
            print(f'\nRandom search result:')
            evaluator.print_results(grid, score, words_found)
    
    if args.method in ['hillclimb', 'both']:
        if args.verbose:
            print(f'\nRunning hill climbing optimization ({args.iterations} iterations)...')
        
        # Use best random grid as starting point if available
        initial_grid = best_grid if args.method == 'both' else None
        initial_dice = best_dice if args.method == 'both' else None

        grid, score, words_found = evaluator.optimize_grid_hill_climbing(
            initial_grid=initial_grid,
            initial_dice=initial_dice,
            iterations=args.iterations
        )
        
        if score > best_score:
            best_grid, best_score, best_words, best_method = grid, score, words_found, 'hill_climbing'
        
        evaluator.print_results(grid, score, words_found)
    
    # Output final result
    if args.verbose:
        print(f'Best method: {best_method}')
    evaluator.print_results(best_grid, best_score, best_words)

if __name__ == '__main__':
    main()