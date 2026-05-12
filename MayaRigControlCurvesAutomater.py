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
        self.shapes = ["Circle", "Square", "Cube", "Star"]
        self.shape_row_len = 3
        self.total_shape_rows = (len(self.shapes) + 1) // self.shape_row_len
        print("Done")

    def _mk_main_layout(self):
        self.layout = QtWidgets.QVBoxLayout(self)
        self._mk_ui()

    def _mk_ui(self):
        self._mk_header()
        self._mk_shapes_ui()

    def _mk_header(self):
        self._header_label = QtWidgets.QLabel("MR Control Curves Automater",
                                              self)
        self._header_label.setStyleSheet("font-size: 20px; "
                                         "font-weight: bold;")
        self._header_label.setAlignment(QtCore.Qt.AlignCenter)
        self.layout.addWidget(self._header_label)

    def _mk_shapes_ui(self):
        self.shapes_layout = QtWidgets.QGridLayout()
        self.refresh_btn = QtWidgets.QPushButton("REFRESH")
        self.refresh_btn.clicked.connect(self.import_shape_library)
        self.refresh_btn.setStyleSheet("background-color: cyan, "
                                       "font-weight: bold;")
        self.shapes_layout.addWidget(self.refresh_btn, 0, 0)
        for shape_idx in range(len(self.shapes)):
            self._current_btn_name = self.shapes[shape_idx]
            btn = QtWidgets.QPushButton(self._current_btn_name)
            btn.clicked.connect(self._create_shape)
            pos = self._get_row_col(shape_idx)
            self.shapes_layout.addWidget(btn, pos[0], pos[1])
        self.layout.addLayout(self.shapes_layout)

    def _get_row_col(self, idx):
        row = (idx + 1) // 3
        col = (idx + 1) % 3
        return row, col

    def _create_shape(self, degree, points, name):
        print(f"Creating {name} shape")
