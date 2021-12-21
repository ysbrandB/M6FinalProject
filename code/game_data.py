level_0={
    'terrain':'../levels/level_data/0/level0_Level.csv',
    'scenery':'../levels/level_data/0/level0_Scenery.csv'
}

if __name__=='__main__':
    print('main!')
    from csv import reader
    path=level_0['terrain']
    print(path)
    with open(path) as map:
        level = reader(map, delimiter=',')
        print(level)