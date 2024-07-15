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
