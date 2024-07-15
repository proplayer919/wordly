from wordly import best_guess, play
from colorama import Fore, Style
import random
from utils import get_answer

possible_answers = [x for x in open("answers.txt", "r").read().splitlines() if x]

starting_word = "atone"


print(f"{Fore.CYAN}WORDLY CUSTOM GAME{Style.RESET_ALL}")

target = input(f"{Fore.YELLOW}Enter target word: {Style.RESET_ALL}")

if not target:
    target = possible_answers[random.randint(0, len(possible_answers) - 1)]

allowed_guesses = input(f"{Fore.YELLOW}Enter number of allowed guesses: {Style.RESET_ALL}")

if not allowed_guesses:
    allowed_guesses = 5
else:
    allowed_guesses = int(allowed_guesses) - 1

if target not in possible_answers:
    print(f"{Fore.RED}Invalid target word{Style.RESET_ALL}")
    exit()

print(f"{Fore.BLUE}Starting word: {Style.RESET_ALL}{starting_word}")

answer = get_answer(starting_word, target)

print(f"{Fore.GREEN}Starting Answer: {Style.RESET_ALL}{answer}")

play(starting_word, answer)

guess = best_guess()

if not guess:
    exit()

print(f"{Fore.LIGHTMAGENTA_EX}Best guess: {Style.RESET_ALL}{guess}")

for i in range(allowed_guesses):
    answer = get_answer(guess, target)

    print(f"{Fore.GREEN}Answer: {Style.RESET_ALL}{answer}")

    if answer == "ggggg":
        print(f"{Fore.BLUE}Correct in {i + 2}: {Style.RESET_ALL}{guess}")
        exit()

    if i == allowed_guesses - 1:
        print(f"{Fore.RED}Incorrect: {Style.RESET_ALL}{target} wasn't found")
    else:
        play(guess, answer)

        guess = best_guess()

        if not guess:
            exit()
        print(f"{Fore.LIGHTMAGENTA_EX}Best guess: {Style.RESET_ALL}{guess}")
