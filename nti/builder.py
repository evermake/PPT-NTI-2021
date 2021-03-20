from nti.robot import Robot
from nti.field import Field


def clear_cells(robot: Robot, field: Field, cells):
    blocks_to_clear = field.get_blocks_on_cells(cells)
    safety_height = field.get_max_field_height() + 100

    for block in blocks_to_clear:
        block = {'id': block[0], 'x': block[1], 'y': block[2]}
        cell_from = (block['x'], block['y'])
        cell_to = field.get_spare_cell(cells)
        robot.move_block(cell_from, cell_to, safety_height, block['id'])
        field.move_block(cell_from, cell_to)


def place_blocks(robot: Robot, work_field: Field, plan_field: Field):
    for floor in range(12):
        blocks_to_place = plan_field.get_blocks_on_floor(floor)
        for cell_to, block in blocks_to_place:
            block_id = block['id']
            block_rot = block['rot']
            found_block = work_field.find_block_with_id(block_id)
            if found_block:
                cell_from, found_block = found_block
                safety_height = work_field.get_max_field_height() + 100
                cell_to = (cell_to[0], cell_to[1], floor)

                rotate = block_rot - found_block.get('rot', block_rot)

                robot.move_block(cell_from, cell_to, safety_height, block_id, rotate_block=rotate)
                work_field.move_block(cell_from, cell_to, mark_as_busy=True)


def build_building(initial_blocks, required_blocks, debug=False):
    initial_field = Field(initial_blocks)
    required_field = Field(required_blocks)
    r = Robot(debug=debug)

    cells_for_building = required_field.get_occupied_cells()
    clear_cells(r, initial_field, cells_for_building)
    place_blocks(r, initial_field, required_field)
    r.move_to(0, 0, speed=150)
    r.move_to_origin()
    r.export_as_code()
