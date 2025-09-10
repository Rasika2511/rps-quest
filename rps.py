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
    draw_pairs={('r','rock'),('p','paper'),('s','scissors')}
    return 'win' if (user,cpu) in winning_pairs else 'draw' if user==cpu or (user,cpu) in draw_pairs else 'lose'

#user=user_input()
#cpu=cpu_choice()
#print(decide_winner(user,'paper'))

results=[]


for i in range(3):
    user=user_input()
    cpu=cpu_choice()
    if decide_winner(user,cpu)=='draw':
        pass
    else:
        results.append(decide_winner(user,cpu))

print(results)
if ('win','win') in results:
    print('you win!')
else:
    print('you lose')







