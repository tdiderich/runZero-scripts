import random

participants = random.sample([
    'Tyler',
    'Marc',
    'Boneil',
    'Dan',
    'Ariana',
    'Eric',
    'Ryan',
    'Madison',
    'Joni',
    'Pearce',
    'Jay',
    'Jon'
], 12)

placeholder = 0
for x in range(1, 4):
    print(f'Group {x}')
    for y in range(4):
        print(participants[placeholder])
        placeholder += 1
