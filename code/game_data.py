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
    },
    'ghosts': {
        'path': '../levels/level_data/0/level0_Pacman.csv',
        'type': 'ghosts'
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


ghosts = {
    'sprite_sheet_path': '../imgs/ghosts/ghost_sprites.png',
    'animation_right': {
        'frames': [0, 1],
        'fps': 7,
    },
    'animation_left': {
        'frames': [2, 3],
        'fps': 7
    },
    'animation_up': {
        'frames': [4, 5],
        'fps': 7
    },
    'animation_down': {
        'frames': [6, 7],
        'fps': 7
    }
}
