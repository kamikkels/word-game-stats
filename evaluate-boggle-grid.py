#!/usr/bin/env python3
"""
boggle-evaluator.py
A Boggle grid evaluator that finds optimal grids for maximum scoring using a genetic algorithm approach to try finding the best arrangement of dice.

Usage:
    python boggle-evaluator.py <wordfile> [options]

Arguments:
    wordfile                   Path to word list file (one word per line)

Options:
    --[s]ize SIZE           Select the boggle variant to test: standard, big (default: standard) 
    --[g]enerations N       Number of optimization generations to process (default: 1,000)
    --[p]opulation N        The population size for each generation (default: 50)
    --[v]erbose             Enable verbose output
    --seed N                Random seed for reproducible results

Processing steps:
1. Loads word list
2. Generates and optimizes Boggle grids
3. Evaluates grids by finding all valid words using DFS traversal
4. Scores words using standard Boggle point system
5. Repeat 2-4 for N generations
5. Reports best grid configuration and achievable score

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

    def mutate_grid(self, grid, dice) -> Tuple[List[List[str]], List[str]]:
        """Create a mutated version of the grid"""
        new_grid = grid.copy()
        new_dice = dice.copy()
        size=self.size
        
        mutation_type = random.choice(['swap', 'reroll', 'swap_and_reroll'])
        
        if mutation_type == 'swap':
            i1, j1 = random.sample(range(size-1), 2)
            i2, j2 = random.sample(range(size-1), 2)
            new_grid[i1][j1], new_grid[i2][j2] = new_grid[i2][j2], new_grid[i1][j1]
            new_dice[i1*size+j1], new_dice[i2*size+j2] = new_dice[i2*size+j2], new_dice[i1*size+j1]

        elif mutation_type == 'reroll':
            i1, j1 = random.sample(range(size-1), 2)
            new_grid[i1][j1] = random.choice(new_dice[i1*size+j1])
        
        elif mutation_type == 'swap_and_reroll':
            i1, j1 = random.sample(range(size-1), 2)
            i2, j2 = random.sample(range(size-1), 2)
            new_grid[i1][j1] = random.choice(new_dice[i1*size+j1])
            new_grid[i1][j1], new_grid[i2][j2] = new_grid[i2][j2], new_grid[i1][j1]
            new_dice[i1*size+j1], new_dice[i2*size+j2] = new_dice[i2*size+j2], new_dice[i1*size+j1]
        
        return new_grid, new_dice
    
    def optimize_grid(self, generations=1000, population_size=50):
        """Use genetic algorithm to find optimal grid"""
        # Initialize population with random samples
        population = []
        for _ in range(population_size):
            population.append(self.generate_random_grid())
        
        best_grid = None
        best_score = -1
        best_words = []
        
        for generation in range(generations):
            # Score the grids
            scored_population = []
            for grid, dice in population:
                score, formed_words = self.calculate_grid_score(grid)
                scored_population.append((score, grid, dice, formed_words))
            
            # Sort by score
            scored_population.sort(reverse=True)
            
            # Update best
            if scored_population[0][0] > best_score:
                best_score = scored_population[0][0]
                best_grid = scored_population[0][1].copy()
                best_words = scored_population[0][3].copy()
                print(f"Generation {generation}: New best score {best_score}, formed {len(best_words)} words")
                if(self.verbose):
                    print(f'Best grid:')
                    self.print_grid(best_grid)
            
            ### Create next generation ###
            survivors = [(grid, dice) for _, grid, dice, _ in scored_population[:population_size//4]]
            new_population = survivors.copy()
            
            while len(new_population) < population_size:
                if random.random() < 0.3:  # 30% random
                    new_population.append(self.generate_random_grid())
                else:  # 70% mutations
                    (parent_grid, parent_dice) = random.choice(survivors)
                    child = self.mutate_grid(parent_grid, parent_dice)
                    new_population.append(child)
            
            population = new_population
        
        return best_grid, best_score, best_words    

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
        for nr, nc in neighbors:
            new_path = path + grid[nr][nc]
            found_words = self.dfs(grid, nr, nc, new_path, found_words)
        
        return found_words
    
    def find_words_in_grid(self, grid: List[List[str]]) -> Dict[str, int]:
        """Find all valid words in the grid using DFS"""
        found_words = {}
        
        # DFS from each position
        for i in range(self.size):
            for j in range(self.size):
                self.dfs(grid, i, j, grid[i][j], found_words)
        
        return found_words
    
    def calculate_grid_score(self, grid: List[List[str]]) -> Tuple[int, Dict[str, int]]:
        """Calculate total score for a grid"""
        found_words = self.find_words_in_grid(grid)
        total_score = sum(found_words.values())
        return total_score, found_words

    def print_grid(self, grid: List[str]):
        """Pretty print a grid"""
        print('+' + '-' * (self.size*2 + 1) + '+')
        for i in range(self.size):
            print('| ' + ' '.join(grid[i]) + ' |')
        print('+' + '-' * (self.size*2 + 1) + '+')
    
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

    def make_trie(self, words: List[str]) -> dict:
        """Make a basic trie out of the word list"""
        trie = dict()
        for word in words:
            step = trie
            for letter in word:
                step = step.setdefault(letter, {})
            step['_end_'] = '_end_'
        return trie

    def in_trie(self, path) -> bool:
        """Check the trie for a given path"""
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
  python boggle-evaluator.py words.txt --size big --generations 500 --population 75
  python boggle-evaluator.py words.txt --verbose --seed 42
        """
    )
    
    parser.add_argument('wordfile', help='Word list file (one word per line)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose output')
    parser.add_argument('--size', '-s', choices=['standard', 'big'], default='standard', help='boggle size (default: standard)')
    parser.add_argument('--generations', '-g', type=int, default=1_000, help='Number of optimization generations to process (default: 1,000)')
    parser.add_argument('--population', '-p', type=int, default=50, help='The population size for each generation (default: 50)')
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
        print(f'Generations: {args.generations}')
        print(f'Population: {args.population}')
        if args.seed:
            print(f'Random seed: {args.seed}')
    
    best_grid = None
    best_score = 0
    best_words = {}
    best_method = ''
    
    # Find optimal grid
    best_grid, best_score, best_words = evaluator.optimize_grid(
        generations=args.generations,
        population_size=args.population
    )
        
    evaluator.print_results(best_grid, best_score, best_words)

if __name__ == '__main__':
    main()