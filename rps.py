import random

possible_options=['rock','paper','scissors']
po=['r','p','s']

def user_input():
    user_choice=input('Enter rock (or r), paper (or p) or scissors (or s): ').lower()
    if user_choice in possible_options or user_choice in po:
        return user_choice
    else:
        print('Please enter one of the specified values')
        exit()

def cpu_choice():
    outcome=random.choice(possible_options)
    print(f'Computer picked {outcome}')
    return outcome

def decide_winner(user: str, cpu: str):
    winning_pairs={('rock','scissors'),('paper','rock'),('scissors','paper'),('r','scissors'),('p','rock'),('s','paper')}
    return 'win' if (user,cpu) in winning_pairs else 'draw' if user==cpu else 'lose'

results=[]
cpu_outcomes=[]

for i in range(3):
    user=user_input()
    cpu=cpu_choice()
    cpu_outcomes.append(cpu)
    results.append(decide_winner(user,cpu))








