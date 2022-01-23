from tiles import StaticTile
from settings import tile_size


class PipeHead(StaticTile):
    def __init__(self, size, grid_position, image, flags):
        super().__init__(size, grid_position, image, flags)
