import pygame
from settings import tile_size as global_tile_size


class Tile:
    def __init__(self, size, grid_position):
        self.size = size
        self.grid_position = grid_position
        self.position = grid_position * global_tile_size
        self.drawable = False
        self.static = False
        self.neighbours = []

    def __eq__(self, other):
        return self.grid_position == other.grid_position

    def __repr__(self):
        return f"{self.position, self.grid_position}"


    def find_neighbours(self, others):
        for other in others:
            if other.grid_position.distance_to(self.grid_position) == 1:
                self.neighbours.append(other)

    def remove_if_not_neighbour(self, others):
        for other in others:
            if other in self.neighbours and other.grid_position.distance_to(self.grid_position) != 1:
                self.neighbours.remove(other)

    def get_center(self):
        return pygame.Vector2(self.position.x + self.size / 2, self.position.y + self.size / 2)


class SpriteTile(Tile):
    def __init__(self, size, grid_position, image):
        super().__init__(size, grid_position)
        self.image = image
        self.drawable = True

    def draw(self, surface):
        surface.blit(self.image, self.position)


class AnimatableTile(SpriteTile):
    def __init__(self, size, grid_position, frames, data):
        super().__init__(size, grid_position, frames[0])
        self.frames = frames
        self.frame_index = 0
        self.frame_time = 0
        self.animation = data['animation_idle']
        self.data = data

    def animate(self, dt):
        # reminder that dt has already been multiplied by 0.1, therefore we multiply by 0.01 to get seconds
        self.frame_time += dt * 0.01
        if self.frame_time >= 1 / self.animation['fps']:
            self.frame_time = 0
            self.frame_index += 1
            if self.frame_index > len(self.animation['frames']) - 1:
                self.frame_index = 0
        self.image = self.get_current_sprite()

    def get_current_sprite(self):
        return self.frames[self.animation['frames'][self.frame_index]]


class StaticTile(SpriteTile):
    def __init__(self, size, grid_position, image, flags):
        super().__init__(size, grid_position, image)
        self.flags = flags
        # flips and rotations
        flip_horizontal = bool(flags & 0b1000)
        flip_vertical = bool(flags & 0b0100)
        rotate = bool(flags & 0b0010)
        self.image = pygame.transform.rotate(self.image, -90 * rotate)
        self.image = pygame.transform.flip(self.image, flip_horizontal != rotate, flip_vertical)
        self.static = True


class PassageTile(Tile):
    def __init__(self, size, grid_position):
        super().__init__(size, grid_position)
        self.parent = None
        self.score = None
        self.distance = None

    def __lt__(self, other):
        return (self.score is not None) and (other.score is None or self.score < other.score)

    def reset(self):
        self.parent = None
        self.score = None
        self.distance = None

    def get_neighbours(self):
        return self.neighbours[:]

    def get_distance(self):
        return self.distance

    def set_parent(self, parent):
        self.parent = parent
        if parent.distance is not None:
            self.distance = parent.distance + 1
        else:
            self.distance = 1

    def set_score(self, score):
        self.score = score

    def manhattan_distance(self, other):
        x_distance = abs(self.position.x - other.position.x)
        y_distance = abs(self.position.y - other.position.y)
        return x_distance + y_distance

    # even though this method exists, the passage tile is still flagged as non-drawable!
    def draw_debug_square(self, surface, color, alpha):
        square = pygame.Surface((self.size, self.size))
        square.fill(color)
        square.set_alpha(alpha)
        surface.blit(square, self.position)
