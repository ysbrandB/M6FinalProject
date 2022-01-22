# Layers are stacked in order of drawing
level_0 = {
    'tiles_sheet_path': '../imgs/terrain/mario_terrain.png',
    'layers': {
        'terrain': {
            'path': '../levels/level_data/0/level0_Level.csv',
            'type': 'static'
        },
        'ghost_passage': {
            'path': '../levels/level_data/0/level0_GhostPassage.csv',
            'type': 'passage'
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
        },
        'coins': {
            'path': '../levels/level_data/0/level0_Coins.csv',
            'type': 'coin'
        },
        'question_blocks': {
            'path': '../levels/level_data/0/level0_Question_blocks.csv',
            'type': 'question_block'
        }
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
    'seconds_following': 12,
    'seconds_spreading': 8,
    'animation_idle': {
        'frames': [0],
        'fps': 1
    },
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
    },
    'animation_scared': {
        'frames': [8, 9],
        'fps': 7
    }, 'animation_scared_white': {
        'frames': [10, 11],
        'fps': 7
    }, 'animation_dead_right': {
        'frames': [12],
        'fps': 1
    }, 'animation_dead_left': {
        'frames': [13],
        'fps': 1
    }, 'animation_dead_up': {
        'frames': [14],
        'fps': 1
    }, 'animation_dead_down': {
        'frames': [15],
        'fps': 1
    }
}

coins = {
    'sprite_sheet_path': '../imgs/coin/coin.png',
    'animation_idle': {
        'frames': [0, 1, 2, 3, 4, 5, 6, 7],
        'fps': 10
    }
}

question_block = {
    'sprite_sheet_path': '../imgs/question_block/question_block.png',
    'animation_idle': {
        'frames': [0, 1, 2],
        'fps': 2
    },
    'animation_hit': {
        'frames': [2, 3],
        'fps': 2
    }
}


