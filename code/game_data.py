# Layers are stacked in order of drawing
level_0 = {
    'terrain': {
        'path': '../levels/level_data/0/level0_Level.csv',
        'type': 'static'
    },
    'scenery': {
        'path': '../levels/level_data/0/level0_Scenery.csv',
        'type': 'static'
    },
    'scenery2': {
        'path': '../levels/level_data/0/level0_Additional Scenery.csv',
        'type': 'static'
    },
    'player': {
        'path': '../levels/level_data/0/level0_Mario.csv',
        'type': 'player'
    }
}

player = {
    'sprite_sheet_path': '../imgs/player/shroomaddict.png',
    'animation_idle': {
        'frames': [0],
        'fps': 1,
    },
    'animation_walking': {
        'frames': [1, 2, 3],
        'fps': 10
    },
    'animation_running': {
        'frames': [1, 2, 3],
        'fps': 16
    },
    'animation_jumping': {
        'frames': [5],
        'fps': 1
    }
}
