# Wordly

Wordly is a wordle solver using UWIv2 (Universal Wordle Interface) to communicate between Wordly and its interface.

**Current WSE rating: approx. ``3.85`` (exact in 'wse.txt' file).**

## Answer format (PWN - Portable Wordle Notation)

The answer format is 'g' for a green letter (correct letter in correct position), 'y' for a yellow letter (correct letter in wrong position), and '-' for a grey letter (incorrect letter).

For example, if the answer is 'ggggg', the guess is perfect. If the answer is 'y--y-', the guess is partially correct. If the answer is '-----', the guess is incorrect.
