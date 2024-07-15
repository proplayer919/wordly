import math

# Read and process the possible guesses
with open("guesses.txt", "r") as f:
    possible_guesses = [line.strip() for line in f if line.strip()]

# Use sets for faster membership testing
not_possible_chars = set()
known_not_words = set()

# Initialize known and unknown structures
known = ["*"] * 5
unknown = []


def play(guess: str, answer: str):
    if guess not in known_not_words:
        known_not_words.add(guess)

    for i, char in enumerate(guess):
        if answer[i] == "-":
            not_possible_chars.add(char)
        elif answer[i] == "y":
            obj = {"char": char, "index": i}
            if obj not in unknown:
                unknown.append(obj)
        else:
            known[i] = char
            unknown[:] = [
                obj for obj in unknown if obj["char"] != char or obj["index"] == i
            ]


def rank_guess(guess: str):
    if not guess or guess in known_not_words:
        return -math.inf

    score = 0
    for i, char in enumerate(guess):
        if char in not_possible_chars:
            score -= 2
        if known[i] == char:
            score += 1
        score += sum(
            0.5 for obj in unknown if obj["char"] == char and obj["index"] != i
        )

    return score


def best_guess():
    best_score = -math.inf
    best_guess = None

    for guess in possible_guesses:
        score = rank_guess(guess)
        if score > best_score:
            best_score = score
            best_guess = guess

    if best_guess is None:
        print("Ran out of guesses")

    return best_guess
