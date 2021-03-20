from .constants import *
from .field import get_block_height


def get_cell_coord(cell_x, cell_y):
    x = 25 + cell_x * 50
    y = 25 + cell_y * 50
    return x, y


class Robot:
    MAGNET_SIGNAL_NUM = 10
    ORIGIN_POSE_NAME = 'origin_pose'
    ORIGIN_POSE_Z_OFFSET = 50

    def __init__(self, speed=250, accuracy=0.5, debug=False):
        self.commands_stack = []
        self.debug = debug

        self.set_speed(speed)
        self.set_accuracy(accuracy)

        self.disable_magnet()
        self._save_origin()

    def cmd(self, command):
        self.commands_stack.append(command)

    def _save_origin(self):
        self.wait_stop()
        self.cmd('HERE %s' % self.ORIGIN_POSE_NAME)

    def set_speed(self, speed, always=True):
        """Sets robot speed in mm/s."""
        self.cmd(f"SPEED {speed} MM/S{' ALWAYS' if always else ''}")

    def set_accuracy(self, accuracy, always=True):
        """Sets robot accuracy."""
        self.cmd(f'ACCURACY {accuracy}' + (' ALWAYS' if always else ''))

    def sleep(self, seconds):
        self.cmd(F'TWAIT {seconds}')

    def wait_stop(self):
        self.cmd('BREAK')

    def toggle_magnet(self, state: bool, wait=True):
        if wait:
            self.wait_stop()
        if self.debug:
            self.cmd('CLOSEI' if state else 'OPENI')
        sign = '' if state else '-'
        self.cmd(f'SIGNAL {sign}{self.MAGNET_SIGNAL_NUM}')

    def enable_magnet(self):
        self.toggle_magnet(True)

    def disable_magnet(self):
        self.toggle_magnet(False)

    def move_to_origin(self):
        self.cmd(f'JMOVE {self.ORIGIN_POSE_NAME}')

    def move_to(self, x=None, y=None, z=None, speed=None, method='J'):
        if method not in ('J', 'L'):
            method = 'J'
        if x is None or y is None or z is None:
            if z is not None:
                z -= 50
            self.wait_stop()
            self.cmd('HERE tmp')
            shift = f'{"" if x is None else x}, {"" if y is None else y}, {"" if z is None else z}'
            self.cmd(
                f'POINT dist = SHIFT({self.ORIGIN_POSE_NAME} BY {shift})'
            )
            if x is None:
                self.cmd('POINT/X dist = tmp')
            if y is None:
                self.cmd('POINT/Y dist = tmp')
            if z is None:
                self.cmd('POINT/Z dist = tmp')

            if speed:
                self.set_speed(speed, always=False)
            self.cmd(f'{method}MOVE dist')
        else:
            z -= 50
            if speed:
                self.set_speed(speed, always=False)
            self.cmd(f'{method}MOVE SHIFT({self.ORIGIN_POSE_NAME} BY {x}, {y}, {z})')

    def move_to_cell(self, cell_x, cell_y, cell_z=None, speed=None, method='J'):
        x, y = get_cell_coord(cell_x, cell_y)
        if cell_z:
            z = cell_z * 50
        else:
            z = None
        self.move_to(x, y, z, speed, method)

    def move_block(self, from_cell, to_cell, safety_height=200, block_id=BLOCK_CUBE, rotate_block=None):
        block_height = get_block_height(block_id)

        if len(to_cell) < 3:
            to_cell = (*to_cell, 0)

        from_x, from_y = from_cell[0], from_cell[1]
        to_x, to_y, to_z = to_cell

        self.move_to(z=safety_height)
        self.move_to_cell(from_x, from_y)

        # Pick up
        self.move_to(z=block_height + 30, speed=200)
        self.move_to(z=block_height, speed=20)
        self.enable_magnet()
        self.move_to(z=block_height + 30, speed=25)
        self.move_to(z=safety_height + block_height)

        # Move to dist
        self.move_to_cell(to_x, to_y)

        # Rotate, if necessary
        if rotate_block:
            self.wait_stop()
            self.cmd('HERE tmp_rot')

            self.cmd(F'POINT {self.ORIGIN_POSE_NAME} = {self.ORIGIN_POSE_NAME} - TRANS(0,0,0,0,0,{-rotate_block})')
            self.cmd(F'POINT tmp_rot = tmp_rot - TRANS(0,0,0,0,0,{-rotate_block})')

            self.cmd(f'JMOVE tmp_rot')

        # Put down
        self.move_to(z=to_z * 50 + block_height + 30, speed=200)
        self.move_to(z=to_z * 50 + block_height, speed=20)
        self.disable_magnet()
        self.move_to(z=to_z * 50 + block_height + 30, speed=25)
        self.move_to(z=safety_height)

        # Rotate back, if necessary
        if rotate_block:
            self.wait_stop()
            self.cmd('HERE tmp_rot')

            self.cmd(F'POINT {self.ORIGIN_POSE_NAME} = {self.ORIGIN_POSE_NAME} - TRANS(0,0,0,0,0,{rotate_block})')
            self.cmd(F'POINT tmp_rot = tmp_rot - TRANS(0,0,0,0,0,{rotate_block})')

            self.cmd(f'JMOVE tmp_rot')

    def export_as_code(self, filename='program.as'):
        body = '\n  '.join(self.commands_stack)

        result = '.PROGRAM main()\n  ' + body + '\n.END'

        with open(filename, 'w') as f:
            f.write(result)
