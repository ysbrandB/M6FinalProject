import pygame
from settings import tile_size as global_tile_size


class Tile:
    def __init__(self, size, grid_position):
        self.size = size
        self.grid_position = grid_position
        self.position = grid_position * global_tile_size
        self.drawable = False
        self.neighbours = []

    def __eq__(self, other):
        return self.grid_position == other.grid_position

    def find_neighbours(self, others):
        for other in others:
            if other.grid_position.distance_to(self.grid_position) == 1:
                self.neighbours.append(other)

    def remove_if_not_neighbour(self, others):
        for other in others:
            if other in self.neighbours and other.grid_position.distance_to(self.grid_position) != 1:
                self.neighbours.remove(other)


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


class PassageTile(Tile):
    def __init__(self, size, grid_position):
        super().__init__(size, grid_position)

    # even though this method exists, the passage tile is still flagged as non-drawable!
    def draw_debug_square(self, surface):
        red_square = pygame.Surface((self.size, self.size))
        red_square.fill((255, 0, 0))
        red_square.set_alpha(50)
        surface.blit(red_square, self.position)
