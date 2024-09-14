from engine import Game, get_answer
from colorama import Fore, Style
import random
import os
import traceback
import datetime
import requests

starting_word = "salet"


def load_words(filename):
    """Load words from a file, stripping any empty lines."""
    with open(filename, "r") as f:
        return [line.strip() for line in f if line.strip()]


def clear_screen():
    """Clear the console screen."""
    os.system("cls" if os.name == "nt" else "clear")


def display_word_test(target, total_guesses, total_games):
    """Display the current word being tested with progress."""
    clear_screen()
    print(
        f"{Fore.CYAN}Testing word: {Fore.YELLOW}{target} ({total_guesses / total_games * 100:.2f}%){Style.RESET_ALL}"
    )


def simulate_game_for_all_targets(possible_guesses):
    """Simulate games for all possible guesses and return the average guesses."""
    total_guesses = 0
    total_games = len(possible_guesses)
    games_played = 0

    for target in possible_guesses:
        display_word_test(target, games_played, total_games)

        game = Game()
        guess = game.best_guess()
        guess_count = 1  # Initial guess

        while guess and guess_count < 6:
            answer = get_answer(guess, target)
            game.play(guess, answer)

            if answer == "ggggg":
                print(game.get_combined_rep())
                break

            guess = game.best_guess()
            guess_count += 1

        total_guesses += guess_count
        games_played += 1

    return total_guesses / total_games


def play_game(target=None, max_guesses=6):
    """Play a single game with an optional target and allowed guesses."""
    game = Game()

    if target is None:
        target = random.choice(load_words("answers.txt"))
        print(f"{Fore.YELLOW}Using random target: {Style.RESET_ALL}{target}")

    print(f"{Fore.BLUE}Starting word: {Style.RESET_ALL}{starting_word}")
    answer = get_answer(starting_word, target)
    
    print(f"{Fore.GREEN}Answer: {Style.RESET_ALL}{answer}")

    if answer == "ggggg":
        print(f"{Fore.BLUE}Correct in 1: {Style.RESET_ALL}{starting_word}")
        game.play(starting_word, answer)
        print(game.get_combined_rep())
    else: 
        game.play(starting_word, answer)
        print(game.get_combined_rep())

        guess = game.best_guess()
        if not guess:
            return

        print(f"{Fore.LIGHTMAGENTA_EX}Best guess: {Style.RESET_ALL}{guess}")

        for i in range(max_guesses):
            answer = get_answer(guess, target)
            print(f"{Fore.GREEN}Answer: {Style.RESET_ALL}{answer}")

            if answer == "ggggg":
                print(f"{Fore.BLUE}Correct in {i + 2}: {Style.RESET_ALL}{guess}")
                game.play(guess, answer)
                print(game.get_combined_rep())
                break

            if i == max_guesses - 1:
                print(f"{Fore.RED}Incorrect: {Style.RESET_ALL}{target} wasn't found")
            else:
                game.play(guess, answer)
                print(game.get_combined_rep())
                guess = game.best_guess()
                if not guess:
                    return
                print(f"{Fore.LIGHTMAGENTA_EX}Best guess: {Style.RESET_ALL}{guess}")


def normal_mode():
    """Play in normal mode where the user enters the answers manually."""
    global starting_word

    print(
        f"{Fore.BLUE}How to enter answers: 'g' for green, 'y' for yellow, '-' for grey. Example: '-gy--'{Style.RESET_ALL}"
    )
    starting_word = (
        input(
            f'{Fore.YELLOW}Enter starting word (blank for "{starting_word}"): {Style.RESET_ALL}'
        )
        or starting_word
    )
    answer = input(f"{Fore.GREEN}Enter answer: {Style.RESET_ALL}")

    game = Game()
    game.play(starting_word, answer)
    print(game.get_combined_rep())

    guess = game.best_guess()
    if not guess:
        return

    print(f"{Fore.LIGHTMAGENTA_EX}Best guess: {Style.RESET_ALL}{guess}")

    for i in range(6):
        answer = input(f"{Fore.GREEN}Enter answer: {Style.RESET_ALL}")

        if answer == "ggggg":
            print(f"{Fore.BLUE}Correct in {6 - i}: {Style.RESET_ALL}{guess}")
            game.play(guess, answer)
            print(game.get_combined_rep())
            break
        elif i == 4:
            print(f"{Fore.RED}Incorrect: {Style.RESET_ALL}Target not found")
        else:
            game.play(guess, answer)
            print(game.get_combined_rep())
            guess = game.best_guess()
            if not guess:
                return
            print(f"{Fore.LIGHTMAGENTA_EX}Best guess: {Style.RESET_ALL}{guess}")
            
def custom_mode(target=None):
    if not target:
        target = input(
            f"{Fore.BLUE}Enter target word: {Style.RESET_ALL}"
        ) or random.choice(load_words("answers.txt"))
    print(f"{Fore.YELLOW}Using target: {Style.RESET_ALL}{target}")
    max_guesses = int(
        input(
            f"{Fore.YELLOW}Enter number of allowed guesses (default 6): {Style.RESET_ALL}"
        )
        or 6
    )
    play_game(target, max_guesses)

def main():
    print(f"{Fore.CYAN}WORDLY V2{Style.RESET_ALL}")

    try:
        mode = int(
            input(
                f"{Fore.YELLOW}Choose mode (1: normal, 2: custom, 3: today's, 4: test): {Style.RESET_ALL}"
            )
        )
    except ValueError:
        print(f"{Fore.RED}Invalid mode{Style.RESET_ALL}")
        return

    if mode == 1:
        normal_mode()
    elif mode == 2:
        custom_mode()
    elif mode == 3:
        date = datetime.date.today()
        url = f"https://www.nytimes.com/svc/wordle/v2/{date:%Y-%m-%d}.json"
        response = requests.get(url).json()
        custom_mode(response['solution'])
    elif mode == 4:
        print(f"{Fore.CYAN}Testing all possible answers...{Style.RESET_ALL}")
        avg_guesses = simulate_game_for_all_targets(load_words("answers.txt"))
        print(f"{Fore.GREEN}Average guesses: {avg_guesses}{Style.RESET_ALL}")

    if input(f"{Fore.MAGENTA}Play again? (1: yes, 2: no): {Style.RESET_ALL}") == "1":
        main()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        with open("error.log", "w") as f:
            f.write(f"{str(e)}\n")
            f.write(traceback.format_exc())
        print(f"{Fore.RED}Error. Check 'error.log' for details.{Style.RESET_ALL}")
