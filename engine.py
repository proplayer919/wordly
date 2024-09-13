import math
from colorama import Fore, Style
import csv
import re

freqs = {}

# Define a regex pattern to match keys that are exactly 5 letters long and contain only alphabetic characters
pattern = re.compile(r'^[a-zA-Z]{5}$')

# Open and read the CSV file
with open("word_frequencies.csv", mode='r', newline='', encoding='utf-8') as file:
    reader = csv.reader(file)
        
    for row in reader:
        # Ensure the row has at least two columns
        if len(row) >= 2:
            key, value = row[0], row[1]
                
            # Apply the filter: only include keys that match the pattern
            if pattern.match(key):
                freqs[key] = value

with open("guesses.txt", "r") as f:
    possible_guesses = [line.strip() for line in f if line.strip()]


def get_answer(guess: str, target: str) -> str:
    result = ["-"] * len(guess)
    target_chars = list(target)
    guess_chars = list(guess)

    for i in range(len(guess)):
        if guess[i] == target[i]:
            result[i] = "g"
            target_chars[i] = None
            guess_chars[i] = None

    for i in range(len(guess)):
        if guess_chars[i] is not None and guess_chars[i] in target_chars:
            result[i] = "y"
            target_chars[target_chars.index(guess_chars[i])] = None

    return "".join(result)


class Game:
    def __init__(self):
        self.not_possible_chars = set()
        self.known_not_words = set()

        self.known = ["*"] * 5
        self.unknown = []

        self.guesses = []
        self.patterns = []

    def get_words_from_pattern(self, patterns: list[str], guesses: list[str]) -> list[str]:
        """
        Gets all words that match the given patterns.

        Args:
            patterns (list[str]): The patterns to match.
            guesses (list[str]): The guesses that made the patterns.

        Returns:
            list[str]: The list of words that match the patterns.
        """
        words = []
        for word in possible_guesses:
            if word not in guesses:
                words.append(word)

        new_words = []
        for word in words:
            allowed = True
            for i, pattern in enumerate(patterns):
                for j, char in enumerate(word):
                    try:
                        if pattern[j] == "-" and char in guesses[i]:
                            allowed = False
                            break
                        elif pattern[j] == "y" and char not in guesses[i]:
                            allowed = False
                            break
                        elif pattern[j] == "g" and word[i] != guesses[i][j]:
                            allowed = False
                            break
                    except IndexError:
                        allowed = False
                        break

            if allowed:
                new_words.append(word)

        return new_words


    def play(self, guess: str, answer: str):
        self.guesses.append(guess)
        self.patterns.append(answer)

        if guess not in self.known_not_words:
            self.known_not_words.add(guess)

        for i, char in enumerate(guess):
            if answer[i] == "-":
                self.not_possible_chars.add(char)
            elif answer[i] == "y":
                obj = {"char": char, "index": i}
                if obj not in self.unknown:
                    self.unknown.append(obj)
            else:
                self.known[i] = char
                self.unknown[:] = [
                    obj for obj in self.unknown if obj["char"] != char or obj["index"] == i
                ]

    def rank_guess(self, guess: str, frequency_multiplier: float = 1.0):
        if not guess or guess in self.known_not_words:
            return -math.inf

        score = 0
        guessed_chars = set()

        for i, char in enumerate(guess):
            if char in guessed_chars:
                score -= 2
            guessed_chars.add(char)

            if char in self.not_possible_chars:
                score -= 5

            if self.known[i] == char:
                score += 1000
                
            if guess in freqs:
                score += float(freqs[guess]) * frequency_multiplier
            else:
                score += 0.075

            score += sum(
                1.0 for obj in self.unknown if obj["char"] == char and obj["index"] != i
            )

        return score

    def best_guess(self):
        best_score = -math.inf
        best_guess = None

        guesses = self.get_words_from_pattern(self.patterns, self.guesses)

        if not guesses:
            guesses = possible_guesses

        if not guesses:
            print(f"{Fore.RED}Ran out of guesses{Style.RESET_ALL}")
            return None

        for guess in guesses:
            score = self.rank_guess(guess)
            if score > best_score:
                best_score = score
                best_guess = guess

        if best_guess is None:
            print(f"{Fore.RED}Ran out of guesses{Style.RESET_ALL}")

        return best_guess

    def get_emoji_rep(self):
        green = "🟩"
        yellow = "🟨"
        grey = "⬛"

        representation = ""
        for i, pattern in enumerate(self.patterns):
            pattern = pattern.replace("g", green).replace("y", yellow).replace("-", grey)
            representation += pattern + "\n"

        return representation

    def get_colorful_rep(self):
        green = Fore.GREEN
        yellow = Fore.YELLOW
        grey = Fore.LIGHTBLACK_EX

        representation = ""
        for i, guess in enumerate(self.guesses):
            pattern = self.patterns[i]
            colorful_guess = ""
            for j, char in enumerate(guess):
                if pattern[j] == "g":
                    colorful_guess += green + char + Style.RESET_ALL
                elif pattern[j] == "y":
                    colorful_guess += yellow + char + Style.RESET_ALL
                else:
                    colorful_guess += grey + char + Style.RESET_ALL
            representation += colorful_guess + "\n"

        return representation

    def get_combined_rep(self):
        colorful_rep = self.get_colorful_rep()
        emoji_rep = self.get_emoji_rep()

        rep = ""

        for i, line in enumerate(emoji_rep.split("\n")):
            rep += line + "  " + colorful_rep.split("\n")[i] + "\n"

        return rep
