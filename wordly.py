from engine import Game, get_answer
from colorama import Fore, Style
import random
import os
import traceback
import datetime
import requests


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

        uwi = game.uwi_cmd("uwi")
        if uwi is None or uwi != "uwi2ok":
            print(
                f"{Fore.RED}Error: Wordle Engine is not using UWIv2!{Style.RESET_ALL} Response: {uwi}"
            )
            return

        uwi = game.uwi_cmd("pos blank")
        if uwi is None or uwi != "posok":
            print(
                f"{Fore.RED}Error: Wordle Engine did not recognize a blank position!{Style.RESET_ALL} Response: {uwi}"
            )
            return

        starting_word = game.uwi_cmd("guess")
        if starting_word is None or not starting_word.startswith("guessok\n"):
            print(
                f"{Fore.RED}Error: Wordle Engine did not recognize the guess command!{Style.RESET_ALL} Response: {starting_word}"
            )
            return
        starting_word = starting_word[8:]

        answer = get_answer(starting_word, target)
        if answer is None:
            print(
                f"{Fore.RED}Error: Could not get answer for {starting_word} and {target}!"
            )
            return

        guess_count = 1  # Initial guess

        if answer == "ggggg":
            with open("wordly.log", "a") as f:
                f.write(f"{target} {guess_count}\n")
        else:
            current_pwn = starting_word + answer

            pwn = game.uwi_cmd("pwn " + current_pwn)
            if pwn is None or pwn != "pwnok":
                print(
                    f"{Fore.RED}Error: Wordle Engine did not recognize the pwn command!{Style.RESET_ALL} Response: {pwn}"
                )
                return

            guess = None
            answer = None

            while True:
                guess = game.uwi_cmd("guess")
                if guess is None or not guess.startswith("guessok\n"):
                    print(
                        f"{Fore.RED}Error: Wordle Engine did not recognize the guess command!{Style.RESET_ALL} Response: {guess}"
                    )
                    return
                guess = guess[8:]
                if not guess:
                    return

                answer = get_answer(guess, target)
                if answer is None:
                    print(
                        f"{Fore.RED}Error: Could not get answer for {guess} and {target}!"
                    )
                    return

                current_pwn = current_pwn + "/" + guess + answer

                pwn = game.uwi_cmd("pwn " + current_pwn)
                if pwn is None or pwn != "pwnok":
                    print(
                        f"{Fore.RED}Error: Wordle Engine did not recognize the pwn command!{Style.RESET_ALL} Response: {pwn}"
                    )
                    return

                if answer == "ggggg":
                    with open("wordly.log", "a") as f:
                        f.write(f"{target} {guess_count}\n")
                    break

                answer = get_answer(guess, target)
                if answer is None:
                    print(
                        f"{Fore.RED}Error: Could not get answer for {guess} and {target}!"
                    )
                    return
                guess_count += 1

        total_guesses += guess_count
        games_played += 1

    return total_guesses / total_games


