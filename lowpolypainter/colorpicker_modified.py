"""
tkcolorpicker - Alternative to colorchooser for Tkinter.
Copyright 2017 Juliette Monsel <j_4321@protonmail.com>

tkcolorpicker is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Colorpicker dialog (modified for Low Poly Painter program)
"""


from PIL import ImageTk
from Tkinter import *
from tkcolorpicker.functions import tk, ttk, round2, create_checkered_image, \
    overlay, PALETTE, hsv_to_rgb, hexa_to_rgb, rgb_to_hexa, col2hue, rgb_to_hsv
from tkcolorpicker.alphabar import AlphaBar
from tkcolorpicker.gradientbar import GradientBar
from tkcolorpicker.colorsquare import ColorSquare
from tkcolorpicker.spinbox import Spinbox
from tkcolorpicker.limitvar import LimitVar
from locale import getdefaultlocale
import tkMessageBox

class ColorPicker(Frame):
    """Color picker dialog."""

    def __init__(self, parent=None, color=(187, 192, 191), alpha=False, title=("Color Chooser")):
        """
        Create a ColorPicker dialog.

        Arguments:
            * parent: parent window
            * color: initially selected color in rgb or hexa format
            * alpha: alpha channel support (boolean)
            * title: dialog title
        """
        Frame.__init__(self, parent, bg="white")
        self.parent = parent
        self.color = ""
        self.alpha_channel = bool(alpha)
        font1 = "-family {Heiti TC} -size 12 -weight normal -slant "  \
            "roman -underline 0 -overstrike 0"
        style = ttk.Style(self)
        style.configure('.', font=font1, bg='#ffffff', highlightbackground='#ffffff')
        style.map("palette.TFrame", relief=[('focus', 'flat')],
                  bordercolor=[('focus', "#ffffff")])

        if isinstance(color, str):
            if re.match(r"^#[0-9A-F]{8}$", color.upper()):
                col = hexa_to_rgb(color)
                self._old_color = col[:3]
                if alpha:
                    self._old_alpha = col[3]
                    old_color = color
                else:
                    old_color = color[:7]
            elif re.match(r"^#[0-9A-F]{6}$", color.upper()):
                self._old_color = hexa_to_rgb(color)
                old_color = color
                if alpha:
                    self._old_alpha = 255
                    old_color += 'FF'
            else:
                col = self.winfo_rgb(color)
                self._old_color = tuple(round2(c * 255 / 65535) for c in col)
                args = self._old_color
                if alpha:
                    self._old_alpha = 255
                    args = self._old_color + (255,)
                old_color = rgb_to_hexa(*args)
        else:
            self._old_color = color[:3]
            if alpha:
                if len(color) < 4:
                    color += (255,)
                    self._old_alpha = 255
                else:
                    self._old_alpha = color[3]
            old_color = rgb_to_hexa(*color)

        # --- frame for palette and pipette tool
        frame = tk.Frame(self)
        frame.columnconfigure(0, weight=0)
        frame.rowconfigure(0, weight=0)
        frame.columnconfigure(1, weight=1)
        frame.rowconfigure(1, weight=1)
        frame.columnconfigure(2, weight=0)
        frame.rowconfigure(2, weight=0)

        # --- palette stores chosen colors
        palette = tk.Frame(frame)
        palette.grid(row=0, column=0, sticky="nsew")

        # at start default palette item 1 is in edit mode (borderwidth=1 instead of 0)
        self.paletteFrame1 = tk.Frame(palette, borderwidth=1, relief="solid")
        self.paletteFrame1.number = 1
        self.paletteItem1 = tk.Label(self.paletteFrame1, background=rgb_to_hexa(*self._old_color), width=2, height=1)
        self.paletteItem1.editMode = True
        self.paletteItem1.bind("<1>", self._palette_cmd)
        self.paletteItem1.pack()
        self.paletteFrame1.grid(row=0, column=0, padx=2, pady=2)

        self.paletteFrame2 = tk.Frame(palette, borderwidth=0, relief="solid")
        self.paletteFrame2.number = 2
        self.paletteItem2 = tk.Label(self.paletteFrame2, background=PALETTE[1], width=2, height=1)
        self.paletteItem2.editMode = False
        self.paletteItem2.bind("<1>", self._palette_cmd)
        self.paletteItem2.pack()
        self.paletteFrame2.grid(row=0, column=1, padx=2, pady=2)

        self.paletteFrame3 = tk.Frame(palette, borderwidth=0, relief="solid")
        self.paletteFrame3.number = 3
        self.paletteItem3 = tk.Label(self.paletteFrame3, background=PALETTE[2], width=2, height=1)
        self.paletteItem3.editMode = False
        self.paletteItem3.bind("<1>", self._palette_cmd)
        self.paletteItem3.pack()
        self.paletteFrame3.grid(row=0, column=2, padx=2, pady=2)

        self.paletteFrame4 = tk.Frame(palette, borderwidth=0, relief="solid")
        self.paletteFrame4.number = 4
        self.paletteItem4 = tk.Label(self.paletteFrame4, background=PALETTE[3], width=2, height=1)
        self.paletteItem4.editMode = False
        self.paletteItem4.bind("<1>", self._palette_cmd)
        self.paletteItem4.pack()
        self.paletteFrame4.grid(row=0, column=3, padx=2, pady=2)

        self.paletteFrame5 = tk.Frame(palette, borderwidth=0, relief="solid")
        self.paletteFrame5.number = 5
        self.paletteItem5 = tk.Label(self.paletteFrame5, background=PALETTE[4], width=2, height=1)
        self.paletteItem5.editMode = False
        self.paletteItem5.bind("<1>", self._palette_cmd)
        self.paletteItem5.pack()
        self.paletteFrame5.grid(row=0, column=4, padx=2, pady=2)

        self.paletteFrame6 = tk.Frame(palette, borderwidth=0, relief="solid")
        self.paletteFrame6.number = 6
        self.paletteItem6 = tk.Label(self.paletteFrame6, background=PALETTE[5], width=2, height=1)
        self.paletteItem6.editMode = False
        self.paletteItem6.bind("<1>", self._palette_cmd)
        self.paletteItem6.pack()
        self.paletteFrame6.grid(row=0, column=5, padx=2, pady=2)

        self.paletteFrame7 = tk.Frame(palette, borderwidth=0, relief="solid")
        self.paletteFrame7.number = 7
        self.paletteItem7 = tk.Label(self.paletteFrame7, background=PALETTE[6], width=2, height=1)
        self.paletteItem7.editMode = False
        self.paletteItem7.bind("<1>", self._palette_cmd)
        self.paletteItem7.pack()
        self.paletteFrame7.grid(row=0, column=6, padx=2, pady=2)

        self.paletteFrame8 = tk.Frame(palette, borderwidth=0, relief="solid")
        self.paletteFrame8.number = 8
        self.paletteItem8 = tk.Label(self.paletteFrame8, background=PALETTE[7], width=2, height=1)
        self.paletteItem8.editMode = False
        self.paletteItem8.bind("<1>", self._palette_cmd)
        self.paletteItem8.pack()
        self.paletteFrame8.grid(row=0, column=7, padx=2, pady=2)

        self.paletteFrame9 = tk.Frame(palette, borderwidth=0, relief="solid")
        self.paletteFrame9.number = 9
        self.paletteItem9 = tk.Label(self.paletteFrame9, background=PALETTE[8], width=2, height=1)
        self.paletteItem9.editMode = False
        self.paletteItem9.bind("<1>", self._palette_cmd)
        self.paletteItem9.pack()
        self.paletteFrame9.grid(row=0, column=8, padx=2, pady=2)

        self.paletteFrame10 = tk.Frame(palette, borderwidth=0, relief="solid")
        self.paletteFrame10.number = 10
        self.paletteItem10 = tk.Label(self.paletteFrame10, background=PALETTE[9], width=2, height=1)
        self.paletteItem10.editMode = False
        self.paletteItem10.bind("<1>", self._palette_cmd)
        self.paletteItem10.pack()
        self.paletteFrame10.grid(row=0, column=9, padx=2, pady=2)

        self.paletteItems = [self.paletteItem1, self.paletteItem2, self.paletteItem3, self.paletteItem4, self.paletteItem5,
                            self.paletteItem6, self.paletteItem7, self.paletteItem8, self.paletteItem9, self.paletteItem10]
        self.paletteFrames = [self.paletteFrame1, self.paletteFrame2, self.paletteFrame3, self.paletteFrame4, self.paletteFrame5,
                            self.paletteFrame6, self.paletteFrame7, self.paletteFrame8, self.paletteFrame9, self.paletteFrame10]

        # TODO: --- pipette tool for choosing color from image or screen?
        self.pipetteLabel = tk.Label(palette, text="Pipette", font=font1)
        self.pipetteLabel.bind("<1>", self.chooseColorFromImage)
        self.pipetteLabel.grid(row=0, column=10, padx=5)

        # --- ColorSquare
        hue = col2hue(*self._old_color)

        square = tk.Frame(self, borderwidth=0, relief='flat')
        self.square = ColorSquare(square, hue=hue, width=200, height=200,
                                  color=rgb_to_hsv(*self._old_color),
                                  highlightthickness=0)
        self.square.pack()

        # --- GradientBar
        bar = tk.Frame(self, borderwidth=0, relief='flat')
        self.bar = GradientBar(bar, hue=hue, width=200, height=15, highlightthickness=0)
        self.bar.pack()

        col_frame = tk.Frame(self)

        # --- hue saturation value
        hsv_frame = tk.Frame(col_frame, relief="flat", borderwidth=0)
        hsv_frame.pack(pady=(0, 4), fill="x")
        hsv_frame.columnconfigure(0, weight=1)
        self.hue = LimitVar(0, 360, self)
        self.saturation = LimitVar(0, 100, self)
        self.value = LimitVar(0, 100, self)

        s_h = Spinbox(hsv_frame, from_=0, to=360, width=4, name='spinbox',
                      textvariable=self.hue, bg='#ffffff', buttonbackground='#ffffff',insertbackground='#ffffff', command=self._update_color_hsv)
        s_s = Spinbox(hsv_frame, from_=0, to=100, width=4,
                      textvariable=self.saturation, name='spinbox',
                      command=self._update_color_hsv)
        s_v = Spinbox(hsv_frame, from_=0, to=100, width=4, name='spinbox',
                      textvariable=self.value, command=self._update_color_hsv)
        h, s, v = rgb_to_hsv(*self._old_color)
        s_h.delete(0, 'end')
        s_h.insert(0, h)
        s_s.delete(0, 'end')
        s_s.insert(0, s)
        s_v.delete(0, 'end')
        s_v.insert(0, v)
        s_h.grid(row=0, column=1, sticky='w', padx=4, pady=4)
        s_s.grid(row=1, column=1, sticky='w', padx=4, pady=4)
        s_v.grid(row=2, column=1, sticky='w', padx=4, pady=4)
        tk.Label(hsv_frame, text=('Hue'), font=font1, relief="flat").grid(row=0, column=0, sticky='e',
                                                 padx=4, pady=4)
        tk.Label(hsv_frame, text=('Saturation'), font=font1, relief="flat").grid(row=1, column=0, sticky='e',
                                                        padx=4, pady=4)
        tk.Label(hsv_frame, text=('Value'), font=font1, relief="flat").grid(row=2, column=0, sticky='e',
                                                   padx=4, pady=4)

        # --- rgb
        rgb_frame = tk.Frame(col_frame, relief="flat", borderwidth=0)
        rgb_frame.pack(pady=4, fill="x")
        rgb_frame.columnconfigure(0, weight=1)
        self.red = LimitVar(0, 255, self)
        self.green = LimitVar(0, 255, self)
        self.blue = LimitVar(0, 255, self)

        s_red = Spinbox(rgb_frame, from_=0, to=255, width=4, name='spinbox',
                        textvariable=self.red, command=self._update_color_rgb)
        s_green = Spinbox(rgb_frame, from_=0, to=255, width=4, name='spinbox',
                          textvariable=self.green, command=self._update_color_rgb)
        s_blue = Spinbox(rgb_frame, from_=0, to=255, width=4, name='spinbox',
                         textvariable=self.blue, command=self._update_color_rgb)
        s_red.delete(0, 'end')
        s_red.insert(0, self._old_color[0])
        s_green.delete(0, 'end')
        s_green.insert(0, self._old_color[1])
        s_blue.delete(0, 'end')
        s_blue.insert(0, self._old_color[2])
        s_red.grid(row=0, column=1, sticky='e', padx=4, pady=4)
        s_green.grid(row=1, column=1, sticky='e', padx=4, pady=4)
        s_blue.grid(row=2, column=1, sticky='e', padx=4, pady=4)
        tk.Label(rgb_frame, text=('r'), font=font1).grid(row=0, column=0, sticky='e',
                                                 padx=4, pady=4)
        tk.Label(rgb_frame, text=('g'), font=font1).grid(row=1, column=0, sticky='e',
                                                   padx=4, pady=4)
        tk.Label(rgb_frame, text=('b'), font=font1).grid(row=2, column=0, sticky='e',
                                                  padx=4, pady=4)
        # --- hexa
        hexa_frame = tk.Frame(col_frame)
        hexa_frame.pack(fill="x")
        self.hexa = tk.Entry(hexa_frame, justify="right", width=10, name='entry', font=font1, highlightbackground='#ffffff')
        self.hexa.insert(0, old_color.upper())
        tk.Label(hexa_frame, text="Hex", font=font1).pack(side="left", padx=4, pady=(4, 1))
        self.hexa.pack(side="left", padx=6, pady=(4, 1), fill='x', expand=True)

        # --- alpha (not implemented in GUI)
        if alpha:
            alpha_frame = tk.Frame(self)
            alpha_frame.columnconfigure(1, weight=1)
            self.alpha = LimitVar(0, 255, self)
            alphabar = tk.Frame(alpha_frame, borderwidth=2, relief='flat')
            self.alphabar = AlphaBar(alphabar, alpha=self._old_alpha, width=200,
                                     color=self._old_color, highlightthickness=0)
            self.alphabar.pack()
            s_alpha = Spinbox(alpha_frame, from_=0, to=255, width=4,
                              textvariable=self.alpha, command=self._update_alpha)
            s_alpha.delete(0, 'end')
            s_alpha.insert(0, self._old_alpha)
            alphabar.grid(row=0, column=0, padx=(0, 4), pady=4, sticky='w')
            tk.Label(alpha_frame, text=_('Alpha')).grid(row=0, column=1, sticky='e',
                                                         padx=4, pady=4)
            s_alpha.grid(row=0, column=2, sticky='w', padx=(4, 6), pady=4)

        # --- validation
        # TODO: color or validation image instead of text, image placing still makes trouble
        self.button_frame = tk.Frame(self)
        #path = "lowpolypainter/resources/icons/"
        #self.okImage = PhotoImage(path + 'color.png')
        self.okButton = Label(self.button_frame, text='Color Face', borderwidth="0", width='20', height='3', background='#ffffff', font=font1)
        #self.okButton.configure(image=self.okImage)
        self.okButton.bind("<Button-1>", self.ok)
        self.okButton.pack(side='right')

        # --- placement
        square.grid(row=0, column=0, padx=10, pady=(9, 0), sticky='nsew')
        bar.grid(row=1, column=0, padx=10, pady=(10, 4), sticky='nsew')
        if alpha:
            alpha_frame.grid(row=2, column=0, columnspan=2, padx=10,
                             pady=(1, 4), sticky='nsew')
        col_frame.grid(row=0, rowspan=2, column=1, padx=(4, 10), pady=(10, 4))
        frame.grid(row=3, column=0, columnspan=2, pady=(4, 10), padx=10, sticky="nsew")
        self.button_frame.grid(row=4, column=0, pady=(0, 10), padx=10, sticky="nsew")


        # --- bindings
        self.bar.bind("<ButtonRelease-1>", self._change_color, True)
        self.bar.bind("<Button-1>", self._unfocus, True)
        if alpha:
            self.alphabar.bind("<ButtonRelease-1>", self._change_alpha, True)
            self.alphabar.bind("<Button-1>", self._unfocus, True)
        self.square.bind("<Button-1>", self._unfocus, True)
        self.square.bind("<ButtonRelease-1>", self._change_sel_color, True)
        self.square.bind("<B1-Motion>", self._change_sel_color, True)
        s_red.bind('<FocusOut>', self._update_color_rgb)
        s_green.bind('<FocusOut>', self._update_color_rgb)
        s_blue.bind('<FocusOut>', self._update_color_rgb)
        s_red.bind('<Return>', self._update_color_rgb)
        s_green.bind('<Return>', self._update_color_rgb)
        s_blue.bind('<Return>', self._update_color_rgb)
        s_h.bind('<FocusOut>', self._update_color_hsv)
        s_s.bind('<FocusOut>', self._update_color_hsv)
        s_v.bind('<FocusOut>', self._update_color_hsv)
        s_h.bind('<Return>', self._update_color_hsv)
        s_s.bind('<Return>', self._update_color_hsv)
        s_v.bind('<Return>', self._update_color_hsv)
        if alpha:
            s_alpha.bind('<Return>', self._update_alpha)
            s_alpha.bind('<FocusOut>', self._update_alpha)
        self.hexa.bind("<FocusOut>", self._update_color_hexa)
        self.hexa.bind("<Return>", self._update_color_hexa)

        self.lift()

    def get_color(self):
        """Return selected color, return an empty string if no color is selected."""
        return self.color

    def _unfocus(self, event):
        """Unfocus palette items when click on bar or square."""
        w = self.focus_get()
        if w != self and 'spinbox' not in str(w) and 'entry' not in str(w):
            self.focus_set()

    def _update_preview(self):
        """Update color preview in palette items"""
        color = self.hexa.get()
        activePaletteItem = filter(lambda item: item.editMode, self.paletteItems)[0]
        activePaletteItem.configure(background=color)

    def _reset_preview(self, event):
        """Respond to user click on a palette item."""
        label = event.widget
        label.master.focus_set()
        label.master.configure(relief="flat")
        args = self._old_color
        if self.alpha_channel:
            args += (self._old_alpha,)
            self.alpha.set(self._old_alpha)
            self.alphabar.set_color(args)
        color = rgb_to_hexa(*args)
        h, s, v = rgb_to_hsv(*self._old_color)
        self.red.set(self._old_color[0])
        self.green.set(self._old_color[1])
        self.blue.set(self._old_color[2])
        self.hue.set(h)
        self.saturation.set(s)
        self.value.set(v)
        self.hexa.delete(0, "end")
        self.hexa.insert(0, color.upper())
        self.bar.set(h)
        self.square.set_hsv((h, s, v))
        self._update_preview()

    def _palette_items_update(self, activeItemNumber):
        # change border look of active palette frame
        for item in self.paletteFrames:
            if item.number != activeItemNumber:
                item.configure(borderwidth=0)
            else:
                item.configure(borderwidth=1)

        # update editMode bools
        for item in self.paletteItems:
            if item.master.number != activeItemNumber:
                item.editMode = False
            else:
                item.editMode = True

    def _palette_cmd(self, event):
        """Respond to user click on a palette item."""
        activeNumber = event.widget.master.number
        self._palette_items_update(activeNumber)
        label = self.paletteItems[activeNumber-1]

        r, g, b = self.winfo_rgb(label.cget("background"))
        r = round2(r * 255 / 65535)
        g = round2(g * 255 / 65535)
        b = round2(b * 255 / 65535)
        args = (r, g, b)
        if self.alpha_channel:
            a = self.alpha.get()
            args += (a,)
            self.alphabar.set_color(args)
        color = rgb_to_hexa(*args)
        h, s, v = rgb_to_hsv(r, g, b)
        self.red.set(r)
        self.green.set(g)
        self.blue.set(b)
        self.hue.set(h)
        self.saturation.set(s)
        self.value.set(v)
        self.hexa.delete(0, "end")
        self.hexa.insert(0, color.upper())
        self._update_preview()
        self.bar.set(h)
        self.square.set_hsv((h, s, v))

    def _change_sel_color(self, event):
        """Respond to motion of the color selection cross."""
        (r, g, b), (h, s, v), color = self.square.get()
        self.red.set(r)
        self.green.set(g)
        self.blue.set(b)
        self.saturation.set(s)
        self.value.set(v)
        self.hexa.delete(0, "end")
        self.hexa.insert(0, color.upper())
        if self.alpha_channel:
            self.alphabar.set_color((r, g, b))
            self.hexa.insert('end',
                             ("%2.2x" % self.alpha.get()).upper())
        self._update_preview()

    def _change_color(self, event):
        """Respond to motion of the hsv cursor."""
        h = self.bar.get()
        self.square.set_hue(h)
        (r, g, b), (h, s, v), sel_color = self.square.get()
        self.red.set(r)
        self.green.set(g)
        self.blue.set(b)
        self.hue.set(h)
        self.saturation.set(s)
        self.value.set(v)
        self.hexa.delete(0, "end")
        self.hexa.insert(0, sel_color.upper())
        if self.alpha_channel:
            self.alphabar.set_color((r, g, b))
            self.hexa.insert('end',
                             ("%2.2x" % self.alpha.get()).upper())
        self._update_preview()

    def _change_alpha(self, event):
        """Respond to motion of the alpha cursor."""
        a = self.alphabar.get()
        self.alpha.set(a)
        hexa = self.hexa.get()
        hexa = hexa[:7] + ("%2.2x" % a).upper()
        self.hexa.delete(0, 'end')
        self.hexa.insert(0, hexa)
        self._update_preview()

    def _update_color_hexa(self, event=None):
        """Update display after a change in the HEX entry."""
        color = self.hexa.get().upper()
        self.hexa.delete(0, 'end')
        self.hexa.insert(0, color)
        if re.match(r"^#[0-9A-F]{6}$", color):
            r, g, b = hexa_to_rgb(color)
            self.red.set(r)
            self.green.set(g)
            self.blue.set(b)
            h, s, v = rgb_to_hsv(r, g, b)
            self.hue.set(h)
            self.saturation.set(s)
            self.value.set(v)
            self.bar.set(h)
            self.square.set_hsv((h, s, v))
            if self.alpha_channel:
                a = self.alpha.get()
                self.hexa.insert('end', ("%2.2x" % a).upper())
                self.alphabar.set_color((r, g, b, a))
        elif self.alpha_channel and re.match(r"^#[0-9A-F]{8}$", color):
            r, g, b, a = hexa_to_rgb(color)
            self.red.set(r)
            self.green.set(g)
            self.blue.set(b)
            self.alpha.set(a)
            self.alphabar.set_color((r, g, b, a))
            h, s, v = rgb_to_hsv(r, g, b)
            self.hue.set(h)
            self.saturation.set(s)
            self.value.set(v)
            self.bar.set(h)
            self.square.set_hsv((h, s, v))
        else:
            self._update_color_rgb()
        self._update_preview()

    def _update_alpha(self, event=None):
        """Update display after a change in the alpha spinbox."""
        a = self.alpha.get()
        hexa = self.hexa.get()
        hexa = hexa[:7] + ("%2.2x" % a).upper()
        self.hexa.delete(0, 'end')
        self.hexa.insert(0, hexa)
        self.alphabar.set(a)
        self._update_preview()

    def _update_color_hsv(self, event=None):
        """Update display after a change in the HSV spinboxes."""
        if event is None or event.widget.old_value != event.widget.get():
            h = self.hue.get()
            s = self.saturation.get()
            v = self.value.get()
            sel_color = hsv_to_rgb(h, s, v)
            self.red.set(sel_color[0])
            self.green.set(sel_color[1])
            self.blue.set(sel_color[2])
            if self.alpha_channel:
                sel_color += (self.alpha.get(),)
                self.alphabar.set_color(sel_color)
            hexa = rgb_to_hexa(*sel_color)
            self.hexa.delete(0, "end")
            self.hexa.insert(0, hexa)
            self.square.set_hsv((h, s, v))
            self.bar.set(h)
            self._update_preview()

    def _update_color_rgb(self, event=None):
        """Update display after a change in the RGB spinboxes."""
        if event is None or event.widget.old_value != event.widget.get():
            r = self.red.get()
            g = self.green.get()
            b = self.blue.get()
            h, s, v = rgb_to_hsv(r, g, b)
            self.hue.set(h)
            self.saturation.set(s)
            self.value.set(v)
            args = (r, g, b)
            if self.alpha_channel:
                args += (self.alpha.get(),)
                self.alphabar.set_color(args)
            hexa = rgb_to_hexa(*args)
            self.hexa.delete(0, "end")
            self.hexa.insert(0, hexa)
            self.square.set_hsv((h, s, v))
            self.bar.set(h)
            self._update_preview()

    # this method calls the update of chosen face color
    def ok(self, event=None):
        rgb, hsv, hexa = self.square.get()
        if self.alpha_channel:
            hexa = self.hexa.get()
            rgb += (self.alpha.get(),)
        self.color = rgb, hsv, hexa
        self.parent.updateFaceColor(hexa)

    # method which might be useful for future storing methods
    # return color of stored palette items
    def getStoredHexaColors(self):
        colors = [self.paletteItem1.cget("background"), self.paletteItem2.cget("background"),
                self.paletteItem3.cget("background"), self.paletteItem4.cget("background"),
                self.paletteItem5.cget("background"), self.paletteItem6.cget("background"),
                self.paletteItem7.cget("background"), self.paletteItem8.cget("background"),
                self.paletteItem9.cget("background"), self.paletteItem10.cget("background")]
        return colors

    # method which might be useful for future storing methods:
    # configures color of palette items
    def setStoredHexaColors(self, colors):
        if len(colors) == 10:
            self.paletteItem1.config(background=colors[0])
            self.paletteItem2.config(background=colors[1])
            self.paletteItem3.config(background=colors[2])
            self.paletteItem4.config(background=colors[3])
            self.paletteItem5.config(background=colors[4])
            self.paletteItem6.config(background=colors[5])
            self.paletteItem7.config(background=colors[6])
            self.paletteItem8.config(background=colors[7])
            self.paletteItem9.config(background=colors[8])
            self.paletteItem10.config(background=colors[9])

    def getCoords(self, event=None):
        print tuple([event.x_root, event.y_root])
        #colorInput_hexa = self.parent.getColorFromImage(event.x, event.y)
        self.grab_release()

    def chooseColorFromImage(self, event=None):
        self.bind("<1>", self.getCoords)
        self.grab_set()



def askcolor(color="white", parent=None, title=("Color Chooser"), alpha=False):
    """
    Open a ColorPicker dialog and return the chosen color.

    The selected color is returned in RGB(A) and hexadecimal #RRGGBB(AA) formats.
    (None, None) is returned if the color selection is cancelled.

    Arguments:
        * color: initially selected color (RGB(A), hexa or tkinter color name)
        * parent: parent window
        * title: dialog title
        * alpha: alpha channel suppport
    """
    col = ColorPicker(parent, color, alpha, title)
    col.wait_window(col)
    res = col.get_color()
    print(res)
    if res:
        return res[0], res[2]
    else:
        return None, None
