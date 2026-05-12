import json
import os

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

        self.import_shape_library()
        self._mk_main_layout()

    def import_shape_library(self):
        print("Importing shape library...")
        with open(os.path.join(
                               os.path.dirname(__file__),
                               "shape_library.json"),
                  "r") as f:
            self.shape_library = json.load(f)
        self.shapes = self.shape_library["shapes"]
        self.shape_row_len = 3
        self.total_shape_rows = (len(self.shapes) + 1) // self.shape_row_len
        print("Done")
        print(f"shapes = {self.shapes}")

    def _mk_main_layout(self):
        self.layout = QtWidgets.QVBoxLayout(self)
        self._mk_ui()

    def _mk_ui(self):
        self._mk_header()
        self._mk_h_divider()
        self._mk_shapes_ui()
        self._mk_h_divider()
        self._mk_params_ui()
        self.layout.addStretch()

    def _mk_header(self):
        self._header_label = QtWidgets.QLabel("MR Control Curves Automater",
                                              self)
        self._header_label.setStyleSheet("font-size: 20px; "
                                         "font-weight: bold;")
        self._header_label.setAlignment(QtCore.Qt.AlignCenter)
        self.layout.addWidget(self._header_label)

    def _mk_h_divider(self):
        line = QtWidgets.QFrame()
        line.setFrameShape(QtWidgets.QFrame.HLine)
        line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.layout.addWidget(line)

    def _mk_shapes_ui(self):
        self.shapes_layout = QtWidgets.QGridLayout()
        self.refresh_btn = QtWidgets.QPushButton("REFRESH")
        self.refresh_btn.clicked.connect(self.import_shape_library)
        self.refresh_btn.setStyleSheet("background-color: cyan, "
                                       "font-weight: bold;")
        self.shapes_layout.addWidget(self.refresh_btn, 0, 0)
        for shape_idx in range(len(self.shapes)):
            self._current_btn_name = self.shapes[shape_idx]["Name"]
            btn = QtWidgets.QPushButton(self._current_btn_name)
            btn.clicked.connect(self.create_shape)
            pos = self._get_row_col(shape_idx)
            self.shapes_layout.addWidget(btn, pos[0], pos[1])
        self.layout.addLayout(self.shapes_layout)

    def _mk_params_ui(self):
        self.shape_degree = 0
        self.params_layout = QtWidgets.QFormLayout()

    def _get_row_col(self, shape_idx):
        btn_idx = shape_idx + 1
        row = (btn_idx) // 3
        col = (btn_idx) % 3
        return row, col

    def create_shape(self, name):
        name = self.sender().text()
        shape_data = {}
        for shape in self.shapes:
            if shape["Name"] == name:
                shape_data["Name"] = shape["Name"]
                shape_data["Points"] = shape["Points"]
                break
        shape_data["Degree"] = self.shape_degree
        print(f"shape_data = {shape_data}")
        new_shape = Control_Curve(shape_data)
        new_shape.create()


class Control_Curve():
    def __init__(self, shape_data):
        self.degree = shape_data["Degree"]
        self.points = shape_data["Points"]
        self.shape_name = shape_data["Name"]

    def create(self):
        print(f"Creating: {self.shape_name}")
