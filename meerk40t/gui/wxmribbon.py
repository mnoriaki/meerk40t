import copy
import threading

import wx
import wx.lib.agw.ribbon as RB

from wx import aui

from meerk40t.kernel import Job, lookup_listener, signal_listener
from meerk40t.svgelements import Color

from .icons import icons8_opened_folder_50

_ = wx.GetTranslation

ID_PAGE_MAIN = 10
ID_PAGE_TOOL = 20
ID_PAGE_TOGGLE = 30


BUTTONBASE = 0
PARENT = 1
ID = 2
TOGGLE = 3
GROUP = 4


class RibbonButtonBar(RB.RibbonButtonBar):
    def __init__(
        self,
        parent,
        id=wx.ID_ANY,
        pos=wx.DefaultPosition,
        size=wx.DefaultSize,
        agwStyle=0,
    ):
        super().__init__(parent, id, pos, size, agwStyle)
        self.screen_refresh_lock = threading.Lock()

    def OnPaint(self, event):
        """
        Handles the ``wx.EVT_PAINT`` event for :class:`RibbonButtonBar`.

        :param `event`: a :class:`PaintEvent` event to be processed.
        """
        if self.screen_refresh_lock.acquire(timeout=0.2):

            dc = wx.AutoBufferedPaintDC(self)
            if not dc is None:

                self._art.DrawButtonBarBackground(
                    dc, self, wx.Rect(0, 0, *self.GetSize())
                )

                try:
                    layout = self._layouts[self._current_layout]
                except IndexError:
                    return

                for button in layout.buttons:
                    base = button.base

                    bitmap = base.bitmap_large
                    bitmap_small = base.bitmap_small

                    if base.state & RB.RIBBON_BUTTONBAR_BUTTON_DISABLED:
                        bitmap = base.bitmap_large_disabled
                        bitmap_small = base.bitmap_small_disabled

                    rect = wx.Rect(
                        button.position + self._layout_offset,
                        base.sizes[button.size].size,
                    )
                    self._art.DrawButtonBarButton(
                        dc,
                        self,
                        rect,
                        base.kind,
                        base.state | button.size,
                        base.label,
                        bitmap,
                        bitmap_small,
                    )
            # else:
            #     print("DC was faulty")
            self.screen_refresh_lock.release()
        # else:
        #     print ("OnPaint was locked...")