def play_game(target=None, max_guesses=5):
    """Play a single game with an optional target and allowed guesses."""
    game = Game()

    uwi = game.uwi_cmd("uwi")
    if not uwi == "uwi2ok":
        print(
            f"{Fore.RED}Error: Wordle Engine is not using UWIv2!{Style.RESET_ALL} Response: {uwi}"
        )
        return

    uwi = game.uwi_cmd("pos blank")
    if not uwi == "posok":
        print(
            f"{Fore.RED}Error: Wordle Engine did not recognize a blank position!{Style.RESET_ALL} Response: {uwi}"
        )
        return

    if target is None:
        target = random.choice(load_words("answers.txt"))
        print(f"{Fore.YELLOW}Using random target: {Style.RESET_ALL}{target}")

    starting_word = game.uwi_cmd("guess")
    if not starting_word.startswith("guessok\n"):
        print(
            f"{Fore.RED}Error: Wordle Engine did not recognize the guess command!{Style.RESET_ALL} Response: {starting_word}"
        )
        return
    starting_word = starting_word[8:]
    if not starting_word.strip():
        print(f"{Fore.RED}Error: Empty guess!{Style.RESET_ALL}")
        return

    answer = get_answer(starting_word, target)

    current_pwn = starting_word + answer

    pwn = game.uwi_cmd("pwn " + current_pwn)
    if not pwn == "pwnok":
        print(
            f"{Fore.RED}Error: Wordle Engine did not recognize the pwn command!{Style.RESET_ALL} Response: {pwn}"
        )
        return

    if answer == "ggggg":
        game.uwi_cmd("win1")
        print(game.get_combined_rep())
    else:
        guess = game.uwi_cmd("guess")
        if not guess.startswith("guessok\n"):
            print(
                f"{Fore.RED}Error: Wordle Engine did not recognize the guess command!{Style.RESET_ALL} Response: {guess}"
            )
            return
        guess = guess[8:]
        if not guess.strip():
            print(f"{Fore.RED}Error: Empty guess!{Style.RESET_ALL}")
            return

        for i in range(max_guesses):
            answer = get_answer(guess, target)

            current_pwn = current_pwn + "/" + guess + answer

            pwn = game.uwi_cmd("pwn " + current_pwn)
            if not pwn == "pwnok":
                print(
                    f"{Fore.RED}Error: Wordle Engine did not recognize the pwn command!{Style.RESET_ALL} Response: {pwn}"
                )
                return

            if answer == "ggggg":
                game.uwi_cmd("win" + str(i + 2))
                print(game.get_combined_rep())
                return

            if i != max_guesses - 1:
                guess = game.uwi_cmd("guess")
                if not guess.startswith("guessok\n"):
                    print(
                        f"{Fore.RED}Error: Wordle Engine did not recognize the guess command!{Style.RESET_ALL} Response: {guess}"
                    )
                    return
                guess = guess[8:]
                if not guess.strip():
                    print(f"{Fore.RED}Error: Empty guess!{Style.RESET_ALL}")
                    return
            else:
                game.uwi_cmd("lose" + str(i + 2))
                print(game.get_combined_rep())
                return


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
        or 5
    )
    play_game(target, max_guesses)


def interactive_uwi():
    game = Game()

    while True:
        cmd = input(f"{Fore.CYAN}uwi> {Style.RESET_ALL}")
        if cmd == "exit":
            break
        print(game.uwi_cmd(cmd))


def main():
    print(f"{Fore.CYAN}WORDLY V2{Style.RESET_ALL}")

    try:
        mode = int(
            input(
                f"{Fore.YELLOW}Choose mode (1: Custom Game, 2: Today's Wordle, 3: Test WSE rating, 4. Interactive UWI): {Style.RESET_ALL}"
            )
        )
    except ValueError:
        print(f"{Fore.RED}Invalid mode{Style.RESET_ALL}")
        return

    if mode == 1:
        custom_mode()
    elif mode == 2:
        date = datetime.date.today()
        url = f"https://www.nytimes.com/svc/wordle/v2/{date:%Y-%m-%d}.json"
        response = requests.get(url).json()
        custom_mode(response["solution"])
    elif mode == 3:
        print(f"{Fore.CYAN}Testing all possible answers...{Style.RESET_ALL}")
        avg_guesses = simulate_game_for_all_targets(load_words("answers.txt"))
        print(f"{Fore.GREEN}Average guesses: {avg_guesses}{Style.RESET_ALL}")
    elif mode == 4:
        interactive_uwi()

    if input(f"{Fore.MAGENTA}Play again? (1: yes, 2: no): {Style.RESET_ALL}") == "1":
        main()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        with open("error.log", "w") as f:
            f.write(traceback.format_exc())
        print(f"{Fore.RED}Error. Check 'error.log' for details.{Style.RESET_ALL}")
