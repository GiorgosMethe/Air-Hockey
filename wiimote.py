import math

import cwiid


CWIID_BUTTONS = {"1": cwiid.BTN_1, "2": cwiid.BTN_2, 
        "-": cwiid.BTN_MINUS, "+": cwiid.BTN_PLUS,
        "A": cwiid.BTN_A, "B": cwiid.BTN_B,
        "left": cwiid.BTN_LEFT, "right": cwiid.BTN_RIGHT,
        "down": cwiid.BTN_DOWN, "up": cwiid.BTN_UP,
        "home": cwiid.BTN_HOME}


class wiimote(object):
    def __init__(self, macaddr):
        self.__wiimote = cwiid.Wiimote(macaddr)
        self.__wiimote.rpt_mode = cwiid.RPT_BTN | cwiid.RPT_ACC | cwiid.RPT_IR
        self.is_roll_corrected_pos = False

    def roll_corrected_pos(self, is_corrected):
        old_is_corrected = self.is_roll_corrected_pos
        self.is_roll_corrected_pos = is_corrected
        if self.is_roll_corrected_pos:
            acc = cwiid.RPT_ACC 
        else:
            acc = 0
        self.__wiimote.rpt_mode = cwiid.RPT_BTN | cwiid.RPT_IR | acc
        return old_is_corrected

    def get_pressed(self):
        button_state = self.__wiimote.state['buttons']
        is_pressed = {}
        for label, code in CWIID_BUTTONS:
            is_pressed['label'] = bool(button_state & code)
        return is_pressed

    def get_pos(self):
        state = self.__wiimote.state

        ir = max(filter(None, state['ir_src']), key=lambda x: x['size'])

        if not self.is_roll_corrected_pos:
            pos = ir['pos'][0] / cwiid.IR_X_MAX, ir['pos'][1] / cwiid.IR_Y_MAX
            return pos

        acc_x, acc_y, acc_z = state['acc']

        roll = math.atan(acc_x / acc_z)
        if acc_z <= 0:
            sign = 1 if acc_x > 0 else -1
            roll += math.pi * sign
        roll *= -1
        # center of view is (0,0)
        max_x = cwiid.IR_X_MAX / 2.
        max_y = cwiid.IR_Y_MAX / 2.
        c_x = ir['pos'][0] - max_x
        c_y = ir['pos'][1] - max_y
        cos_roll = math.cos(roll)
        sin_roll = math.sin(roll)

        rot_x = cos_roll*c_x - sin_roll*c_y
        rot_y = sin_roll*c_x + cos_roll*c_y
        rot_max_x = cos_roll*max_x - sin_roll*max_y
        rot_max_y = sin_roll*max_x + cos_roll*max_y

        pos = (rot_x + rot_max_x) / rot_max_x, (rot_y + rot_max_y) / rot_max_y
        return pos

    def get_rel(self):
        new_pos = self.get_pos()
        rel_x = self.old_pos[0] - new_pos[0]
        rel_y = self.old_pos[1] - new_pos[1]
        self.old_pos = new_pos
        return rel_x, rel_y

    def set_pos(self):
        """ Only provided to implement complete pygame.mouse interface.
        
        Because it does not control a cursor, this has no semantics in this
        case.
        """
        raise RuntimeError("Not appropriate for a Wiimote")

    def set_visible(self, is_visible):
        """ Only provided to implement complete pygame.mouse interface.
        
        Because it does not control a cursor, this has no semantics in this
        case.
        """
        raise RuntimeError("Not appropriate for a Wiimote")

    def get_focused(self):
        return True

    def set_cursor(self, size, hotspot, xormasks, andmasks):
        """ Only provided to implement complete pygame.mouse interface.
        
        Because it does not control a cursor, this has no semantics in this
        case.
        """
        raise RuntimeError("Not appropriate for a Wiimote")

    def get_cursor(self):
        """ Only provided to implement complete pygame.mouse interface.
        
        Because it does not control a cursor, this has no semantics in this
        case.
        """
        raise RuntimeError("Not appropriate for a Wiimote")