# def debug_system_colors():
#     reslist = list()
#     slist = (
#         (wx.SYS_COLOUR_SCROLLBAR, "The scrollbar grey area."),
#         (wx.SYS_COLOUR_DESKTOP, "The desktop colour."),
#         (wx.SYS_COLOUR_ACTIVECAPTION, "Active window caption colour."),
#         (wx.SYS_COLOUR_INACTIVECAPTION, "Inactive window caption colour."),
#         (wx.SYS_COLOUR_MENU, "Menu background colour."),
#         (wx.SYS_COLOUR_WINDOW, "Window background colour."),
#         (wx.SYS_COLOUR_WINDOWFRAME, "Window frame colour."),
#         (wx.SYS_COLOUR_MENUTEXT, "Colour of the text used in the menus."),
#         (wx.SYS_COLOUR_WINDOWTEXT, "Colour of the text used in generic windows."),
#         (
#             wx.SYS_COLOUR_CAPTIONTEXT,
#             "Colour of the text used in captions, size boxes and scrollbar arrow boxes.",
#         ),
#         (wx.SYS_COLOUR_ACTIVEBORDER, "Active window border colour."),
#         (wx.SYS_COLOUR_INACTIVEBORDER, "Inactive window border colour."),
#         (wx.SYS_COLOUR_APPWORKSPACE, "Background colour for MDI applications."),
#         (wx.SYS_COLOUR_HIGHLIGHT, "Colour of item(s) selected in a control."),
#         (
#             wx.SYS_COLOUR_HIGHLIGHTTEXT,
#             "Colour of the text of item(s) selected in a control.",
#         ),
#         (wx.SYS_COLOUR_BTNFACE, "Face shading colour on push buttons."),
#         (wx.SYS_COLOUR_BTNSHADOW, "Edge shading colour on push buttons."),
#         (wx.SYS_COLOUR_GRAYTEXT, "Colour of greyed (disabled) text."),
#         (wx.SYS_COLOUR_BTNTEXT, "Colour of the text on push buttons."),
#         (wx.SYS_COLOUR_INACTIVECAPTIONTEXT, "Colour of the text in inactive captions."),
#         (wx.SYS_COLOUR_BTNHIGHLIGHT, "Highlight colour for buttons."),
#         (
#             wx.SYS_COLOUR_3DDKSHADOW,
#             "Dark shadow colour for three-dimensional display elements.",
#         ),
#         (wx.SYS_COLOUR_3DLIGHT, "Light colour for three-dimensional display elements."),
#         (wx.SYS_COLOUR_INFOTEXT, "Text colour for tooltip controls."),
#         (wx.SYS_COLOUR_INFOBK, "Background colour for tooltip controls."),
#         # (wx.SYS_COLOUR_LISTBOX, "Background colour for list-like controls."),
#         # (wx.SYS_COLOUR_HOTLIGHT, "Colour for a hyperlink or hot-tracked item."),
#         # (wx.SYS_COLOUR_GRADIENTACTIVECAPTION, "Right side colour in the colour gradient of an active window’s title bar."),
#         # (wx.SYS_COLOUR_GRADIENTINACTIVECAPTION, "Right side colour in the colour gradient of an inactive window’s title bar."),
#         # (wx.SYS_COLOUR_MENUHILIGHT, "The colour used to highlight menu items when the menu appears as a flat menu."),
#         # (wx.SYS_COLOUR_MENUBAR, "The background colour for the menu bar when menus appear as flat menus."),
#         # (wx.SYS_COLOUR_LISTBOXTEXT, "Text colour for list-like controls."),
#         # (wx.SYS_COLOUR_LISTBOXHIGHLIGHTTEXT, "Text colour for the unfocused selection of list-like controls."),
#         # (wx.SYS_COLOUR_BACKGROUND, "Synonym for SYS_COLOUR_DESKTOP ."),
#         # (wx.SYS_COLOUR_3DFACE, "Synonym for SYS_COLOUR_BTNFACE ."),
#         # (wx.SYS_COLOUR_3DSHADOW, "Synonym for SYS_COLOUR_BTNSHADOW ."),
#         # (wx.SYS_COLOUR_BTNHILIGHT, "Synonym for SYS_COLOUR_BTNHIGHLIGHT ."),
#         # (wx.SYS_COLOUR_3DHIGHLIGHT, "Synonym for SYS_COLOUR_BTNHIGHLIGHT ."),
#         # (wx.SYS_COLOUR_3DHILIGHT, "Synonym for SYS_COLOUR_BTNHIGHLIGHT ."),
#         # (wx.SYS_COLOUR_FRAMEBK, "Synonym for SYS_COLOUR_BTNFACE "),
#     )
#     is_dark = False
#     dark_bg = False
#     try:
#         sysappearance = wx.SystemSettings().GetAppearance()
#         source = "Sysappearance"
#         is_dark = sysappearance.IsDark()
#         dark_bg = sysappearance.IsUsingDarkBackground()
#         reslist.append(
#             "%s delivered: is_dark=%s, dark_bg=%s" % (source, is_dark, dark_bg)
#         )
#         source = "Default"
#         is_dark = wx.SystemSettings().GetColour(wx.SYS_COLOUR_WINDOW)[0] < 127
#         dark_bg = wx.SystemSettings().GetColour(wx.SYS_COLOUR_WINDOW)[0] < 127
#         reslist.append(
#             "%s delivered: is_dark=%s, dark_bg=%s" % (source, is_dark, dark_bg)
#         )
#     except:
#         source = "Default"
#         is_dark = wx.SystemSettings().GetColour(wx.SYS_COLOUR_WINDOW)[0] < 127
#         dark_bg = wx.SystemSettings().GetColour(wx.SYS_COLOUR_WINDOW)[0] < 127
#         reslist.append(
#             "%s delivered: is_dark=%s, dark_bg=%s" % (source, is_dark, dark_bg)
#         )
#     for colpair in slist:
#         syscol = wx.SystemSettings().GetColour(colpair[0])
#         if syscol is None:
#             s = "Null"
#         else:
#             try:
#                 s = syscol.GetAsString(wx.C2S_NAME)
#             except AssertionError:
#                 s = syscol.GetAsString(wx.C2S_CSS_SYNTAX)
#         reslist.append("{col} for {desc}".format(col=s, desc=colpair[1]))
#     return reslist


def register_panel_ribbon(window, context):
    # debug_system_colors()
    minh = 150
    pane = (
        aui.AuiPaneInfo()
        .Name("ribbon")
        .Top()
        .RightDockable(False)
        .LeftDockable(False)
        .MinSize(300, minh)
        .FloatingSize(640, minh)
        .Caption(_("Ribbon"))
        .CaptionVisible(not context.pane_lock)
    )
    pane.dock_proportion = 640
    ribbon = RibbonPanel(window, wx.ID_ANY, context=context)
    pane.control = ribbon

    window.on_pane_add(pane)
    context.register("pane/ribbon", pane)


