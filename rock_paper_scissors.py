"""
Rock, Paper, Scissors - Task 4

A simple command line game where the player goes up against the
computer. Keeps score across rounds and lets the player quit whenever
they want.
"""

import random

# the three valid moves, kept in one place so it's easy to change later
CHOICES = ["rock", "paper", "scissors"]

# maps each move to the move it beats
# e.g. rock beats scissors, so CHOICES beats = {"rock": "scissors", ...}
BEATS = {
    "rock": "scissors",
    "scissors": "paper",
    "paper": "rock"
}


def get_user_choice():
    """Ask the player to pick rock, paper or scissors and validate the input."""
    while True:
        choice = input("Choose rock, paper, or scissors: ").strip().lower()

        # let people type just the first letter too, feels nicer to use
        if choice in ("r", "p", "s"):
            choice = {"r": "rock", "p": "paper", "s": "scissors"}[choice]

        if choice in CHOICES:
            return choice

        print("That's not a valid choice, try again (rock/paper/scissors).\n")


def get_computer_choice():
    """Randomly pick a move for the computer."""
    return random.choice(CHOICES)


def decide_winner(user, computer):
    """
    Work out who won this round.
    Returns "user", "computer" or "tie".
    """
    if user == computer:
        return "tie"
    elif BEATS[user] == computer:
        return "user"
    else:
        return "computer"


def print_round_result(user, computer, winner):
    """Print out what happened this round in a readable way."""
    print(f"\nYou chose:      {user}")
    print(f"Computer chose: {computer}")

    if winner == "tie":
        print("It's a tie!\n")
    elif winner == "user":
        print("You win this round!\n")
    else:
        print("Computer wins this round!\n")


def ask_play_again():
    """Ask the player if they want another round, keep asking until we get a clear answer."""
    while True:
        answer = input("Play again? (y/n): ").strip().lower()
        if answer in ("y", "yes"):
            return True
        elif answer in ("n", "no"):
            return False
        else:
            print("Please answer with y or n.")


def main():
    print("=" * 40)
    print("   ROCK, PAPER, SCISSORS")
    print("=" * 40)
    print("Rock beats scissors, scissors beats paper, paper beats rock.")
    print("First to quit ends the game. Good luck!\n")

    # running totals for the whole session
    user_score = 0
    computer_score = 0
    ties = 0
    round_number = 1

    while True:
        print(f"--- Round {round_number} ---")

        user_choice = get_user_choice()
        computer_choice = get_computer_choice()
        winner = decide_winner(user_choice, computer_choice)

        print_round_result(user_choice, computer_choice, winner)

        # update the scoreboard based on who won
        if winner == "user":
            user_score += 1
        elif winner == "computer":
            computer_score += 1
        else:
            ties += 1

        print(f"Score -> You: {user_score}  Computer: {computer_score}  Ties: {ties}\n")

        if not ask_play_again():
            break

        round_number += 1
        print()  # just a blank line to separate rounds visually

    # final summary once the player decides to stop
    print("\n" + "=" * 40)
    print("Thanks for playing! Final score:")
    print(f"You: {user_score}   Computer: {computer_score}   Ties: {ties}")

    if user_score > computer_score:
        print("You came out on top overall. Nice one!")
    elif computer_score > user_score:
        print("Computer got the better of you this time. Rematch soon?")
    else:
        print("Overall it's a tie, nobody's bragging rights here.")
    print("=" * 40)


if __name__ == "__main__":
    main()
