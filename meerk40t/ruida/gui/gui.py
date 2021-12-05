from meerk40t.gui.icons import icons8_info_50

try:
    import wx
except ImportError as e:
    from meerk40t.core.exceptions import Mk40tImportAbort

    raise Mk40tImportAbort("wxpython")


def plugin(kernel, lifecycle):
    if lifecycle == "service":
        return "provider/device/ruida"
    if lifecycle == "register":
        service = kernel.get_context("ruida0")
        _ = kernel.translation

        def popup_info(event):
            dlg = wx.MessageDialog(
                None,
                _("Ruida Driver is not yet completed."),
                _("Non Implemented Device"),
                wx.OK | wx.ICON_WARNING,
            )
            dlg.ShowModal()
            dlg.Destroy()

        service.register(
            "button/control/Info",
            {
                "label": _("Ruida Info"),
                "icon": icons8_info_50,
                "tip": _("Provide information about the Ruida Driver"),
                "action": popup_info,
            },
        )

    elif lifecycle == "boot":
        service = kernel.get_context("ruida0")
        service.add_service_delegate(RuidaGui(service))


class RuidaGui:
    def __init__(self, context):
        self.context = context
        # This is a stub.
