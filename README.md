# Word Game Stats
A collection of scripts for evaluating game states in different word games 

## Tile Game Hand Analyzer
This Python script analyzes all possible opening hands in a tile based word game (e.g. Scrabble) to determine how many can form valid words using a given word list. 
It performs a full combinatorial sweep of hands based on official tile distributions and reports both raw and weighted statistics.

### Features 
Exhaustive analysis of possible opening hands.
Determines which hands can form at least one valid word.
Supports wildcard tiles (?) and weighted probability calculations.

### Usage 
1. Prepare a word list
Create a plain text file with each word on a new line

Example:

> apple - a fruit
> zebra
> quiz
> house - a building
> sea
> pant
> pants - plural of pant

2. Minimise the word list
note: capitalisation, and characters after a space will be removed
```
python wordprocessor.py <base-wordlist.txt> <minimal-wordlist.txt>
```

3. Run the evaluator
```
python evaluate-hands.py <wordlist.txt>
```

4. Output
The script prints:

Total number of hands analyzed
Number and percentage of hands that can form valid words
Weighted statistics based on tile probabilities

When a new dictionary is added, or existing one is updated a github action has been setup to process it and commit the output into the output dir.

#### Example output 

```
Loaded 173 valid words
3,190,000 hands checked | 251,021 dead | 623.4s taken
------- Results --------
Total hands : 3,199,724
With valid  : 2,948,703  92.1549%
No options  : 251,021   7.8451%
------- Weighted -------
Total hands : 16,007,560,800
With valid  : 15,915,965,384  99.4278%
No options  : 91,595,416   0.5722%
------------------------
```

### How It Works 
Uses backtracking to generate all combinations of 7 tiles.
Checks each hand against a preloaded list of valid words.
Wildcards (?) are treated as flexible tiles.
Computes both raw counts and weighted probabilities using combinatorics to cover all possible starting hands.

## Boggle maximal point grid
Finds grids that provide a maximum score for a given word list

# Contributing
We welcome contributions! Here's how you can help:

## Adding Dictionaries for Tile Games (No coding required!)
To add a new dictionary file:

1. Click the "Fork" button at the top of this repository
2. Navigate to the dictionaries/ folder in your fork
3. Click "Add file" -> "Create new file"
4. Name your file (for consistency please use the format [Dictionary][Year].txt)
5. Add your dictionary content (one word, or word + definition per line)
6. Scroll down and click "Commit new file"
7. Go back to the main page of your fork and click "Contribute" -> "Open pull request"

## Code Contributions

1. Fork the repository
2. Create a branch
3. Make your changes
4. Submit a pull request with an explanation of what the changes do

## Reporting Issues
Found a bug? Open an issue with:

1. What you expected
2. What actually happened
3. Steps to reproduce

# License 
See LICENSE