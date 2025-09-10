import random

possible_options=['rock','paper','scissors']

def user_input():
    user_choice=input('Enter rock (or r), paper (or p) or scissors (or s): ').lower()
    if user_choice in possible_options:
        return user_choice
    else:
        print('Please enter one of the specified values')
        exit()
def cpu_choice():
    outcome=random.choice(possible_options)
    print(f'Computer picked {outcome}')
    return outcome

def decide_winner(user: str, cpu: str):
    winning_pairs={('rock','scissors'),('paper','rock'),('scissors','paper'),('r','s'),('p','r'),('s','p')}
    return 'win' if (user,cpu) in winning_pairs else 'draw' if user==cpu else 'lose'

user=user_input()
cpu=cpu_choice()
print(decide_winner(user,cpu))






