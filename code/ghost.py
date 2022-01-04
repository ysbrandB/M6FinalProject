import math

import pygame
import bisect
from tiles import AnimatableTile

def find_tile_from_position(position, passages):
    for passage in passages:
        if position == passage.grid_position:
            return passage


def highlight_path(target, surface, my_tile):
    # print(f"Path length is: {target.distance}")
    current_node = target.parent
    while current_node is not None and current_node != my_tile:
        current_node.draw_debug_square(surface, (255, 0, 0))
        current_node = current_node.parent


class Ghost(AnimatableTile):
    def __init__(self, size, grid_position, frames, data, ghost_id):
        super().__init__(size, grid_position, frames, data)
        self.dir = pygame.math.Vector2(0, 0)
        self.id = ghost_id
        sprite_row_start = ghost_id * 8
        self.frames = self.frames[sprite_row_start:sprite_row_start + 8]
        self.animation = data['animation_left']
        self.target = None

    def live(self, dt, surface, player, passages):
        self.grid_position = pygame.math.Vector2(round(self.position.x / self.size), round(self.position.y / self.size))
        self.position += (self.dir.elementwise() * 0.1)
        self.move_to_target(player, passages, surface)
        self.animate(dt)
        self.draw(surface)

    def move_to_target(self, player, passages, surface):
        if self.target is None:
            match self.id:
                case 0:
                    self.a_star_search(player, passages, surface)
                    self.dir = self.target.grid_position - self.grid_position
                case 1:
                    self.greedy_search(player, passages, surface)
                    self.dir = self.target.grid_position - self.grid_position
                case 2:
                    self.depth_search(player, passages, surface)
                    self.dir = self.target.grid_position - self.grid_position
                case 3:
                    self.breadth_first(player, passages, surface)
                    self.dir = self.target.grid_position - self.grid_position

        if (self.target is not None):
            if (math.dist(self.target.get_center(), self.get_center())) < 1:
                self.set_center(self.target.get_center())
                self.dir = pygame.math.Vector2(0, 0)
                self.target = None

    def set_center(self, center):
        self.position = pygame.math.Vector2(center.x - self.size / 2, center.y - self.size / 2)

    def a_star_search(self, target, passages, surface):
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
        while current_node is not None and current_node != my_tile and current_node.distance != 1:
            current_node = current_node.parent

        self.target = current_node

        highlight_path(target_tile, surface, my_tile)
        # print(f"The number of visited nodes is: {len(visited)}")

    def greedy_search(self, target, passages, surface):

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
        while current_node is not None and current_node != my_tile and current_node.distance != 1:
            current_node = current_node.parent

        self.target = current_node

        current_node.draw_debug_square(surface, (0, 255, 0))
        highlight_path(target_tile, surface, my_tile)

    def depth_search(self, target, passages, surface):
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
                    for next_node in neighbours:
                        if next_node not in visited:
                            next_node.set_parent(current_node)
                            stack.append(next_node)
            else:
                break

        current_node = target_tile.parent
        while current_node is not None and current_node != my_tile and current_node.distance != 1:
            current_node = current_node.parent

        self.target = current_node

        highlight_path(target_tile, surface, my_tile)

    def breadth_first(self, target, passages, surface):

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
                    # random.shuffle(neighbours)
                    for next_node in neighbours:
                        if next_node not in visited:
                            next_node.set_parent(current_node)
                            queue.append(next_node)
            else:
                break

        current_node = target_tile.parent
        while current_node is not None and current_node != my_tile and current_node.distance != 1:
            current_node = current_node.parent

        self.target = current_node

        highlight_path(target_tile, surface, my_tile)