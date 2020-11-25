# Language: Python

import sys
from enum import Enum
from random import randint


def main():
    # Initialize
    choices = ["Rock", "Paper", "Scissors"]
    human_score, computer_score = 0, 0

    # Matrix-like dictionary to see which move is superior to which (move at index 0 relative to move at index 1)

    class Precedence(Enum):
        SUPERIOR = 1
        EQUAL = 0
        INFERIOR = -1

    win_lose = {'Rock': {'Paper': Precedence.INFERIOR, 'Rock': Precedence.EQUAL, 'Scissors': Precedence.SUPERIOR},
                'Paper': {'Paper': Precedence.EQUAL, 'Rock': Precedence.SUPERIOR, 'Scissors': Precedence.INFERIOR},
                'Scissors': {'Paper': Precedence.SUPERIOR, 'Rock': Precedence.INFERIOR, 'Scissors': Precedence.EQUAL}}

    while True:

        # computer's move is random
        rand_idx = randint(0, len(choices) - 1)
        computer_choice = choices[rand_idx]

        # human move from input
        human_choice = input("Choose between Rock, Paper, and Scissors: ")
        while human_choice not in choices:
            human_choice = input("Not a valid move. Please input either 'Rock', 'Paper', or 'Scissors': ")

        print('You played {}, while computer played {}'.format(human_choice, computer_choice))

        result_computer = win_lose[computer_choice][human_choice]

        if result_computer == Precedence.INFERIOR:
            print("You win a point, show us what you've got!")
            human_score += 1
        elif result_computer == Precedence.SUPERIOR:
            print("Computer wins a point. Oh no, AI is overtaking the world!")
            computer_score += 1
        else:
            print("It's a tie!")

        print('Your score: {}. Score for computer: {}'.format(human_score, computer_score))

        play_again = input("Do you want to play again?(y/n): ")
        while play_again not in ['y', 'n']:
            play_again = input("Invalid. Do you want to play again?(y/n): ")
        if play_again == 'y':
            continue
        elif play_again == 'n':
            print('Goodbye, World!')
            break


if __name__ == '__main__':
    sys.exit(main())
