import math

import cwiid
import pygame


CWIID_BUTTONS = {"1": cwiid.BTN_1, "2": cwiid.BTN_2, 
        "-": cwiid.BTN_MINUS, "+": cwiid.BTN_PLUS,
        "A": cwiid.BTN_A, "B": cwiid.BTN_B,
        "left": cwiid.BTN_LEFT, "right": cwiid.BTN_RIGHT,
        "down": cwiid.BTN_DOWN, "up": cwiid.BTN_UP,
        "home": cwiid.BTN_HOME}


class wiimote(object):
    IR_X_MAX = float(cwiid.IR_X_MAX)
    IR_Y_MAX = float(cwiid.IR_Y_MAX)

    def __init__(self, macaddr):
        self.__wiimote = cwiid.Wiimote(macaddr)
        self.__wiimote.rpt_mode = cwiid.RPT_BTN | cwiid.RPT_ACC | cwiid.RPT_IR
        self.is_roll_corrected_pos = False
        # for get_rel's history
        self.rel_old_pos = (0, 0) 
        # for getl_pos's history, when no LED is seen
        self.pos_old_pos = (0, 0, False) 

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

        try:
            ir = max(filter(None, state['ir_src']), key=lambda x: x['size'])
        except ValueError:
            return self.pos_old_pos

        if not self.is_roll_corrected_pos:
            pos = 1 - ir['pos'][0] / self.IR_X_MAX, ir['pos'][1] / self.IR_Y_MAX
        else:
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
        self.pos_old_pos = pos[0], pos[1], False
        return pos[0], pos[1], True
        return pos

    def get_rel(self):
        new_pos = self.get_pos()
        rel_x = self.rel_old_pos[0] - new_pos[0]
        rel_y = self.rel_old_pos[1] - new_pos[1]
        self.rel_old_pos = new_pos
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

if __name__ == "__main__":
    raw_input("Press 1+2 on the Wiimote to connect; then press Enter")
    wm = wiimote("00:25:A0:B3:00:EB")
    print "Connected!"
    pygame.init()
    screen = pygame.display.set_mode((400,400))
    #screen = pygame.display.get_surface()
    black = (0, 0, 0)
    white = (255, 255, 255)
    while True:
        pos = wm.get_pos()
        if not pos[2]:
            continue
        pos = (int(400. * pos[0]), int(400. * pos[1]))
        print pos
        screen.fill(black)
        pygame.draw.circle(screen, white, pos, 3, 2)
        pygame.display.update()
        if pygame.event.get(pygame.QUIT):
            print "Quitting the game"
            break
    pygame.display.quit()
