import math
from colorama import Fore, Style
import csv
import re
import traceback
import concurrent.futures

freqs = {}

# Define a regex pattern to match keys that are exactly 5 letters long and contain only alphabetic characters
pattern = re.compile(r"^[a-zA-Z]{5}$")

# Open and read the CSV file
with open("word_frequencies.csv", mode="r", newline="", encoding="utf-8") as file:
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
        self.starting_word = "salet"

        self.not_possible_chars = set()
        self.known_not_words = set()

        self.known = ["*"] * 5
        self.unknown = []

        self.guesses = []
        self.patterns = []

        self.entropy_cache = {}

        self.use_info_gain = True

    def clean(self):
        self.known = ["*"] * 5
        self.unknown = []
        self.guesses = []
        self.patterns = []
        self.not_possible_chars = set()
        self.known_not_words = set()
        self.entropy_cache = {}

    def decode_pwn(self, pwn: str) -> tuple[list[str], list[str]]:
        """
        Decodes the given PWN (Portable Wordle Notation) string.

        Args:
            pwn (str): The PWN (Portable Wordle Notation) string to decode.

        Returns:
            tuple[list[str], list[str]]: A tuple containing the decoded patterns and guesses.
        """
        chunks = pwn.split("/")
        guesses = []
        patterns = []
        for chunk in chunks:
            if chunk == "":
                continue
            guesses.append(chunk[:5])
            patterns.append(chunk[5:])
        return patterns, guesses

    def uwi_cmd(self, cmd: str) -> str:
        """
        Executes the given UWI (Universal Wordle Interface) command.

        Args:
            cmd (str): The command to execute.

        Returns:
            str: The output of the command.
        """
        print(f"{Fore.CYAN}Received UWI command: {cmd}{Style.RESET_ALL}")  # For debug

        if cmd == "uwi":
            return "uwi2ok"
        elif cmd.startswith("pos "):
            try:
                position = cmd[4:]
                if position == "blank":
                    return "posok"
                else:
                    position = self.decode_pwn(position)
                    self.play_all(position[1], position[0])
                    return "posok"
            except Exception as e:
                with open("error.log", "w") as f:
                    f.write(traceback.format_exc())
                print(
                    f"{Fore.RED}Error while executing UWI command {cmd}. Check 'error.log' for details.{Style.RESET_ALL}"
                )
                return "poserror"
        elif cmd == "guess":
            return "guessok\n" + self.best_guess() or "guesserror"
        elif cmd.startswith("pwn "):
            try:
                pwn = cmd[4:]
                position = self.decode_pwn(pwn)
                self.clean()
                self.play_all(position[1], position[0])
                return "pwnok"
            except Exception as e:
                with open("error.log", "w") as f:
                    f.write(traceback.format_exc())
                print(
                    f"{Fore.RED}Error while executing UWI command {cmd}. Check 'error.log' for details.{Style.RESET_ALL}"
                )
                return "pwnerror"
        elif cmd.startswith("win") or cmd.startswith("lose"):
            return cmd + "ok"

    def get_words_from_pattern(
        self, patterns: list[str], guesses: list[str]
    ) -> list[str]:
        """
        Quickly filter words based on patterns and guesses, minimizing unnecessary checks.
        """
        new_words = []

        for word in possible_guesses:
            if word in guesses:
                continue

            match = True
            for i, pattern in enumerate(patterns):
                for j, char in enumerate(word):
                    if pattern[j] == "-" and char in guesses[i]:
                        match = False
                        break
                    elif pattern[j] == "y" and (
                        char not in guesses[i] or word[i] == guesses[i][j]
                    ):
                        match = False
                        break
                    elif pattern[j] == "g" and word[j] != guesses[i][j]:
                        match = False
                        break

                if not match:
                    break

            if match:
                new_words.append(word)

        return new_words

    def calculate_entropy(self, guess: str, possible_words: list[str]) -> float:
        """
        Calculate and cache the entropy for a given guess based on the possible words.
        """
        if guess in self.entropy_cache:
            return self.entropy_cache[guess]

        pattern_counts = {}

        for word in possible_words:
            pattern = get_answer(guess, word)  # Simulate the pattern for this guess
            if pattern not in pattern_counts:
                pattern_counts[pattern] = 0
            pattern_counts[pattern] += 1

        entropy = 0.0
        total_words = len(possible_words)

        for pattern, count in pattern_counts.items():
            probability = count / total_words
            entropy -= probability * math.log2(probability)

        self.entropy_cache[guess] = entropy
        return entropy

    def get_entropy_frequency_weights(
        self,
        remaining_words_count: int,
        total_words_count: int,
        entropy_weight_multiplier: float = 0.8,
    ) -> tuple[float, float]:
        """
        Dynamically calculate weights for entropy and frequency based on the number of remaining possible words.

        Args:
            remaining_words_count (int): The current number of possible words.
            total_words_count (int): The total number of words in the dictionary.

        Returns:
            tuple[float, float]: A tuple of entropy weight and frequency weight.
        """
        # Early in the game (many possible words), prioritize entropy
        entropy_weight = (
            remaining_words_count / total_words_count
        ) * entropy_weight_multiplier

        # Later in the game (fewer possible words), prioritize frequency
        frequency_weight = max(3.0 - entropy_weight, 1.0)

        return entropy_weight, frequency_weight

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
                    obj
                    for obj in self.unknown
                    if obj["char"] != char or obj["index"] == i
                ]

    def play_all(self, guesses: list[str], answers: list[str]):
        for guess, answer in zip(guesses, answers):
            self.play(guess, answer)

    def rank_all_guesses(self, guesses: list[str]) -> str:
        """
        Rank all guesses in parallel using concurrent processing to speed up the ranking process.
        """
        best_score = -math.inf
        best_guess = None

        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            future_to_guess = {
                executor.submit(self.rank_guess, guess): guess for guess in guesses
            }

            for future in concurrent.futures.as_completed(future_to_guess):
                guess = future_to_guess[future]
                score = future.result()

                if score > best_score:
                    best_score = score
                    best_guess = guess

        return best_guess

    def rank_guess(
        self,
        guess: str,
        frequency_multiplier: float = 10.0,
        discard_guesses_not_in_freqs: bool = True,
    ) -> float:
        if not guess or guess in self.known_not_words:
            return -math.inf

        if any(char in self.not_possible_chars for char in guess):
            return -math.inf  # Early return for impossible guesses

        possible_words = self.get_words_from_pattern(self.patterns, self.guesses)
        if not possible_words:
            # print(
            #     f"{Fore.RED}Error: No possible words found for guess: {guess}. Using all possible words.{Style.RESET_ALL}"
            # )
            possible_words = possible_guesses

        # Skip guesses that are not in the frequency list
        score_penalty = 0
        if guess not in freqs and discard_guesses_not_in_freqs:
            score_penalty = 100  # Discard guesses not in the frequency list

        # Calculate entropy for the guess, but skip already invalid guesses
        entropy = self.calculate_entropy(guess, possible_words)

        # Calculate frequency score
        frequency_score = float(freqs.get(guess, 0.075)) * frequency_multiplier

        # Get dynamic weights
        total_words_count = len(possible_guesses)
        remaining_words_count = len(possible_words)
        entropy_weight, frequency_weight = self.get_entropy_frequency_weights(
            remaining_words_count, total_words_count
        )

        # Combine entropy and frequency scores
        score = (
            (entropy_weight * entropy)
            + (frequency_weight * frequency_score)
            - score_penalty
        )

        return score

    def best_guess(self, discard_guesses_not_in_freqs: bool = True) -> str | None:
        if not self.guesses:
            return self.starting_word

        best_score = -math.inf
        best_guess = None

        # Get possible guesses from current patterns and guesses
        guesses = self.get_words_from_pattern(self.patterns, self.guesses)

        # If no words match the pattern, use the full possible guess list
        if not guesses:
            guesses = possible_guesses

        if not guesses:
            print(f"{Fore.RED}Ran out of guesses{Style.RESET_ALL}")
            return None

        # Find the best guess based on rank (entropy + frequency combined)
        for guess in guesses:
            score = self.rank_guess(
                guess,
                10 if discard_guesses_not_in_freqs else 1,
                discard_guesses_not_in_freqs,
            )
            if score > best_score:
                best_score = score
                best_guess = guess

        if best_guess is None:
            if discard_guesses_not_in_freqs:
                print(
                    f"{Fore.RED}Ran out of guesses so switching to not discard guesses not in the frequency list{Style.RESET_ALL}"
                )
                return self.best_guess(False)

            print(f"{Fore.RED}Ran out of guesses{Style.RESET_ALL}")
            return None

        return best_guess

    def get_emoji_rep(self):
        green = "🟩"
        yellow = "🟨"
        grey = "⬛"

        representation = ""
        for i, pattern in enumerate(self.patterns):
            pattern = (
                pattern.replace("g", green).replace("y", yellow).replace("-", grey)
            )
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
