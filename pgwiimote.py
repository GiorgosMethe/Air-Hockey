"""A wrapper for cwiid.Wiimote, to act as a pygame.mouse."""
import cwiid
import pygame


CWIID_BUTTONS = {"1": cwiid.BTN_1, "2": cwiid.BTN_2, 
        "-": cwiid.BTN_MINUS, "+": cwiid.BTN_PLUS,
        "A": cwiid.BTN_A, "B": cwiid.BTN_B,
        "left": cwiid.BTN_LEFT, "right": cwiid.BTN_RIGHT,
        "down": cwiid.BTN_DOWN, "up": cwiid.BTN_UP,
        "home": cwiid.BTN_HOME}


class Wiimote(object):
    IR_X_MAX = float(cwiid.IR_X_MAX)
    IR_Y_MAX = float(cwiid.IR_Y_MAX)

    def __init__(self, macaddr=None):
        if macaddr is None:
            self.__wiimote = cwiid.Wiimote()
        else:
            self.__wiimote = cwiid.Wiimote(macaddr)
        self.__wiimote.rpt_mode = cwiid.RPT_BTN | cwiid.RPT_IR
        # for get_rel's history
        self.rel_old_pos = (0, 0) 
        # for getl_pos's history, when no LED is seen
        self.pos_old_pos = (0, 0, False) 
        self.__thread = None

    def set_leds(self, bitmask):
        self.__wiimote.led = bitmask

    def get_pressed(self):
        button_state = self.__wiimote.state['buttons']
        is_pressed = {}
        for label, code in CWIID_BUTTONS.items():
            is_pressed[label] = bool(button_state & code)
        return is_pressed

    def get_pos(self):
        state = self.__wiimote.state

        try:
            ir = max(filter(None, state['ir_src']), key=lambda x: x['size'])
        except ValueError:
            return self.pos_old_pos

        pos = 1 - ir['pos'][0] / self.IR_X_MAX, ir['pos'][1] / self.IR_Y_MAX
        self.pos_old_pos = pos[0], pos[1], False
        return pos[0], pos[1], True

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
    black = (0, 0, 0)
    white = (255, 255, 255)
    red = (255, 0, 0)
    screen_width = 400
    screen_height = 400
    raw_input("Press 1+2 on the Wiimote to connect; then press Enter")
    wm = Wiimote("00:25:A0:B3:00:EB")
    print "Connected! Program exits on Wiimote button press."
    pygame.init()
    screen = pygame.display.set_mode((screen_width, screen_height))

    def convert_to_screen(pos):
        return (int(screen_width * pos[0]), int(screen_height * pos[1]))

    while True not in wm.get_pressed().values():
        pos = wm.get_pos()
        if not pos[2]:
            pygame.draw.circle(screen, red, convert_to_screen(pos), 3, 2)
            pygame.display.update()
            continue
        print pos
        screen.fill(black)
        pygame.draw.circle(screen, white, convert_to_screen(pos), 3, 2)
        pygame.display.update()
        if pygame.event.get(pygame.QUIT):
            print "Quitting the game"
            break
    pygame.display.quit()
