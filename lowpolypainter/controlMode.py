from enum import Enum

# MASK
MASK_SHIFT = 0x0001
MASK_CTRL = 0x0004
MASK_LEFT_ALT = 0x0008
MASK_RIGHT_ALT = 0x0080

class Mode(Enum):
    POINT = 0
    POINT_AND_LINE = 1
    CONNECT_OR_SPLIT = 2
    PIPETTE = 3


class ControlMode:
    def __init__(self, window):
        self.window = window
        self.modeChangeFunctions = {Mode.POINT: window.changeModeToP,
                                    Mode.POINT_AND_LINE: window.changeModeToPAL,
                                    Mode.CONNECT_OR_SPLIT: window.changeModeToSL,
                                    Mode.PIPETTE: window.changeModeToPipette}

        self.mode = None
        self.lastClickedMode = None

    def reset(self):
        self.changeMode(Mode.POINT_AND_LINE)
        self.lastClickedMode = None

    def changeMode(self, mode):
        self.modeChangeFunctions[mode]()
        self.mode = mode

    def storeOldMode(self):
        if self.lastClickedMode is None:
            self.lastClickedMode = self.mode

    def changeModeKeyPress(self, event):
        if event.char == 'e':
            self.storeOldMode()
            self.changeMode(Mode.CONNECT_OR_SPLIT)
        elif event.char == 'q':
            self.storeOldMode()
            self.changeMode(Mode.POINT)
        elif event.char == 'p' or event.char == 'r':
            self.storeOldMode()
            self.changeMode(Mode.PIPETTE)
        elif event.char == 'w':
            self.storeOldMode()
            self.changeMode(Mode.POINT_AND_LINE)