class RibbonPanel(wx.Panel):
    def __init__(self, *args, context=None, **kwds):
        kwds["style"] = kwds.get("style", 0) | wx.TAB_TRAVERSAL
        wx.Panel.__init__(self, *args, **kwds)
        self.context = context
        self._job = Job(
            process=self._perform_realization,
            job_name="realize_ribbon_bar",
            interval=0.1,
            times=1,
            run_main=True,
        )
        self.buttons = []
        self.ribbon_bars = []
        self.ribbon_panels = []
        self.ribbon_pages = []

        # Some helper variables for showing / hiding the toolbar
        self.panels_shown = True
        self.minmax = None
        self.context = context
        self.stored_labels = {}
        self.stored_height = 0
        self.art_provider_count = 0

        self.button_lookup = {}
        self.group_lookup = {}

        # Define Ribbon.
        self._ribbon = RB.RibbonBar(
            self,
            agwStyle=RB.RIBBON_BAR_DEFAULT_STYLE
            | RB.RIBBON_BAR_SHOW_PANEL_EXT_BUTTONS
            | RB.RIBBON_BAR_SHOW_PANEL_MINIMISE_BUTTONS,
        )
        self.__set_ribbonbar()

        sizer_1 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_1.Add(self._ribbon, 1, wx.EXPAND, 0)
        self.SetSizer(sizer_1)
        self.Layout()
        # self._ribbon
        self.pipe_state = None
        self._ribbon_dirty = False

    def button_click_right(self, event):
        """
        Handles the ``wx.EVT_RIGHT_DOWN`` event
        :param `event`: a :class:`MouseEvent` event to be processed.
        """
        evt_id = event.GetId()
        bar = None
        active_button = 0
        for item in self.ribbon_bars:
            item_id = item.GetId()
            if item_id == evt_id:
                bar = item
                # Now look for the corresponding buttons...
                if not bar._hovered_button is None:
                    # print ("Hovered button: %d" % bar._hovered_button.base.id)
                    active_button = bar._hovered_button.base.id
                break
        if bar is None or active_button == 0:
            # Nothing found
            return

        # We know the active button. Lookup and execute action_right
        button = self.button_lookup.get(active_button)
        if button is not None:
            action = button.action_right
            if action:
                action(event)

    def button_click(self, event):
        # Let's figure out what kind of action we need to perform
        evt_id = event.GetId()
        button = self.button_lookup.get(evt_id)
        if button is None:
            return

        if button.group:
            # Toggle radio buttons
            button.toggle = not button.toggle
            if button.toggle:  # got toggled
                button_group = self.group_lookup.get(button.group, [])

                for obutton in button_group:
                    # Untoggle all other buttons in this group.
                    if obutton.group == button.group and obutton.id != button.id:
                        obutton.parent.ToggleButton(obutton.id, False)
            else:  # got untoggled...
                # so let' activate the first button of the group (implicitly defined as default...)
                button_group = self.group_lookup.get(button.group)
                if button_group:
                    first_button = button_group[0]
                    first_button.parent.ToggleButton(first_button.id, True)

                    # Clone event and recurse.
                    mevent = event.Clone()
                    mevent.SetId(first_button.id)
                    self.button_click(mevent)
                    return
        if button.action is not None:
            # We have an action to call.
            button.action(event)

        if button.state_pressed is None:
            # If there's a pressed state we should change the button state
            return
        button.toggle = not button.toggle
        if button.toggle:
            self._restore_button_aspect(button, button.state_pressed)
        else:
            self._restore_button_aspect(button, button.state_unpressed)
        self.ensure_realize()

    def drop_click(self, event):
        """
        Drop down of a hybrid button was clicked.

        We make a menu popup and fill it with the data about the multi-button

        @param event:
        @return:
        """
        evt_id = event.GetId()
        button = self.button_lookup.get(evt_id)
        if button is None:
            return
        if button.toggle:
            return
        menu = wx.Menu()
        for v in button.button_dict["multi"]:
            menu_id = wx.NewId()
            menu.Append(menu_id, v.get("label"))
            self.Bind(wx.EVT_MENU, self.drop_menu_click(button, v), id=menu_id)
        event.PopupMenu(menu)

    def drop_menu_click(self, button, v):
        """
        Creates menu_item_click processors for the various menus created for a drop-click

        @param button:
        @param v:
        @return:
        """
        def menu_item_click(event):
            """
            Process menu item click.

            @param event:
            @return:
            """
            key_id = v.get("identifier")
            setattr(self.context, button.save_id, key_id)
            button.state_unpressed = key_id
            self._restore_button_aspect(button, key_id)
            self.ensure_realize()

        return menu_item_click

    def _restore_button_aspect(self, base_button, key):
        if not hasattr(base_button, "alternatives"):
            return
        alt = base_button.alternatives[key]
        base_button.action = alt.get("action", base_button.action)
        base_button.label = alt.get("label", base_button.label)
        base_button.help_string = alt.get("help_string", base_button.help_string)
        base_button.bitmap_large = alt.get("bitmap_large", base_button.bitmap_large)
        base_button.bitmap_large_disabled = alt.get(
            "bitmap_large_disabled", base_button.bitmap_large_disabled
        )
        base_button.bitmap_small = alt.get("bitmap_small", base_button.bitmap_small)
        base_button.bitmap_small_disabled = alt.get(
            "bitmap_small_disabled", base_button.bitmap_small_disabled
        )
        base_button.client_data = alt.get("client_data", base_button.client_data)
        # base_button.id = alt.get("id", base_button.id)
        # base_button.kind = alt.get("kind", base_button.kind)
        # base_button.state = alt.get("state", base_button.state)
        base_button.key = key

    def _store_button_aspect(self, base_button, key, **kwargs):
        if not hasattr(base_button, "alternatives"):
            base_button.alternatives = {}
        base_button.alternatives[key] = {
            "action": base_button.action,
            "label": base_button.label,
            "help_string": base_button.help_string,
            "bitmap_large": base_button.bitmap_large,
            "bitmap_large_disabled": base_button.bitmap_large_disabled,
            "bitmap_small": base_button.bitmap_small,
            "bitmap_small_disabled": base_button.bitmap_small_disabled,
            "client_data": base_button.client_data,
            # "id": base_button.id,
            # "kind": base_button.kind,
            # "state": base_button.state,
        }
        key_dict = base_button.alternatives[key]
        for k in kwargs:
            if kwargs[k] is not None:
                key_dict[k] = kwargs[k]

    def _update_button_aspect(self, base_button, key, **kwargs):
        if not hasattr(base_button, "alternatives"):
            base_button.alternatives = {}
        key_dict = base_button.alternatives[key]
        for k in kwargs:
            if kwargs[k] is not None:
                key_dict[k] = kwargs[k]

    def set_buttons(self, new_values, button_bar):
        show_tip = not self.context.disable_tool_tips
        button_bar._current_layout = 0
        button_bar._hovered_button = None
        button_bar._active_button = None
        button_bar.ClearButtons()
        buttons = []
        for button, name, sname in new_values:
            buttons.append(button)

        def sort_priority(elem):
            return elem.get("priority", 0)
        buttons.sort(key=sort_priority)  # Sort buttons by priority

        for button in buttons:
            # Every registered button in the updated lookup gets created.
            new_id = wx.NewId()
            group = button.get("group")
            resize_param = button.get("size")
            if "multi" in button:
                # Button is a multi-type button
                b = button_bar.AddHybridButton(
                    button_id=new_id,
                    label=button["label"],
                    bitmap=button["icon"].GetBitmap(resize=resize_param),
                    help_string=button["tip"] if show_tip else "",
                )
                button_bar.Bind(
                    RB.EVT_RIBBONBUTTONBAR_DROPDOWN_CLICKED,
                    self.drop_click,
                    id=new_id,
                )
            else:
                if "group" in button:
                    bkind = RB.RIBBON_BUTTON_TOGGLE
                else:
                    bkind = RB.RIBBON_BUTTON_NORMAL
                if "toggle" in button:
                    bkind = RB.RIBBON_BUTTON_TOGGLE
                b = button_bar.AddButton(
                    button_id=new_id,
                    label=button["label"],
                    bitmap=button["icon"].GetBitmap(resize=resize_param),
                    bitmap_disabled=button["icon"].GetBitmap(
                        resize=resize_param, color=Color("grey")
                    ),
                    help_string=button["tip"] if show_tip else "",
                    kind=bkind,
                )

            # Store all relevant aspects for newly registered button.
            b.button_dict = button
            b.state_pressed = None
            b.state_unpressed = None
            b.toggle = False
            b.parent = button_bar
            b.group = group
            b.identifier = button.get("identifier")
            b.action = button.get("action")
            b.action_right = button.get("right")
            if "rule_enabled" in button:
                b.enable_rule = button.get("rule_enabled")
            else:
                b.enable_rule = lambda cond: True

            if "multi" in button:
                # Store alternative aspects for multi-buttons, load stored previous state.

                multi_action = button["multi"]
                multi_ident = button.get("identifier")
                b.save_id = multi_ident
                initial_id = self.context.setting(str, b.save_id, "default")

                for i, v in enumerate(multi_action):
                    key = v.get("identifier", i)
                    self._store_button_aspect(b, key)
                    self._update_button_aspect(b, key, **v)
                    if "icon" in v:
                        v_icon = button.get("icon")
                        self._update_button_aspect(
                            b,
                            key,
                            bitmap_large=v_icon.GetBitmap(resize=resize_param),
                            bitmap_large_disabled=v_icon.GetBitmap(
                                resize=resize_param, color=Color("grey")
                            ),
                        )
                    if key == initial_id:
                        self._restore_button_aspect(b, key)
            if "toggle" in button:
                # Store toggle and original aspects for toggle-buttons

                b.state_pressed = "toggle"
                b.state_unpressed = "original"

                self._store_button_aspect(b, "original")

                toggle_action = button["toggle"]
                key = toggle_action.get("identifier", "toggle")
                self._store_button_aspect(
                    b,
                    key,
                    **toggle_action
                )
                if "icon" in toggle_action:
                    toggle_icon = toggle_action.get("icon")
                    self._update_button_aspect(
                        b,
                        key,
                        bitmap_large=toggle_icon.GetBitmap(resize=resize_param),
                        bitmap_large_disabled=toggle_icon.GetBitmap(
                            resize=resize_param, color=Color("grey")
                        ),
                    )

            # Store newly created button in the various lookups
            self.button_lookup[new_id] = b
            if group is not None:
                c_group = self.group_lookup.get(group)
                if c_group is None:
                    c_group = []
                    self.group_lookup[group] = c_group
                c_group.append(b)

            button_bar.Bind(
                RB.EVT_RIBBONBUTTONBAR_CLICKED, self.button_click, id=new_id
            )
            button_bar.Bind(wx.EVT_RIGHT_UP, self.button_click_right)

        self.ensure_realize()
        # Disable buttons by default
        self.apply_enable_rules()

    def apply_enable_rules(self):
        for k in self.button_lookup:
            v = self.button_lookup[k]
            try:
                enable_it = v.enable_rule(0)
            except:
                enable_it = True
            v.parent.EnableButton(v.id, enable_it)

    @lookup_listener("button/project")
    def set_project_buttons(self, new_values, old_values):
        self.set_buttons(new_values, self.project_button_bar)

    @lookup_listener("button/control")
    def set_control_buttons(self, new_values, old_values):
        self.set_buttons(new_values, self.control_button_bar)

    @lookup_listener("button/config")
    def set_config_buttons(self, new_values, old_values):
        self.set_buttons(new_values, self.config_button_bar)

    @lookup_listener("button/modify")
    def set_modify_buttons(self, new_values, old_values):
        self.set_buttons(new_values, self.modify_button_bar)

    @lookup_listener("button/tool")
    def set_tool_buttons(self, new_values, old_values):
        self.set_buttons(new_values, self.tool_button_bar)

    @lookup_listener("button/geometry")
    def set_geometry_buttons(self, new_values, old_values):
        self.set_buttons(new_values, self.geometry_button_bar)

    @lookup_listener("button/align")
    def set_align_buttons(self, new_values, old_values):
        self.set_buttons(new_values, self.align_button_bar)

    @signal_listener("emphasized")
    def on_emphasis_change(self, origin, *args):
        self.apply_enable_rules()

    @signal_listener("selected")
    def on_selected_change(self, origin, node=None, *args):
        self.apply_enable_rules()

    # @signal_listener("ribbonbar")
    # def on_rb_toggle(self, origin, showit, *args):
    #     self._ribbon.ShowPanels(True)

    @signal_listener("tool_changed")
    def on_tool_changed(self, origin, newtool=None, *args):
        # Signal provides a tuple with (togglegroup, id)
        if newtool is None:
            return
        if isinstance(newtool, (list, tuple)):
            group = newtool[0].lower() if newtool[0] is not None else ""
            identifier = newtool[1].lower() if newtool[1] is not None else ""
        else:
            group = newtool
            identifier = ""

        button_group = self.group_lookup.get(group, [])
        for button in button_group:
            # Reset toggle state
            if button.identifier == identifier:
                # Set toggle state
                button.parent.ToggleButton(button.id, True)
                button.toggle = True
            else:
                button.parent.ToggleButton(button.id, False)
                button.toggle = False

    @property
    def is_dark(self):
        # wxPython's SysAppearance does not always deliver a reliable response from
        # wx.SystemSettings().GetAppearance().IsDark()
        # so lets tick with 'old way', although this one is fishy...
        result = wx.SystemSettings().GetColour(wx.SYS_COLOUR_WINDOW)[0] < 127
        return result

    def ensure_realize(self):
        self._ribbon_dirty = True
        self.context.schedule(self._job)

    def _perform_realization(self, *args):
        self._ribbon_dirty = False
        self._ribbon.Realize()

    def __set_ribbonbar(self):
        self.ribbonbar_caption_visible = False

        if self.is_dark:
            provider = self._ribbon.GetArtProvider()
            _update_ribbon_artprovider_for_dark_mode(provider)
        self.ribbon_position_aspect_ratio = True
        self.ribbon_position_ignore_update = False

        home = RB.RibbonPage(
            self._ribbon,
            ID_PAGE_MAIN,
            _("Home"),
            icons8_opened_folder_50.GetBitmap(resize=16),
        )
        self.ribbon_pages.append(home)
        # self.Bind(
        #    RB.EVT_RIBBONBAR_HELP_CLICK,
        #    lambda e: self.context("webhelp help\n"),
        # )

        self.project_panel = RB.RibbonPanel(
            home,
            wx.ID_ANY,
            "" if self.is_dark else _("Project"),
            agwStyle=RB.RIBBON_PANEL_MINIMISE_BUTTON,
        )
        self.ribbon_panels.append(self.project_panel)

        button_bar = RibbonButtonBar(self.project_panel)
        self.project_button_bar = button_bar
        self.ribbon_bars.append(button_bar)

        self.control_panel = RB.RibbonPanel(
            home,
            wx.ID_ANY,
            "" if self.is_dark else _("Control"),
            icons8_opened_folder_50.GetBitmap(),
            agwStyle=RB.RIBBON_PANEL_MINIMISE_BUTTON,
        )
        self.ribbon_panels.append(self.control_panel)

        button_bar = RibbonButtonBar(self.control_panel)
        self.control_button_bar = button_bar
        self.ribbon_bars.append(button_bar)

        self.config_panel = RB.RibbonPanel(
            home,
            wx.ID_ANY,
            "" if self.is_dark else _("Configuration"),
            icons8_opened_folder_50.GetBitmap(),
            agwStyle=RB.RIBBON_PANEL_MINIMISE_BUTTON,
        )
        self.ribbon_panels.append(self.config_panel)

        button_bar = RibbonButtonBar(self.config_panel)
        self.config_button_bar = button_bar
        self.ribbon_bars.append(button_bar)

        tool = RB.RibbonPage(
            self._ribbon,
            ID_PAGE_TOOL,
            _("Tools"),
            icons8_opened_folder_50.GetBitmap(resize=16),
        )
        self.ribbon_pages.append(tool)

        self.tool_panel = RB.RibbonPanel(
            tool,
            wx.ID_ANY,
            "" if self.is_dark else _("Tools"),
            icons8_opened_folder_50.GetBitmap(),
            agwStyle=RB.RIBBON_PANEL_MINIMISE_BUTTON,
        )
        self.ribbon_panels.append(self.tool_panel)

        button_bar = RibbonButtonBar(self.tool_panel)
        self.tool_button_bar = button_bar
        self.ribbon_bars.append(button_bar)

        self.modify_panel = RB.RibbonPanel(
            tool,
            wx.ID_ANY,
            "" if self.is_dark else _("Modification"),
            icons8_opened_folder_50.GetBitmap(),
            agwStyle=RB.RIBBON_PANEL_MINIMISE_BUTTON,
        )
        self.ribbon_panels.append(self.modify_panel)

        button_bar = RibbonButtonBar(self.modify_panel)
        self.modify_button_bar = button_bar
        self.ribbon_bars.append(button_bar)

        self.geometry_panel = RB.RibbonPanel(
            tool,
            wx.ID_ANY,
            "" if self.is_dark else _("Geometry"),
            icons8_opened_folder_50.GetBitmap(),
            agwStyle=RB.RIBBON_PANEL_MINIMISE_BUTTON,
        )
        self.ribbon_panels.append(self.geometry_panel)
        button_bar = RibbonButtonBar(self.geometry_panel)
        self.geometry_button_bar = button_bar
        self.ribbon_bars.append(button_bar)

        self.align_panel = RB.RibbonPanel(
            tool,
            wx.ID_ANY,
            "" if self.is_dark else _("Alignment"),
            icons8_opened_folder_50.GetBitmap(),
            agwStyle=RB.RIBBON_PANEL_MINIMISE_BUTTON,
        )
        self.ribbon_panels.append(self.align_panel)
        button_bar = RibbonButtonBar(self.align_panel)
        self.align_button_bar = button_bar
        self.ribbon_bars.append(button_bar)

        # self._ribbon.Bind(RB.EVT_RIBBONBAR_PAGE_CHANGING, self.on_page_changing)
        # minmaxpage = RB.RibbonPage(self._ribbon, ID_PAGE_TOGGLE, "Click me")
        # self.ribbon_pages.append(minmaxpage)
        self._ribbon.Bind(RB.EVT_RIBBONBAR_PAGE_CHANGED, self.on_page_changed)

        self.ensure_realize()

    def pane_show(self):
        pass

    def pane_hide(self):
        pass

    # def on_page_changing(self, event):
    #     page = event.GetPage()
    #     p_id = page.GetId()
    #     # print ("Page Changing to ", p_id)
    #     if p_id  == ID_PAGE_TOGGLE:
    #         slist = debug_system_colors()
    #         msg = ""
    #         for s in slist:
    #             msg += s + "\n"
    #         wx.MessageBox(msg, "Info", wx.OK | wx.ICON_INFORMATION)
    #         event.Veto()

    def on_page_changed(self, event):
        page = event.GetPage()
        p_id = page.GetId()
        if p_id != ID_PAGE_TOOL:
            self.context("tool none\n")
        event.Skip()


