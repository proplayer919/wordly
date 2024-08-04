from colorama import Fore, Style

with open("answers.txt", "r") as f:
    possible_answers = [line.strip() for line in f if line.strip()]

print(f"{Fore.CYAN}WORDLY WORD FINDER{Style.RESET_ALL}")

known = input(f"{Fore.YELLOW}Enter known letters ('*' for unknown): {Style.RESET_ALL}")

not_allowed = input(f"{Fore.YELLOW}Enter not allowed words (comma separated): {Style.RESET_ALL}")

not_allowed = not_allowed.split(",") if not_allowed else []

if not known:
    known = "*****"
else:
    known = known.lower()
    
# find the answer that matches the known letters
for answer in possible_answers:
    if known == "*****":
        print(f"{Fore.GREEN}Found: {Style.RESET_ALL}{answer}")
        exit()
        
    if answer in not_allowed:
        continue
    
    for i in range(len(known)):
        if known[i] == "*":
            continue
        if known[i] != answer[i]:
            break
    else:
        print(f"{Fore.GREEN}Found: {Style.RESET_ALL}{answer}")
        exit()

print(f"{Fore.RED}No matches found{Style.RESET_ALL}")
