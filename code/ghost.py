import bisect
import math
import pygame

from settings import ghost_tiles_to_follow, tile_size, vertical_tile_number, horizontal_tile_number
from tiles import AnimatableTile
from random import randrange
from helpers import map_from_to, find_tile_from_position, find_nearest_passage_to_vector

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
        self.state = self.DEAD
        self.manhattan_dist_to_player = 0
        self.sound = pygame.mixer.Sound('../sfx/coin.wav')

    def live(self, dt, surface, player, passages, ghosts, ghost_follow, ghost_scared):
        self.position += (self.dir.elementwise() * dt * 0.5)
        self.grid_position = pygame.math.Vector2(math.floor(self.position.x / self.size),
                                                 math.floor(self.position.y / self.size))
        self.manhattan_dist_to_player = abs(self.grid_position.x - player.grid_position.x) + abs(
            self.grid_position.y - player.grid_position.y)
        self.move_to_target(player, passages, ghosts)
        self.set_animation()
        self.set_state(ghost_follow, ghost_scared)
        self.animate(dt)
        self.draw_path(surface)
        self.draw(surface)

    def set_state(self, ghost_follow, ghost_scared):
        # set the state this ghost is in, following or spreading decided by level, the rest by the ghost itself
        if self.state == self.DEAD:
            if self.origin.distance_to(self.grid_position) < 2:
                self.state = self.FOLLOWING
        elif ghost_scared:
            self.state = self.SCARED
        else:
            if ghost_follow:
                self.state = self.FOLLOWING
            else:
                self.state = self.SPREADING

    def search_path(self, player, passages, ghosts):
        # decide the target based on the state of the ghost, and search the path to it.
        if self.state == self.DEAD:
            target = find_nearest_passage_to_vector(self.origin, passages)
            self.a_star_search(target, passages)
        elif self.state == self.SPREADING:
            target = self.find_scatter_position(passages)
            self.a_star_search(target, passages)
        else:
            target = player

            match self.id:
                case 0:
                    # blinky
                    # pathfinds directly to the player
                    self.a_star_search(target, passages)
                case 1:
                    # pinky
                    # pathfinds 4 blocks 'in front' of the player
                    target = find_nearest_passage_to_vector(
                        player.position + (player.get_facing_direction() * 8 * tile_size), passages)

                    if target.grid_position.distance_to(self.grid_position) < 4:
                        target = find_nearest_passage_to_vector(
                            player.position + (player.get_facing_direction() * -1 * 8 * tile_size), passages)
                    self.greedy_search(target, passages)
                case 2:
                    # inky
                    # pathfinds two tiles in front, then subtract blinkys position and multiplies by 2,
                    # the adds that to blinkys position, 'sandwiching' the player
                    target = find_nearest_passage_to_vector(
                        ((player.position + player.get_facing_direction() * 2 * tile_size) - ghosts[0].position) * 2 +
                        ghosts[0].position, passages)
                    self.a_star_search(target, passages)
                case 3:
                    # pathfinds untill it is eight tiles from the player, then scatters again
                    if self.position.distance_to(player.position) > 8 * tile_size:
                        self.greedy_search(target, passages)
                    else:
                        target = self.find_scatter_position(passages)
                        self.greedy_search(target, passages)

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

    def a_star_search(self, target, passages):
        self.path = []
        for passage in passages:
            passage.reset()

        target_tile = find_tile_from_position(target.grid_position, passages)
        my_tile = find_tile_from_position(self.grid_position, passages)
        queue = [my_tile]
        visited = []

        while len(queue) > 0:
            current_node = queue.pop(0)
            if current_node != target_tile:
                if current_node not in visited:
                    visited.append(current_node)
                    neighbours = current_node.get_neighbours()
                    for next_node in neighbours:
                        if next_node not in visited and next_node:
                            old_distance = (next_node.get_distance() if next_node.get_distance() else 0)
                            next_node.set_parent(current_node)
                            new_distance = (next_node.get_distance() if next_node.get_distance() else 0)
                            new_score = new_distance + next_node.manhattan_distance(target_tile)
                            if next_node not in queue:
                                next_node.set_score(new_score)
                                bisect.insort(queue, next_node)
                            elif old_distance < new_distance:
                                next_node.set_score(new_score)
                                temp = queue.pop(queue.index(next_node))
                                bisect.insort_left(queue, temp)
            else:
                break

        current_node = target_tile.parent
        self.path.append(current_node)
        while current_node is not None and current_node != my_tile and current_node.distance != 1:
            current_node = current_node.parent
            self.path.append(current_node)

    def greedy_search(self, target, passages):
        self.path = []
        for passage in passages:
            passage.reset()

        target_tile = find_tile_from_position(target.grid_position, passages)
        my_tile = find_tile_from_position(self.grid_position, passages)
        queue = [my_tile]
        visited = []

        while len(queue) > 0:
            current_node = queue.pop(0)
            if current_node != target_tile:
                if current_node not in visited:
                    visited.append(current_node)
                    neighbours = current_node.get_neighbours()
                    for next_node in neighbours:
                        if next_node not in visited:
                            next_node.set_parent(current_node)
                            next_node.set_score(next_node.manhattan_distance(target_tile))
                            bisect.insort(queue, next_node)
            else:
                break

        current_node = target_tile.parent
        self.path.append(current_node)
        while current_node is not None and current_node != my_tile and current_node.distance != 1:
            current_node = current_node.parent
            self.path.append(current_node)

        if len(self.path) <= 0:
            self.path = None

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

    # find a random passage tile in the corner designated to this ghost
    def find_scatter_position(self, passages):
        x = (randrange(0, math.floor(horizontal_tile_number / 2 * tile_size))) if self.id % 2 == 0 else (
            randrange(math.floor(horizontal_tile_number / 2 * tile_size),
                      horizontal_tile_number * tile_size))
        y = (randrange(0, math.floor(vertical_tile_number / 2 * tile_size))) if self.id < 2 else (
            randrange(math.floor(vertical_tile_number / 2 * tile_size), vertical_tile_number * tile_size))
        return find_nearest_passage_to_vector(pygame.math.Vector2(x, y), passages)
