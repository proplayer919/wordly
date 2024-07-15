from wordly import play, best_guess
from colorama import Fore, Style
from utils import get_answer

possible_answers = [x for x in open("answers.txt", "r").read().splitlines() if x]

starting_word = "atone"

amounts = [0] * 7


print(f"{Fore.CYAN}WORDLY TESTER{Style.RESET_ALL}")

for i in range(len(possible_answers)):
    target = possible_answers[i]

    answer = get_answer(starting_word, target)

    if answer == "ggggg":
        print(f"{Fore.RED}Got in 1: {Style.RESET_ALL}{starting_word}")
        amounts[0] += 1
        continue

    play(starting_word, answer)

    guess = best_guess()

    if not guess:
        amounts[6] += 1
        continue

    for j in range(5):
        answer = get_answer(guess, target)

        if answer == "ggggg":
            print(f"{Fore.RED}Got in {j+2}: {Style.RESET_ALL}{guess}")
            amounts[j + 1] += 1
            break

        play(guess, answer)

        guess = best_guess()

        if not guess:
            amounts[6] += 1
            break

total = sum(amounts) - amounts[6]

print(f"\n{Fore.BLUE}Results: {Style.RESET_ALL}")

for i in range(6):
    print(
        f"{Fore.MAGENTA}Got in {i+1}: {Style.RESET_ALL}{amounts[i]} - {round(amounts[i] / total * 100, 2)}%"
    )

print(
    f"{Fore.RED}Failed (ran out of guesses): {Style.RESET_ALL}{amounts[6]} - {round(amounts[6] / total * 100, 2)}%"
)
