import maya.cmds as cmds
import maya.OpenMayaUI as omui
from PySide6 import QtWidgets, QtCore
from shiboken6 import wrapInstance


def get_maya_main_win():
    """Return the Maya main window"""
    main_win_addr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_win_addr), QtWidgets.QWidget)


class Window(QtWidgets.QDialog):

    def __init__(self):
        super().__init__(parent=get_maya_main_win())
        self.setWindowTitle("Control Curves Automater")
        self.resize(300, 400)
        self._mk_main_layout()

    def _mk_main_layout(self):
        self._layout = QtWidgets.QVBoxLayout(self)
        # make UI
        # header label
        self._header_label = QtWidgets.QLabel("MR Control Curves Automater",
                                              self)
        self._header_label.setStyleSheet("font-size: 20px; "
                                         "font-weight: bold;")
        self._header_label.setAlignment(QtCore.Qt.AlignCenter)
        self._layout.addWidget(self._header_label)