# RIBBON_ART_BUTTON_BAR_LABEL_COLOUR = 16
# RIBBON_ART_BUTTON_BAR_HOVER_BORDER_COLOUR = 17
# RIBBON_ART_BUTTON_BAR_ACTIVE_BORDER_COLOUR = 22
# RIBBON_ART_GALLERY_BORDER_COLOUR = 27
# RIBBON_ART_GALLERY_BUTTON_ACTIVE_FACE_COLOUR = 40
# RIBBON_ART_GALLERY_ITEM_BORDER_COLOUR = 45
# RIBBON_ART_TAB_LABEL_COLOUR = 46
# RIBBON_ART_TAB_SEPARATOR_COLOUR = 47
# RIBBON_ART_TAB_SEPARATOR_GRADIENT_COLOUR = 48
# RIBBON_ART_TAB_BORDER_COLOUR = 59
# RIBBON_ART_PANEL_BORDER_COLOUR = 60
# RIBBON_ART_PANEL_BORDER_GRADIENT_COLOUR = 61
# RIBBON_ART_PANEL_MINIMISED_BORDER_COLOUR = 62
# RIBBON_ART_PANEL_MINIMISED_BORDER_GRADIENT_COLOUR = 63
# RIBBON_ART_PANEL_LABEL_COLOUR = 66
# RIBBON_ART_PANEL_HOVER_LABEL_BACKGROUND_COLOUR = 67
# RIBBON_ART_PANEL_HOVER_LABEL_BACKGROUND_GRADIENT_COLOUR = 68
# RIBBON_ART_PANEL_HOVER_LABEL_COLOUR = 69
# RIBBON_ART_PANEL_MINIMISED_LABEL_COLOUR = 70
# RIBBON_ART_PANEL_BUTTON_FACE_COLOUR = 75
# RIBBON_ART_PANEL_BUTTON_HOVER_FACE_COLOUR = 76
# RIBBON_ART_PAGE_BORDER_COLOUR = 77

