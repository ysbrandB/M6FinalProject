import bisect
import math
import random

import pygame

from settings import ghost_tiles_to_follow
from tiles import AnimatableTile


def mapFromTo(x, a, b, c, d):
    return (x - a) / (b - a) * (d - c) + c


def find_tile_from_position(position, passages):
    for passage in passages:
        if position == passage.grid_position:
            return passage


class Ghost(AnimatableTile):
    def __init__(self, size, grid_position, frames, data, ghost_id):
        super().__init__(size, grid_position, frames, data)
        self.dir = pygame.math.Vector2(0, 0)
        self.id = ghost_id
        sprite_row_start = ghost_id * 8
        self.frames = self.frames[sprite_row_start:sprite_row_start + 8]
        self.animation = data['animation_left']
        self.target = None
        self.path = None
        self.tiles_followed = 0

    def live(self, dt, surface, player, passages):
        self.grid_position = pygame.math.Vector2(round(self.position.x / self.size), round(self.position.y / self.size))
        self.position += (self.dir.elementwise() * dt * 0.5)
        self.move_to_target(player, passages, surface)
        self.set_animation()
        self.animate(dt)
        self.draw_path(surface)
        self.draw(surface)

    def move_to_target(self, player, passages, surface):
        if self.path is None:
            self.search_path(player, passages, surface)

        elif self.target is None and self.path:
            if self.tiles_followed < ghost_tiles_to_follow:
                self.tiles_followed += 1
                self.target = self.path.pop()

            elif self.tiles_followed >= ghost_tiles_to_follow:
                self.search_path(player, passages, surface)
                self.tiles_followed = 0

            if self.target is not None:
                self.dir = self.target.grid_position - self.grid_position

        else:
            if self.target is not None:
                if (math.dist(self.target.get_center(), self.get_center())) < 1:
                    self.set_center(self.target.get_center())
                    self.dir = pygame.math.Vector2(0, 0)
                    self.target = None

    def search_path(self, player, passages, surface):
        match self.id:
            case 0:
                self.a_star_search(player, passages, surface)
            case 1:
                self.greedy_search(player, passages, surface)
            case 2:
                self.depth_search(player, passages, surface)
            case 3:
                self.a_star_search(player, passages, surface)

    def set_center(self, center):
        self.position = pygame.math.Vector2(center.x - self.size / 2, center.y - self.size / 2)

    def set_animation(self):
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

    def a_star_search(self, target, passages, surface):
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

        # highlight_path(target_tile, surface, my_tile)

    def greedy_search(self, target, passages, surface):
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

        # highlight_path(target_tile, surface, my_tile)

    def depth_search(self, target, passages, surface):
        self.path = []
        for passage in passages:
            passage.reset()

        target_tile = find_tile_from_position(target.grid_position, passages)
        my_tile = find_tile_from_position(self.grid_position, passages)
        stack = [my_tile]
        visited = []

        while len(stack) > 0:
            current_node = stack.pop()
            if current_node != target_tile:
                if current_node not in visited:
                    visited.append(current_node)
                    neighbours = current_node.get_neighbours()
                    # random.shuffle(neighbours)
                    for next_node in neighbours:
                        if next_node not in visited:
                            next_node.set_parent(current_node)
                            stack.append(next_node)
            else:
                break

        current_node = target_tile.parent
        self.path.append(current_node)
        while current_node is not None and current_node != my_tile and current_node.distance != 1:
            current_node = current_node.parent
            self.path.append(current_node)

    def draw_path(self, surface):
        for index, tile in enumerate(self.path):
            if tile:
                tile.draw_debug_square(surface, (
                    mapFromTo(self.id, 0, 4, 0, 255), mapFromTo(self.id, 0, 4, 0, 255),
                    mapFromTo(self.id, 0, 4, 0, 255)),
                                       mapFromTo(index, 0, len(self.path), 0, 255))
