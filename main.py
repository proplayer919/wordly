from wordly import play, best_guess
from colorama import Fore, Style

starting_word = "atone"

print(f"{Fore.CYAN}WORDLY{Style.RESET_ALL}")

print(
    f"{Fore.BLUE}How to enter answers: 'g' for a green letter, 'y' for a yellow letter, '-' for a grey letter. Example: '-gy--'{Style.RESET_ALL}"
)

guess = input(
    f'{Fore.YELLOW}Enter starting word (blank for "{starting_word}"): {Style.RESET_ALL}'
)
answer = input(f"{Fore.GREEN}Enter answer: {Style.RESET_ALL}")

play(guess, answer)

guess = best_guess()

if not guess:
    exit()

print(f"{Fore.LIGHTMAGENTA_EX}Best guess: {Style.RESET_ALL}{guess}")

for i in range(5):
    answer = input(f"{Fore.GREEN}Enter answer: {Style.RESET_ALL}")

    if answer == "ggggg":
        print(f"{Fore.RED}Correct: {Style.RESET_ALL}{guess}")
        exit()

    if i == 4:
        print(f"{Fore.RED}Incorrect: {Style.RESET_ALL}The target wasn't found")
    else:
        play(guess, answer)

        guess = best_guess()

        if not guess:
            exit()
        print(f"{Fore.LIGHTMAGENTA_EX}Best guess: {Style.RESET_ALL}{guess}")
