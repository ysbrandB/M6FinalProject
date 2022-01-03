import pygame
import bisect
from tiles import AnimatableTile
import pprint


class Ghost(AnimatableTile):
    def __init__(self, size, grid_position, frames, data, ghost_id):
        super().__init__(size, grid_position, frames, data)
        self.dir = pygame.math.Vector2(0, 0)
        self.id = ghost_id
        sprite_row_start = ghost_id * 8
        self.frames = self.frames[sprite_row_start:sprite_row_start + 8]
        self.animation = data['animation_left']

    def live(self, dt, surface, player, passages):
        self.animate(dt)
        self.draw(surface)
        self.grid_position = pygame.math.Vector2(round(self.position.x / self.size), round(self.position.y / self.size))
        # self.a_star_search(player, passages, surface)
        # self.position+=(self.dir.elementwise()*0.001)

    def a_star_search(self, target, passages, surface):
        for passage in passages:
            passage.reset()

        targetTile=
        queue = [self.graph.start]
        visited = []

        while len(queue) > 0:
            current_node = queue.pop(0)
            if current_node != self.graph.target:
                if current_node not in visited:
                    visited.append(current_node)
                    neighbours = current_node.get_neighbours()
                    for next_node in neighbours:
                        if next_node not in visited:
                            old_distance = (next_node.get_distance() if next_node.get_distance() else 0)
                            next_node.set_parent(current_node)
                            new_distance = (next_node.get_distance() if next_node.get_distance() else 0)
                            new_score = new_distance + next_node.manhattan_distance(self.graph.target)
                            if (next_node not in queue):
                                next_node.set_score(new_score)
                                bisect.insort(queue, next_node)
                            elif (old_distance < new_distance):
                                next_node.set_score(new_score)
                                temp = queue.pop(queue.index(next_node))
                                bisect.insort_left(queue, temp)
            else:
                break
        print("The number of visited nodes is: {}".format(len(visited)))
        self.highlight_path(target, surface)

    def highlight_path(self, target, surface):
        # Compute the path, back to front.
        current_node = target.parent

        while current_node is not None and current_node != self.graph.start:
            current_node.draw_debug_square(surface)
            current_node = current_node.parent

        print("Path length is: {}".format(self.graph.target.distance))
