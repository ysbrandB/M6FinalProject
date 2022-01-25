from csv import reader
from settings import tile_size
from math import sqrt
import pygame
import bisect


def import_csv_layout(path):
    terrain_map = []
    with open(path) as parsed_map:
        level = reader(parsed_map, delimiter=',')
        for row in level:
            terrain_map.append(list(row))
        return terrain_map


def import_cut_graphics(path):
    surface = pygame.image.load(path).convert_alpha()
    tile_num_x = int(surface.get_size()[0] / tile_size)
    tile_num_y = int(surface.get_size()[1] / tile_size)
    cut_tiles = []
    for row in range(tile_num_y):
        for col in range(tile_num_x):
            x = col * tile_size
            y = row * tile_size
            new_surface = pygame.Surface((tile_size, tile_size), pygame.SRCALPHA)
            new_surface.blit(surface, (0, 0), pygame.Rect(x, y, tile_size, tile_size))
            cut_tiles.append(new_surface)
    return cut_tiles


def map_from_to(x, a, b, c, d):
    mapped = (x - a) / (b - a) * (d - c) + c
    return mapped


def find_tile_from_grid_position(grid_position, passages):
    found_position=None
    for passage in passages:
        if grid_position == passage.grid_position:
            found_position = passage
    if found_position:
        return found_position
    else:
        nearest_passage = passages[0]
        nearest_distance = float('inf')
        for passage in passages:
            if grid_position.distance_to(passage.grid_position) < nearest_distance:
                nearest_passage = passage
                nearest_distance = grid_position.distance_to(passage.grid_position) < nearest_distance
        return nearest_passage


def find_nearest_passage_to_vector(target_position, passages):
    nearest_passage = passages[0]
    nearest_distance = float('inf')
    for passage in passages:
        if target_position.distance_to(passage.position) < nearest_distance:
            nearest_passage = passage
            nearest_distance = target_position.distance_to(passage.position)
    return nearest_passage


def a_star_search(target, passages, grid_position):
    path = []
    for passage in passages:
        passage.reset()

    target_tile = find_tile_from_grid_position(target.grid_position, passages)
    my_tile = find_tile_from_grid_position(grid_position, passages)
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
    path.append(current_node)
    while current_node is not None and current_node != my_tile and current_node.distance != 1:
        current_node = current_node.parent
        path.append(current_node)
    return path


def greedy_search(target, passages, grid_position):
    path = []
    for passage in passages:
        passage.reset()

    target_tile = find_tile_from_grid_position(target.grid_position, passages)
    my_tile = find_tile_from_grid_position(grid_position, passages)
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
    path.append(current_node)
    while current_node is not None and current_node != my_tile and current_node.distance != 1:
        current_node = current_node.parent
        path.append(current_node)

    if len(path) <= 0:
        path = None

    return path

def get_points_distance(points):
    total = 0
    for i in range(1, len(points)):
        x_dif = points[i].x - points[i - 1].x
        y_dif = points[i].y - points[i - 1].y
        total += sqrt(x_dif ** 2 + y_dif ** 2)
    return total