# RIBBON_ART_TOOLBAR_BORDER_COLOUR = 86
# RIBBON_ART_TOOLBAR_HOVER_BORDER_COLOUR = 87
# RIBBON_ART_TOOLBAR_FACE_COLOUR = 88


def _update_ribbon_artprovider_for_dark_mode(provider):
    def _set_ribbon_colour(provider, art_id_list, colour):
        for id_ in art_id_list:
            try:
                provider.SetColour(id_, colour)
            except:
                # Not all colorcodes are supported by all providers.
                # So lets ignore it
                pass

    TEXTCOLOUR = wx.SystemSettings().GetColour(wx.SYS_COLOUR_BTNTEXT)

    BTNFACE_HOVER = copy.copy(wx.SystemSettings().GetColour(wx.SYS_COLOUR_HIGHLIGHT))
    INACTIVE_BG = copy.copy(
        wx.SystemSettings().GetColour(wx.SYS_COLOUR_INACTIVECAPTION)
    )
    INACTIVE_TEXT = copy.copy(wx.SystemSettings().GetColour(wx.SYS_COLOUR_GRAYTEXT))
    TOOLTIP_FG = copy.copy(wx.SystemSettings().GetColour(wx.SYS_COLOUR_INFOTEXT))
    TOOLTIP_BG = copy.copy(wx.SystemSettings().GetColour(wx.SYS_COLOUR_INFOBK))
    BTNFACE = copy.copy(wx.SystemSettings().GetColour(wx.SYS_COLOUR_BTNFACE))
    BTNFACE_HOVER = BTNFACE_HOVER.ChangeLightness(50)
    HIGHLIGHT = copy.copy(wx.SystemSettings().GetColour(wx.SYS_COLOUR_HOTLIGHT))

    texts = [
        RB.RIBBON_ART_BUTTON_BAR_LABEL_COLOUR,
        RB.RIBBON_ART_PANEL_LABEL_COLOUR,
    ]
    _set_ribbon_colour(provider, texts, TEXTCOLOUR)
    disabled = [
        RB.RIBBON_ART_GALLERY_BUTTON_DISABLED_FACE_COLOUR,
        RB.RIBBON_ART_TAB_LABEL_COLOUR,
    ]
    _set_ribbon_colour(provider, disabled, INACTIVE_TEXT)

    backgrounds = [
        # Toolbar element backgrounds
        RB.RIBBON_ART_TOOL_BACKGROUND_TOP_COLOUR,
        RB.RIBBON_ART_TOOL_BACKGROUND_TOP_GRADIENT_COLOUR,
        RB.RIBBON_ART_TOOL_BACKGROUND_COLOUR,
        RB.RIBBON_ART_TOOL_BACKGROUND_GRADIENT_COLOUR,
        RB.RIBBON_ART_TOOL_HOVER_BACKGROUND_TOP_COLOUR,
        RB.RIBBON_ART_TOOL_HOVER_BACKGROUND_TOP_GRADIENT_COLOUR,
        RB.RIBBON_ART_TOOL_HOVER_BACKGROUND_COLOUR,
        RB.RIBBON_ART_TOOL_HOVER_BACKGROUND_GRADIENT_COLOUR,
        RB.RIBBON_ART_TOOL_ACTIVE_BACKGROUND_TOP_COLOUR,
        RB.RIBBON_ART_TOOL_ACTIVE_BACKGROUND_TOP_GRADIENT_COLOUR,
        RB.RIBBON_ART_TOOL_ACTIVE_BACKGROUND_COLOUR,
        RB.RIBBON_ART_TOOL_ACTIVE_BACKGROUND_GRADIENT_COLOUR,
        # Page Background
        RB.RIBBON_ART_PAGE_BACKGROUND_TOP_COLOUR,
        RB.RIBBON_ART_PAGE_BACKGROUND_TOP_GRADIENT_COLOUR,
        RB.RIBBON_ART_PAGE_BACKGROUND_COLOUR,
        RB.RIBBON_ART_PAGE_BACKGROUND_GRADIENT_COLOUR,
        RB.RIBBON_ART_PAGE_HOVER_BACKGROUND_TOP_COLOUR,
        RB.RIBBON_ART_PAGE_HOVER_BACKGROUND_TOP_GRADIENT_COLOUR,
        RB.RIBBON_ART_PAGE_HOVER_BACKGROUND_COLOUR,
        RB.RIBBON_ART_PAGE_HOVER_BACKGROUND_GRADIENT_COLOUR,
        # Art Gallery
        RB.RIBBON_ART_GALLERY_HOVER_BACKGROUND_COLOUR,
        RB.RIBBON_ART_GALLERY_BUTTON_BACKGROUND_COLOUR,
        RB.RIBBON_ART_GALLERY_BUTTON_BACKGROUND_GRADIENT_COLOUR,
        RB.RIBBON_ART_GALLERY_BUTTON_BACKGROUND_TOP_COLOUR,
        RB.RIBBON_ART_GALLERY_BUTTON_FACE_COLOUR,
        RB.RIBBON_ART_GALLERY_BUTTON_HOVER_BACKGROUND_COLOUR,
        RB.RIBBON_ART_GALLERY_BUTTON_HOVER_BACKGROUND_GRADIENT_COLOUR,
        RB.RIBBON_ART_GALLERY_BUTTON_HOVER_BACKGROUND_TOP_COLOUR,
        RB.RIBBON_ART_GALLERY_BUTTON_HOVER_FACE_COLOUR,
        RB.RIBBON_ART_GALLERY_BUTTON_ACTIVE_BACKGROUND_COLOUR,
        RB.RIBBON_ART_GALLERY_BUTTON_ACTIVE_BACKGROUND_GRADIENT_COLOUR,
        RB.RIBBON_ART_GALLERY_BUTTON_ACTIVE_BACKGROUND_TOP_COLOUR,
        # Panel backgrounds
        RB.RIBBON_ART_PANEL_ACTIVE_BACKGROUND_COLOUR,
        RB.RIBBON_ART_PANEL_ACTIVE_BACKGROUND_GRADIENT_COLOUR,
        RB.RIBBON_ART_PANEL_ACTIVE_BACKGROUND_TOP_COLOUR,
        RB.RIBBON_ART_PANEL_ACTIVE_BACKGROUND_TOP_GRADIENT_COLOUR,
        RB.RIBBON_ART_PANEL_LABEL_BACKGROUND_COLOUR,
        RB.RIBBON_ART_PANEL_LABEL_BACKGROUND_GRADIENT_COLOUR,
        RB.RIBBON_ART_PANEL_HOVER_LABEL_BACKGROUND_COLOUR,
        RB.RIBBON_ART_PANEL_HOVER_LABEL_BACKGROUND_GRADIENT_COLOUR,
        # Tab Background
        RB.RIBBON_ART_TAB_CTRL_BACKGROUND_COLOUR,
        RB.RIBBON_ART_TAB_CTRL_BACKGROUND_GRADIENT_COLOUR,
        RB.RIBBON_ART_TAB_HOVER_BACKGROUND_TOP_COLOUR,
        RB.RIBBON_ART_TAB_HOVER_BACKGROUND_TOP_GRADIENT_COLOUR,
        RB.RIBBON_ART_TAB_HOVER_BACKGROUND_COLOUR,
        RB.RIBBON_ART_TAB_HOVER_BACKGROUND_GRADIENT_COLOUR,
        RB.RIBBON_ART_TAB_ACTIVE_BACKGROUND_TOP_COLOUR,
        RB.RIBBON_ART_TAB_ACTIVE_BACKGROUND_TOP_GRADIENT_COLOUR,
        RB.RIBBON_ART_TAB_ACTIVE_BACKGROUND_COLOUR,
        RB.RIBBON_ART_TAB_ACTIVE_BACKGROUND_GRADIENT_COLOUR,
    ]
    _set_ribbon_colour(provider, backgrounds, BTNFACE)
    highlights = [
        RB.RIBBON_ART_PANEL_HOVER_LABEL_BACKGROUND_COLOUR,
        RB.RIBBON_ART_PANEL_HOVER_LABEL_BACKGROUND_GRADIENT_COLOUR,
    ]
    _set_ribbon_colour(provider, highlights, HIGHLIGHT)
    borders = [
        RB.RIBBON_ART_PANEL_BUTTON_HOVER_FACE_COLOUR,
    ]
    _set_ribbon_colour(provider, borders, wx.RED)

    lowlights = [
        RB.RIBBON_ART_TAB_HOVER_BACKGROUND_TOP_COLOUR,
        RB.RIBBON_ART_TAB_HOVER_BACKGROUND_TOP_GRADIENT_COLOUR,
    ]
    _set_ribbon_colour(provider, lowlights, INACTIVE_BG)
