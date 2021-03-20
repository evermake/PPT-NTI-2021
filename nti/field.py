"""
* Make "stupid" moves

1) Clean area for the first floor. All cells and near cells (except cells that higher)
must be clear. Move all blocks preferably higher.
2)
"""
from .constants import *


def get_cell_coord(x, y, z):
    x = int(x)
    y = int(y)
    z = int(z)
    cell_x = (x - 25) // 50
    cell_y = (y - 25) // 50
    floor = z // 50
    return cell_x, cell_y, floor


def get_arch_second_cell_coord(cell_x, cell_y, rot):
    if rot == 0:
        return cell_x + 1, cell_y
    elif rot == 90:
        return cell_x, cell_y - 1
    elif rot == 180:
        return cell_x - 1, cell_y
    else:
        return cell_x, cell_y + 1


def get_block_height(block_id):
    if block_id in (BLOCK_CUBE, BLOCK_ARCH, BLOCK_QUARTER):
        return 50
    elif block_id == BLOCK_CYLINDER:
        return 100
    elif block_id == BLOCK_CONE:
        return 60
    elif block_id == BLOCK_PYRAMID:
        return 70


class Field:

    def __init__(self, blocks: list):
        self.map = self.get_map_from_blocks(blocks)

    @staticmethod
    def get_map_from_blocks(blocks):
        x = 10
        y = 12
        z = 12
        field_map = [[[None for _ in range(x)] for _ in range(y)] for _ in range(z)]

        for block in blocks:
            block_id = int(block.get('id', 1))
            block_x = int(block['x'])
            block_y = int(block['y'])
            block_z = int(block.get('z', 0))
            block_rot = int(block.get('rot', 0))
            cell_x, cell_y, floor = get_cell_coord(block_x, block_y, block_z)
            field_map[floor][cell_y][cell_x] = {
                'id': block_id,
                'rot': block_rot,
                'free': True
            }

        return field_map

    def get_block_at(self, cell_x, cell_y, floor=0, return_arch=False):
        if cell_x < 0 or cell_x > 9 or cell_y < 0 or cell_y > 11 or floor < 0 or floor > 11:
            return None
        else:
            block = self.map[floor][cell_y][cell_x]

            if not return_arch:
                return block

            if block is not None:
                return block
            else:
                # Search for arch at
                # Top
                neighbour = self.get_block_at(cell_x, cell_y + 1, floor)
                if neighbour and neighbour['id'] == BLOCK_ARCH and neighbour['rot'] == 90:
                    return neighbour
                # Right
                neighbour = self.get_block_at(cell_x + 1, cell_y, floor)
                if neighbour and neighbour['id'] == BLOCK_ARCH and neighbour['rot'] == 180:
                    return neighbour
                # Bottom
                neighbour = self.get_block_at(cell_x, cell_y - 1, floor)
                if neighbour and neighbour['id'] == BLOCK_ARCH and neighbour['rot'] == 270:
                    return neighbour
                # Left
                neighbour = self.get_block_at(cell_x - 1, cell_y, floor)
                if neighbour and neighbour['id'] == BLOCK_ARCH and neighbour['rot'] == 0:
                    return neighbour
        return None

    def get_cell_height(self, cell_x, cell_y):
        if cell_y > 11 or cell_x > 9:
            return 0
        max_height = 0
        for floor in range(12):
            b = self.get_block_at(cell_x, cell_y, floor)

            if b is not None:
                max_height = get_block_height(b['id']) + 50 * floor
            else:
                # Search for arch at
                # Top
                neighbour = self.get_block_at(cell_x, cell_y + 1, floor)
                if neighbour and neighbour['id'] == BLOCK_ARCH and neighbour['rot'] == 90:
                    max_height = get_block_height(BLOCK_ARCH) + 50 * floor
                    continue
                # Right
                neighbour = self.get_block_at(cell_x + 1, cell_y, floor)
                if neighbour and neighbour['id'] == BLOCK_ARCH and neighbour['rot'] == 180:
                    max_height = get_block_height(BLOCK_ARCH) + 50 * floor
                    continue
                # Bottom
                neighbour = self.get_block_at(cell_x, cell_y - 1, floor)
                if neighbour and neighbour['id'] == BLOCK_ARCH and neighbour['rot'] == 270:
                    max_height = get_block_height(BLOCK_ARCH) + 50 * floor
                    continue
                # Left
                neighbour = self.get_block_at(cell_x - 1, cell_y, floor)
                if neighbour and neighbour['id'] == BLOCK_ARCH and neighbour['rot'] == 0:
                    max_height = get_block_height(BLOCK_ARCH) + 50 * floor
                    continue
        return max_height

    def move_block(self, cell_from, cell_to, mark_as_busy=False):
        if len(cell_from) < 3:
            cell_from = (*cell_from, 0)
        if len(cell_to) < 3:
            cell_to = (*cell_to, 0)

        from_x, from_y, from_z = cell_from
        to_x, to_y, to_z = cell_to

        tmp = self.map[from_z][from_y][from_x]
        if tmp:
            if mark_as_busy:
                tmp['free'] = False
            self.map[to_z][to_y][to_x] = tmp
        self.map[from_z][from_y][from_x] = None

    def get_max_field_height(self):
        max_height = 0
        for cell_y in range(12):
            for cell_x in range(10):
                height = self.get_cell_height(cell_x, cell_y)
                if height > max_height:
                    max_height = height
        return max_height

    def is_cell_occupied(self, cell):
        if len(cell) < 3:
            cell = (*cell, 0)
        x, y, z = cell
        cell = self.get_block_at(x, y, z)

        if cell:
            return True
        else:
            # Search for arch at
            # Top
            neighbour = self.get_block_at(x, y + 1, z)
            if neighbour and neighbour['id'] == BLOCK_ARCH and neighbour['rot'] == 90:
                return True
            # Right
            neighbour = self.get_block_at(x + 1, y, z)
            if neighbour and neighbour['id'] == BLOCK_ARCH and neighbour['rot'] == 180:
                return True
            # Bottom
            neighbour = self.get_block_at(x, y - 1, z)
            if neighbour and neighbour['id'] == BLOCK_ARCH and neighbour['rot'] == 270:
                return True
            # Left
            neighbour = self.get_block_at(x - 1, y, z)
            if neighbour and neighbour['id'] == BLOCK_ARCH and neighbour['rot'] == 0:
                return True

    def get_blocks_on_cells(self, cells_to_check):
        blocks = set()
        for cell in cells_to_check:
            if len(cell) < 3:
                cell = (*cell, 0)

            x, y, z = cell

            block = self.get_block_at(x, y, z, return_arch=True)

            if block:
                blocks.add((block['id'], x, y))

        return list(blocks)

    def get_blocks_on_floor(self, floor):
        blocks = []

        if floor < 0:
            floor = 0
        if floor > 11:
            floor = 11
        for cell_y in range(12):
            for cell_x in range(10):
                block = self.map[floor][cell_y][cell_x]
                if block:
                    blocks.append(((cell_x, cell_y), block))
        return blocks

    def get_occupied_cells(self):
        occupied_cells = set()

        blocks = self.map[0]  # First floor
        for cell_y in range(12):
            for cell_x in range(10):
                block = blocks[cell_y][cell_x]
                if block is not None:
                    occupied_cells.add((cell_x, cell_y))

                    if block['id'] == BLOCK_ARCH:
                        occupied_cells.add(get_arch_second_cell_coord(cell_x, cell_y, block.get('rot', 0)))

        occupied_cells = list(filter(
            lambda c: 0 <= c[0] < 10 and 0 <= c[1] < 12,
            occupied_cells
        ))

        return occupied_cells

    def find_block_with_id(self, block_id, floor=0):
        for cell_y in range(12):
            for cell_x in range(10):
                block = self.map[floor][cell_y][cell_x]
                if block and block.get('free', True) and block.get('id', 0) == block_id:
                    return (cell_x, cell_y), block
        return None

    def get_spare_cell(self, cells_to_exclude=()):
        for cell_y in range(11, -1, -1):
            for cell_x in range(9, -1, -1):
                cell = cell_x, cell_y
                if not self.is_cell_occupied(cell) and cell not in cells_to_exclude:
                    return cell

    def get_height_for_move(self, x_from, x_to, y_from, y_to, block_id=BLOCK_CUBE):
        pass
