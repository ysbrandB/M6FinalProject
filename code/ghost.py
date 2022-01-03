import pygame
import bisect
from tiles import AnimatableTile
import pprint


class Ghost(AnimatableTile):
    def __init__(self, size, grid_position, frames, data, ghost_id, empty_tiles):
        super().__init__(size, grid_position, frames, data)
        self.dir = pygame.math.Vector2(0, 0)
        self.id = ghost_id
        sprite_row_start = ghost_id * 8
        self.frames = self.frames[sprite_row_start:sprite_row_start + 8]
        self.empty_tiles = empty_tiles
        self.animation = data['animation_left']

    def live(self, dt, surface, player):
        self.animate(dt)
        self.draw(surface)
        self.grid_position = pygame.math.Vector2(round(self.position.x / self.size), round(self.position.y / self.size))
        #self.a_star_search(player)
        # self.position+=(self.dir.elementwise()*0.001)

    # def a_star_search(self, target):
    #     target_position = Empty_element(pygame.math.Vector2(round(target.position.x / tile_size),
    #                                                         round(target.position.y / tile_size)))
    #     queue = [Empty_element(self.tile_position)]
    #     visited = []
    #
    #     while len(queue) > 0:
    #         current_node = queue.pop(0)
    #         if current_node != target_position:
    #             if current_node not in visited:
    #                 visited.append(current_node)
    #                 neighbours = self.get_neighbours(current_node)
    #                 for next_node in neighbours:
    #                     if next_node not in visited:
    #                         old_distance = (next_node.get_distance() if next_node.get_distance() else 0)
    #                         next_node.set_parent(current_node)
    #                         new_distance = (next_node.get_distance() if next_node.get_distance() else 0)
    #                         new_score = new_distance + next_node.manhattan_distance(target_position)
    #                         if next_node not in queue:
    #                             next_node.set_score(new_score)
    #                             bisect.insort(queue, next_node)
    #                         elif old_distance < new_distance:
    #                             next_node.set_score(new_score)
    #                             temp = queue.pop(queue.index(next_node))
    #                             bisect.insort_left(queue, temp)
    #         else:
    #             break
    #     if len(queue) > 0:
    #         self.set_direction(queue.pop(0))
    #
    #     for tile in self.empty_tiles:
    #         tile.reset_state()
    #
    # def get_neighbours(self, node):
    #     possible_neighbours = [node.position + pygame.math.Vector2(1, 0), node.position + pygame.math.Vector2(1, 1),
    #                            node.position + pygame.math.Vector2(0, 1), node.position + pygame.math.Vector2(0, 0)]
    #     neighbours = []
    #     for neighbour in possible_neighbours:
    #         empty = Empty_element(pygame.math.Vector2(neighbour.x, neighbour.y))
    #         if empty in self.empty_tiles:
    #             ghost_on_tile = False
    #             for ghost in self.level.ghosts:
    #                 if ghost != self:
    #                     if ghost.tile_position == neighbour:
    #                         ghost_on_tile = True
    #             if not ghost_on_tile:
    #                 neighbours.append(empty)
    #     return neighbours
    #
    # def set_direction(self, new_target):
    #     self.dir = self.position - new_target.position
