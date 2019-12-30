#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# generated by wxGlade 0.9.3 on Mon Dec 30 01:30:50 2019
#

import wx

# begin wxGlade: dependencies
# end wxGlade

# begin wxGlade: extracode
# end wxGlade


class RotarySettings(wx.Frame):
    def __init__(self, *args, **kwds):
        # begin wxGlade: RotarySettings.__init__
        kwds["style"] = kwds.get("style", 0) | wx.DEFAULT_FRAME_STYLE | wx.FRAME_TOOL_WINDOW
        wx.Frame.__init__(self, *args, **kwds)
        self.SetSize((222, 347))
        self.checkbox_rotary = wx.CheckBox(self, wx.ID_ANY, "Rotary")
        self.spin_rotary_scaley = wx.SpinCtrlDouble(self, wx.ID_ANY, "1.0", min=0.0, max=5.0)
        self.spin_rotary_scalex = wx.SpinCtrlDouble(self, wx.ID_ANY, "1.0", min=0.0, max=5.0)
        self.checkbox_rotary_loop = wx.CheckBox(self, wx.ID_ANY, "Field Loop")
        self.spin_rotary_rotation = wx.SpinCtrlDouble(self, wx.ID_ANY, "360.0", min=0.0, max=20000.0)
        self.checkbox_rotary_roller = wx.CheckBox(self, wx.ID_ANY, "Uses Roller")
        self.spin_rotary_roller_circumference = wx.SpinCtrlDouble(self, wx.ID_ANY, "50.0", min=0.0, max=800.0)
        self.spin_rotary_object_circumference = wx.SpinCtrlDouble(self, wx.ID_ANY, "50.0", min=0.0, max=800.0)

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_CHECKBOX, self.on_check_rotary, self.checkbox_rotary)
        self.Bind(wx.EVT_SPINCTRLDOUBLE, self.on_spin_rotary_scale_y, self.spin_rotary_scaley)
        self.Bind(wx.EVT_TEXT_ENTER, self.on_spin_rotary_scale_y, self.spin_rotary_scaley)
        self.Bind(wx.EVT_SPINCTRLDOUBLE, self.on_spin_rotary_scale_x, self.spin_rotary_scalex)
        self.Bind(wx.EVT_TEXT_ENTER, self.on_spin_rotary_scale_x, self.spin_rotary_scalex)
        self.Bind(wx.EVT_CHECKBOX, self.on_check_rotary_loop, self.checkbox_rotary_loop)
        self.Bind(wx.EVT_SPINCTRLDOUBLE, self.on_spin_rotation, self.spin_rotary_rotation)
        self.Bind(wx.EVT_TEXT_ENTER, self.on_spin_rotation, self.spin_rotary_rotation)
        self.Bind(wx.EVT_CHECKBOX, self.on_check_rotary_roller, self.checkbox_rotary_roller)
        self.Bind(wx.EVT_SPINCTRLDOUBLE, self.on_spin_rotary_roller_circumference, self.spin_rotary_roller_circumference)
        self.Bind(wx.EVT_TEXT_ENTER, self.on_spin_rotary_roller_circumference, self.spin_rotary_roller_circumference)
        self.Bind(wx.EVT_SPINCTRLDOUBLE, self.on_spin_rotary_object_circumference, self.spin_rotary_object_circumference)
        self.Bind(wx.EVT_TEXT_ENTER, self.on_spin_rotary_object_circumference, self.spin_rotary_object_circumference)
        # end wxGlade
        self.project = None
        self.Bind(wx.EVT_CLOSE, self.on_close, self)

    def on_close(self, event):
        try:
            del self.project.windows["preferences"]
        except KeyError:
            pass
        event.Skip()  # Call destroy.

    def set_project(self, project):
        self.project = project
        self.spin_rotary_scalex.SetValue(self.project.writer.scale_x)
        self.spin_rotary_scaley.SetValue(self.project.writer.scale_y)
        self.checkbox_rotary.SetValue(self.project.writer.rotary)
        self.on_check_rotary(None)

    def __set_properties(self):
        # begin wxGlade: RotarySettings.__set_properties
        self.SetTitle("RotarySettings")
        self.checkbox_rotary.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, 0, "Segoe UI"))
        self.checkbox_rotary.SetToolTip("Use Rotary Settings")
        self.spin_rotary_scaley.SetMinSize((80, 23))
        self.spin_rotary_scaley.SetToolTip("Rotary Scale Factor X")
        self.spin_rotary_scaley.Enable(False)
        self.spin_rotary_scaley.SetIncrement(0.01)
        self.spin_rotary_scalex.SetMinSize((80, 23))
        self.spin_rotary_scalex.SetToolTip("Rotary Scale Factor X")
        self.spin_rotary_scalex.Enable(False)
        self.spin_rotary_scalex.SetIncrement(0.01)
        self.checkbox_rotary_loop.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, 0, "Segoe UI"))
        self.checkbox_rotary_loop.SetToolTip("Use Rotary Settings")
        self.spin_rotary_rotation.SetMinSize((80, 23))
        self.spin_rotary_rotation.SetToolTip("Steps required for a full rotation")
        self.spin_rotary_rotation.Enable(False)
        self.spin_rotary_roller_circumference.SetMinSize((80, 23))
        self.spin_rotary_roller_circumference.SetToolTip("Circumference of roller")
        self.spin_rotary_roller_circumference.Enable(False)
        self.spin_rotary_roller_circumference.SetIncrement(0.01)
        self.spin_rotary_object_circumference.SetMinSize((80, 23))
        self.spin_rotary_object_circumference.SetToolTip("Circumference of object in rotary")
        self.spin_rotary_object_circumference.Enable(False)
        self.spin_rotary_object_circumference.SetIncrement(0.01)
        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: RotarySettings.__do_layout
        sizer_main = wx.BoxSizer(wx.VERTICAL)
        sizer_circumference = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, "Object Circumference"), wx.HORIZONTAL)
        sizer_20 = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, "Roller Circumference"), wx.HORIZONTAL)
        sizer_steps = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, "Rotation Steps"), wx.HORIZONTAL)
        sizer_x = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, "Scale X"), wx.HORIZONTAL)
        sizer_y = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, "Scale Y"), wx.HORIZONTAL)
        sizer_main.Add(self.checkbox_rotary, 0, 0, 0)
        sizer_y.Add(self.spin_rotary_scaley, 0, 0, 0)
        sizer_main.Add(sizer_y, 0, wx.EXPAND, 0)
        sizer_x.Add(self.spin_rotary_scalex, 0, 0, 0)
        sizer_main.Add(sizer_x, 0, wx.EXPAND, 0)
        sizer_main.Add((20, 20), 0, 0, 0)
        sizer_main.Add(self.checkbox_rotary_loop, 0, 0, 0)
        sizer_steps.Add(self.spin_rotary_rotation, 0, 0, 0)
        label_steps = wx.StaticText(self, wx.ID_ANY, "steps")
        sizer_steps.Add(label_steps, 0, 0, 0)
        sizer_main.Add(sizer_steps, 0, wx.EXPAND, 0)
        sizer_20.Add(self.checkbox_rotary_roller, 0, 0, 0)
        sizer_20.Add(self.spin_rotary_roller_circumference, 0, 0, 0)
        label_mm = wx.StaticText(self, wx.ID_ANY, "mm")
        sizer_20.Add(label_mm, 0, 0, 0)
        sizer_main.Add(sizer_20, 0, wx.EXPAND, 0)
        sizer_circumference.Add(self.spin_rotary_object_circumference, 0, 0, 0)
        label_mm2 = wx.StaticText(self, wx.ID_ANY, "mm")
        sizer_circumference.Add(label_mm2, 0, 0, 0)
        sizer_main.Add(sizer_circumference, 0, wx.EXPAND, 0)
        self.SetSizer(sizer_main)
        self.Layout()
        # end wxGlade

    def on_check_rotary(self, event):  # wxGlade: RotarySettings.<event_handler>
        self.project.writer.rotary = self.checkbox_rotary.GetValue()
        self.spin_rotary_scalex.Enable(self.checkbox_rotary.GetValue())
        self.spin_rotary_scaley.Enable(self.checkbox_rotary.GetValue())

    def on_spin_rotary_scale_y(self, event):  # wxGlade: RotarySettings.<event_handler>
        self.project.writer.scale_y = self.spin_rotary_scaley.GetValue()

    def on_spin_rotary_scale_x(self, event):  # wxGlade: RotarySettings.<event_handler>
        self.project.writer.scale_x = self.spin_rotary_scalex.GetValue()

    def on_check_rotary_loop(self, event):  # wxGlade: RotarySettings.<event_handler>
        print("Event handler 'on_check_rotary_loop' not implemented!")
        event.Skip()

    def on_spin_rotation(self, event):  # wxGlade: RotarySettings.<event_handler>
        print("Event handler 'on_spin_rotation' not implemented!")
        event.Skip()

    def on_check_rotary_roller(self, event):  # wxGlade: RotarySettings.<event_handler>
        print("Event handler 'on_check_rotary_roller' not implemented!")
        event.Skip()

    def on_spin_rotary_roller_circumference(self, event):  # wxGlade: RotarySettings.<event_handler>
        print("Event handler 'on_spin_rotary_roller_circumference' not implemented!")
        event.Skip()

    def on_spin_rotary_object_circumference(self, event):  # wxGlade: RotarySettings.<event_handler>
        print("Event handler 'on_spin_rotary_object_circumference' not implemented!")
        event.Skip()


# end of class RotarySettings