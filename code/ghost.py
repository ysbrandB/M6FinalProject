import math
import pygame

from settings import ghost_tiles_to_follow, ghost_scare_timer
from tiles import AnimatableTile
from helpers import map_from_to, find_nearest_passage_to_vector

# a class dedicated to showing, updating and pathfinding the ghosts of pacman

class Ghost(AnimatableTile):
    def __init__(self, size, grid_position, frames, data, ghost_id):
        # initialize the super class animatable tile
        super().__init__(size, grid_position, frames, data)
        # set all necessary variables
        self.dir = pygame.math.Vector2(0, 0)
        self.id = ghost_id
        sprite_row_start = ghost_id * 8
        other_frames = self.frames[4 * 8:6 * 8]
        self.frames = self.frames[sprite_row_start:sprite_row_start + 8]
        self.frames.extend(other_frames)
        self.animation = data['animation_left']
        self.target = None
        self.path = None
        self.tiles_followed = 0
        self.origin = pygame.math.Vector2(math.floor(self.position.x / self.size),
                                          math.floor(self.position.y / self.size))

        self.FOLLOWING = 0
        self.SPREADING = 1
        self.DEAD = 2
        self.SCARED = 3
        self.state = self.FOLLOWING
        self.manhattan_dist_to_player = 5
        self.scare_cooldown = 0

    def live(self, dt, surface, player, passages, ghosts, ghost_follow):
        self.position += (self.dir.elementwise() * dt * 0.5)
        self.grid_position = pygame.math.Vector2(math.floor(self.position.x / self.size),
                                                 math.floor(self.position.y / self.size))
        self.manhattan_dist_to_player = abs(self.grid_position.x - player.grid_position.x) + abs(
            self.grid_position.y - player.grid_position.y)
        self.move_to_target(player, passages, ghosts)
        self.set_animation()
        self.set_state(ghost_follow)
        self.animate(dt)
        # self.draw_path(surface)
        self.draw(surface)

        if self.scare_cooldown > 0:
            self.scare_cooldown -= dt
            print(self.scare_cooldown)
            if self.scare_cooldown < 0:
                self.scare_cooldown = 0

    def set_state(self, ghost_follow):
        # set the state this ghost is in, following or spreading decided by level, the rest by the ghost itself
        if self.state == self.DEAD:
            if self.origin.distance_to(self.grid_position) < 2:
                self.state = self.FOLLOWING

        elif self.state != self.SCARED or self.state == self.SCARED and self.scare_cooldown <= 0:
            if ghost_follow:
                self.state = self.FOLLOWING
            else:
                self.state = self.SPREADING

    def move_to_target(self, player, passages, ghosts):
        # follow the calculated path for at least an x number of tiles,
        # also makes sure the path is only calculated when the tiles are followed or the path is None(speed improvement)
        if self.path is None or self.tiles_followed >= ghost_tiles_to_follow:
            self.search_path(player, passages, ghosts)
            self.tiles_followed = 0

        # get the next node in the path and set direction to the nearest node
        elif self.target is None and len(self.path) > 0:
            self.tiles_followed += 1
            self.target = self.path.pop()
            if self.target:
                if self.target.grid_position and self.grid_position:
                    self.dir = self.target.grid_position - self.grid_position

        # when the ghost is moving to its target, make sure it does it in a grid-like fashion and make it stop at the
        # center of the next tile, to decide if the next node of the path needs to be followed or if the path needs to
        # be recalculated
        elif self.target is not None:
            if (math.dist(self.target.get_center(), self.get_center())) < 1:
                self.tiles_followed += 1
                self.set_center(self.target.get_center())
                self.dir = pygame.math.Vector2(0, 0)
                self.target = None

        elif len(self.path) <= 0:
            self.search_path(player, passages, ghosts)

    # set the center of the ghost to a vector
    def set_center(self, center):
        self.position = pygame.math.Vector2(center.x - self.size / 2, center.y - self.size / 2)

    # determine the animation based upon the state the ghost is in
    def set_animation(self):
        if self.state is self.SCARED:
            if self.id % 2 == 0:
                self.animation = self.data['animation_scared']
            else:
                self.animation = self.data['animation_scared_white']

        else:
            # determine the animation based upon direction and if the ghost is dead
            match self.dir.x:
                case -1:
                    self.animation = self.data[f'animation{"_dead" if self.state == self.DEAD else ""}_left']
                case 1:
                    self.animation = self.data[f'animation{"_dead" if self.state == self.DEAD else ""}_right']

            match self.dir.y:
                case -1:
                    self.animation = self.data[f'animation{"_dead" if self.state == self.DEAD else ""}_up']
                case 1:
                    self.animation = self.data[f'animation{"_dead" if self.state == self.DEAD else ""}_down']
        if self.frame_index >= len(self.frames):
            self.frame_index = 0
    # draw the current path of the ghost with a color based upon id and brightness based upon the vicinity to the target
    def draw_path(self, surface):
        if self.path:
            for index, tile in enumerate(self.path):
                if tile:
                    if index == 0:
                        tile.draw_debug_square(surface, (255, 0, 0), 255)
                    else:
                        tile.draw_debug_square(surface, (
                            map_from_to(self.id, 0, 4, 0, 255), map_from_to(self.id, 0, 4, 255, 0),
                            map_from_to(self.id, 0, 4, 0, 255)),
                                               map_from_to(index, 0, len(self.path), 0, 255))

    def die(self):
        self.state = self.DEAD

    def scare(self):
        self.state = self.SCARED
        self.scare_cooldown = ghost_scare_timer

    def find_scare_position(self, passages, player):
        vector = (self.position-player.position)+self.position
        return find_nearest_passage_to_vector(vector, passages)
