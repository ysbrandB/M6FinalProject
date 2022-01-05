import bisect
import math
import pygame

from settings import ghost_tiles_to_follow
from tiles import AnimatableTile
import random
from helpers import map_from_to, find_tile_from_position


class Ghost(AnimatableTile):
    def __init__(self, size, grid_position, frames, data, ghost_id):
        super().__init__(size, grid_position, frames, data)
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
        self.state_timer = data['seconds_following']
        self.manhattan_dist_to_player = 0
        self.sound = pygame.mixer.Sound('../sfx/coin.wav')

    def live(self, dt, surface, player, passages):
        self.position += (self.dir.elementwise() * dt * 0.5)
        self.grid_position = pygame.math.Vector2(math.floor(self.position.x / self.size),
                                                 math.floor(self.position.y / self.size))
        self.manhattan_dist_to_player = int(
            abs(self.grid_position.x - player.grid_position.x) + abs(self.grid_position.y - player.grid_position.y))
        self.move_to_target(player, passages)
        self.set_animation()
        self.set_state(dt)
        self.animate(dt)
        self.draw_path(surface)
        self.draw(surface)

    def set_state(self, dt):
        self.state_timer -= dt / 100
        if self.state_timer <= 0:
            match self.state:
                case self.FOLLOWING:
                    self.state = self.SPREADING
                    self.state_timer = self.data['seconds_spreading']
                case self.SPREADING:
                    self.state = self.SCARED
                    self.state_timer = self.data['seconds_following']
                case self.DEAD:
                    if self.grid_position == self.origin:
                        self.state = self.FOLLOWING
                        self.state_timer = self.data['seconds_following']

    def search_path(self, player, passages):
        if self.state == self.DEAD:
            target = find_tile_from_position(self.origin, passages)
        elif self.state == self.SPREADING:
            quarterly_split = math.floor(len(passages) / 4)
            quarter = passages[quarterly_split * self.id:quarterly_split * (self.id + 1)]
            target = random.choice(quarter)
        else:
            target = player

        if self.id % 2 == 0:
            self.a_star_search(target, passages)
        else:
            self.greedy_search(target, passages)

    def move_to_target(self, player, passages):
        if self.path is None or self.tiles_followed >= ghost_tiles_to_follow:
            self.search_path(player, passages)
            self.tiles_followed = 0

        elif self.target is None and len(self.path) > 0:
            self.tiles_followed += 1
            self.target = self.path.pop()
            if self.target:
                if self.target.grid_position and self.grid_position:
                    self.dir = self.target.grid_position - self.grid_position

        elif self.target is not None:
            if (math.dist(self.target.get_center(), self.get_center())) < 1:
                self.tiles_followed += 1
                self.set_center(self.target.get_center())
                self.dir = pygame.math.Vector2(0, 0)
                self.target = None

        elif len(self.path) <= 0:
            self.search_path(player, passages)

    def set_center(self, center):
        self.position = pygame.math.Vector2(center.x - self.size / 2, center.y - self.size / 2)

    def set_animation(self):
        if self.state is self.SCARED:
            if self.id % 2 == 0:
                self.animation = self.data['animation_scared']
            else:
                self.animation = self.data['animation_scared_white']

        elif self.state == self.DEAD:
            match self.dir.x:
                case 1:
                    self.animation = self.data['animation_dead_left']
                case -1:
                    self.animation = self.data['animation_dead_right']

            match self.dir.y:
                case 1:
                    self.animation = self.data['animation_dead_up']
                case -1:
                    self.animation = self.data['animation_dead_down']
        else:
            match self.dir.x:
                case 1:
                    self.animation = self.data['animation_right']
                case -1:
                    self.animation = self.data['animation_left']

            match self.dir.y:
                case 1:
                    self.animation = self.data['animation_down']
                case -1:
                    self.animation = self.data['animation_up']

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

        if len(self.path) <= 2:
            self.path = None

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

    # def depth_search(self, target, passages):
    #     self.path = []
    #     for passage in passages:
    #         passage.reset()
    #
    #     target_tile = find_tile_from_position(target.grid_position, passages)
    #     my_tile = find_tile_from_position(self.grid_position, passages)
    #     stack = [my_tile]
    #     visited = []
    #
    #     while len(stack) > 0:
    #         current_node = stack.pop()
    #         if current_node != target_tile:
    #             if current_node not in visited:
    #                 visited.append(current_node)
    #                 neighbours = current_node.get_neighbours()
    #                 # random.shuffle(neighbours)
    #                 for next_node in neighbours:
    #                     if next_node not in visited:
    #                         next_node.set_parent(current_node)
    #                         stack.append(next_node)
    #         else:
    #             break
    #
    #     current_node = target_tile.parent
    #     self.path.append(current_node)
    #     while current_node is not None and current_node != my_tile and current_node.distance != 1:
    #         current_node = current_node.parent
    #         self.path.append(current_node)
    #
    #     if len(self.path) <= 0:
    #         self.path = None

    def draw_path(self, surface):
        if self.path:
            for index, tile in enumerate(self.path):
                if tile:
                    tile.draw_debug_square(surface, (
                        map_from_to(self.id, 0, 4, 0, 255), map_from_to(self.id, 0, 4, 255, 0),
                        map_from_to(self.id, 0, 4, 0, 255)),
                                           map_from_to(index, 0, len(self.path), 0, 255))

    def die(self):
        self.state = self.DEAD
        self.state_timer = float('inf')
