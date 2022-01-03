# This class is largely inspired by grid_element from the tutorial week 6
import math
import pygame
class Empty_element:
    def __init__(self, position):
        self.position = pygame.math.Vector2(position.x, position.y)
        self.neighbours = []
        self.parent = None
        self.distance = None
        self.score = None

    def __lt__(self, other):
        return (self.score is not None) and (other.score is None or self.score < other.score)

    def __hash__(self):
        return hash((self.position.x, self.position.y))

    def __repr__(self):
        return "[%s, %s]" % (self.position, self.score)

    def reset_neighbours(self):
        self.neighbours = []

    def reset_state(self):
        self.parent = None
        self.score = None
        self.distance = None

    def get_neighbours(self):
        return self.neighbours[:]

    def manhattan_distance(self, other):
        x_distance = abs(self.position.x - other.position.x)
        y_distance = abs(self.position.y - other.position.y)
        return x_distance + y_distance

    def eucladian_distance(self, other):
        x_distance = abs(self.position.x - other.position.x)
        y_distance = abs(self.position.y - other.position.y)
        return math.sqrt(x_distance**2+y_distance**2)

    def set_score(self, score):
        self.score = score

    def set_distance(self, distance):
        self.distance = distance

    def get_distance(self):
        return self.distance

    def get_score(self, score):
        return self.score

    def get_position(self):
        return self.position

    def set_parent(self, parent):
        self.parent = parent
        if parent.distance is not None:
            self.distance = parent.distance+1

