from helpers import import_cut_graphics
from game_data import ghosts
from settings import tile_size, vertical_tile_number, horizontal_tile_number
import pygame
import bisect
from empty_path_element import Empty_element
import pprint


class Ghost:
    def __init__(self, x, y, level, value, empty_tiles):
        self.dir = pygame.math.Vector2(0, 0)
        self.value = value % 8
        self.sprites = import_cut_graphics(ghosts['sprite_sheet_path'])
        sprite_row_start = int(value / 7) * 8
        self.sprites = self.sprites[sprite_row_start:sprite_row_start + 8]
        self.position = pygame.Vector2(x, y)
        self.surface = level.display_surface
        self.level = level
        self.animation = ghosts["animation_left"]
        self.frame_index = 0
        self.frame_time = 0
        self.tile_position = pygame.math.Vector2(round(self.position.x / tile_size), round(self.position.y / tile_size))
        self.empty_tiles = empty_tiles

    def draw(self, dt):
        # reminder that dt has already been multiplied by 0.1, therefore we multiply by 0.01 to get seconds
        self.frame_time += dt * 0.01
        if self.frame_time >= 1 / self.animation['fps']:
            self.frame_time = 0
            self.frame_index += 1
            if self.frame_index > len(self.animation['frames']) - 1:
                self.frame_index = 0

        sprite = self.sprites[self.animation['frames'][self.frame_index]]
        self.surface.blit(sprite, (self.position.x, self.position.y))

    def update(self, dt):
        self.draw(dt)
        self.tile_position = pygame.math.Vector2(round(self.position.x / tile_size), round(self.position.y / tile_size))
        self.a_star_search(self.level.player)
        self.position+=(self.dir.elementwise()*0.001)

    def a_star_search(self, target):
        target_position = Empty_element(pygame.math.Vector2(round(target.position.x / tile_size),
                                                            round(target.position.y / tile_size)))
        queue = [Empty_element(self.tile_position)]
        visited = []

        while len(queue) > 0:
            current_node = queue.pop(0)
            if current_node != target_position:
                if current_node not in visited:
                    visited.append(current_node)
                    neighbours = self.get_neighbours(current_node)
                    for next_node in neighbours:
                        if next_node not in visited:
                            old_distance = (next_node.get_distance() if next_node.get_distance() else 0)
                            next_node.set_parent(current_node)
                            new_distance = (next_node.get_distance() if next_node.get_distance() else 0)
                            new_score = new_distance + next_node.manhattan_distance(target_position)
                            if next_node not in queue:
                                next_node.set_score(new_score)
                                bisect.insort(queue, next_node)
                            elif old_distance < new_distance:
                                next_node.set_score(new_score)
                                temp = queue.pop(queue.index(next_node))
                                bisect.insort_left(queue, temp)
            else:
                break
        if len(queue)>0:
            self.set_direction(queue.pop(0))

        for tile in self.empty_tiles:
            tile.reset_state()

    def get_neighbours(self, node):
        possible_neighbours = [node.position + pygame.math.Vector2(1, 0), node.position + pygame.math.Vector2(1, 1),
                               node.position + pygame.math.Vector2(0, 1), node.position + pygame.math.Vector2(0, 0)]
        neighbours = []
        for neighbour in possible_neighbours:
            empty = Empty_element(pygame.math.Vector2(neighbour.x, neighbour.y))
            if empty in self.empty_tiles:
                ghost_on_tile = False
                for ghost in self.level.ghosts:
                    if ghost != self:
                        if ghost.tile_position == neighbour:
                            ghost_on_tile = True
                if not ghost_on_tile:
                    neighbours.append(empty)
        return neighbours

    def set_direction(self, new_target):
        self.dir= self.position-new_target.position
