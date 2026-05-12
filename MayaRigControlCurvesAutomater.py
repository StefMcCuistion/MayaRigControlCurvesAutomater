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

        self.import_settings()
        self._mk_main_layout()

    def import_settings(self):
        print("Importing settings...")
        with open(os.path.join(
                               os.path.dirname(__file__),
                               "MRCCA_userSettings.json"),
                  "r") as f:
            self.user_settings = json.load(f)
        self.shapes = self.user_settings["shapes"]
        self.group_suffixes = self.user_settings["group_suffixes"]
        self.curve_suffixes = self.user_settings["curve_suffixes"]
        self.shape_row_len = 2
        self.total_shape_rows = (len(self.shapes)) // self.shape_row_len
        print("Done")
        print(f"shapes = {self.shapes}")

    def _mk_main_layout(self):
        self.layout = QtWidgets.QVBoxLayout(self)
        self._mk_main_layout_ui()
        self.layout.addStretch()

    def _mk_main_layout_ui(self):
        self._mk_header()
        self._mk_h_divider(self.layout)
        self._mk_shapes_layout()
        self._mk_h_splitter(self.layout)
        self._mk_h_divider(self.layout)
        self._mk_params_layout()

    def _mk_header(self):
        self._header_label = QtWidgets.QLabel("MR Control Curves Automater",
                                              self)
        self._header_label.setStyleSheet("font-size: 20px; "
                                         "font-weight: bold;")
        self._header_label.setAlignment(QtCore.Qt.AlignCenter)
        self.layout.addWidget(self._header_label)

    def _mk_h_divider(self, layout):
        line = QtWidgets.QFrame()
        line.setFrameShape(QtWidgets.QFrame.HLine)
        line.setFrameShadow(QtWidgets.QFrame.Sunken)
        layout.addWidget(line)

    def _mk_v_divider(self, layout):
        line = QtWidgets.QFrame()
        line.setFrameShape(QtWidgets.QFrame.VLine)
        line.setFrameShadow(QtWidgets.QFrame.Sunken)
        layout.addWidget(line)

    def _mk_h_splitter(self, layout):
        self.splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        layout.addWidget(self.splitter)

    def _mk_shapes_layout(self):
        self.shapes_layout = QtWidgets.QHBoxLayout()
        # self._mk_refresh_btn()
        # self._mk_v_divider(self.shapes_layout)
        self._mk_shape_btns()
        self.layout.insertLayout(2, self.shapes_layout)

    def _mk_shape_btns(self):
        self.shape_btns_layout = QtWidgets.QGridLayout()
        for shape_idx in range(len(self.shapes)):
            self._current_btn_name = self.shapes[shape_idx]["Name"]
            btn = QtWidgets.QPushButton(self._current_btn_name)
            btn.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                              QtWidgets.QSizePolicy.Expanding)
            btn.clicked.connect(self.create_shape)
            pos = self._get_row_col(shape_idx)
            self.shape_btns_layout.addWidget(btn, pos[0], pos[1])
        self.shapes_layout.addLayout(self.shape_btns_layout)

    def _mk_refresh_btn(self):
        self.refresh_btn = QtWidgets.QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self.refresh_shapes)
        self.refresh_btn.setStyleSheet("background-color: cyan, "
                                       "font-weight: bold;")
        self.refresh_btn.setSizePolicy(QtWidgets.QSizePolicy.Fixed,
                                       QtWidgets.QSizePolicy.Expanding)
        self.shapes_layout.addWidget(self.refresh_btn)

    def _mk_params_layout(self):
        self.shape_degree = 0
        self.params_layout = QtWidgets.QFormLayout()
        self._mk_axis_ui()
        self._mk_match_direction_ui()
        self._mk_suffix_ui()
        self._mk_shape_scale_ui()
        self._mk_color_ui()
        self._mk_line_thickness_ui()
        self._mk_group_name_ui()
        self._mk_delete_all_btn()
        self.layout.addLayout(self.params_layout)

    def _mk_axis_ui(self):
        self.axis_layout = QtWidgets.QHBoxLayout()
        self.axis_label = QtWidgets.QLabel("Face Axis:")
        self.axis_combobox = QtWidgets.QComboBox()
        self.axis_combobox.addItems(["X", "Y", "Z"])
        self.axis_layout.addWidget(self.axis_label)
        self.axis_layout.addWidget(self.axis_combobox)
        self.params_layout.addRow(self.axis_layout)

    def _mk_match_direction_ui(self):
        self.match_dir_layout = QtWidgets.QHBoxLayout()
        self.match_dir_layout.addWidget(QtWidgets.QLabel(
            "Match Joint Orientation:"))
        self.match_dir_checkbox = QtWidgets.QCheckBox()
        self.match_dir_checkbox.setChecked(True)
        self.match_dir_layout.addWidget(self.match_dir_checkbox)
        self.params_layout.addRow(self.match_dir_layout)

    def _mk_suffix_ui(self):
        # Group Suffixes
        self.group_suffix_layout = QtWidgets.QHBoxLayout()
        self.group_suffix_label = QtWidgets.QLabel("Group Suffix:")
        self.group_suffix_combobox = QtWidgets.QComboBox()
        self.group_suffix_combobox.addItems(self.group_suffixes)
        self.group_suffix_layout.addWidget(self.group_suffix_label)
        self.group_suffix_layout.addWidget(self.group_suffix_combobox)
        self.params_layout.addRow(self.group_suffix_layout)
        # Control Curve Suffixes
        self.curve_suffix_layout = QtWidgets.QHBoxLayout()
        self.curve_suffix_label = QtWidgets.QLabel("NURBS Curve Suffix:")
        self.curve_suffix_combobox = QtWidgets.QComboBox()
        self.curve_suffix_combobox.addItems(self.curve_suffixes)
        self.curve_suffix_layout.addWidget(self.curve_suffix_label)
        self.curve_suffix_layout.addWidget(self.curve_suffix_combobox)
        self.params_layout.addRow(self.curve_suffix_layout)
        self.params_layout.addRow(self.group_suffix_layout)

    def _mk_shape_scale_ui(self):
        self.scale_layout = QtWidgets.QHBoxLayout()
        self.scale_label = QtWidgets.QLabel("Scale: ")
        self.scale_spinbox = QtWidgets.QDoubleSpinBox()
        self.scale_spinbox.setRange(0.01, 10000.0)
        self.scale_spinbox.setSingleStep(5.0)
        self.scale_spinbox.setValue(15.0)
        self.scale_layout.addWidget(self.scale_label)
        self.scale_layout.addWidget(self.scale_spinbox)
        self.params_layout.addRow(self.scale_layout)

    def _mk_color_ui(self):
        pass

    def _mk_line_thickness_ui(self):
        line_thickness_layout = QtWidgets.QHBoxLayout()
        line_thickness_layout.addWidget(QtWidgets.QLabel(
            "Thick Lines"))
        self.thick_lines_checkbox = QtWidgets.QCheckBox()
        self.thick_lines_checkbox.setChecked(False)
        line_thickness_layout.addWidget(self.thick_lines_checkbox)
        self.params_layout.addRow(line_thickness_layout)

    def _mk_group_name_ui(self):
        pass

    def _mk_delete_all_btn(self):
        pass

    def _get_row_col(self, shape_idx):
        btn_idx = shape_idx
        row = (btn_idx) // self.shape_row_len
        col = (btn_idx) % self.shape_row_len
        return row, col

    def refresh_shapes(self):
        self.import_settings()
        win = Window()
        win.show()
        self.close()

    def create_shape(self, name):
        selection = cmds.ls(selection=True)
        if not selection:
            cmds.warning("Please select one or more joints first.")
            return
        name = self.sender().text()
        shape_data = {}
        for shape in self.shapes:
            if shape["Name"] == name:
                shape_data["Name"] = shape["Name"]
                shape_data["Points"] = shape["Points"]
                break
        shape_data["Axis"] = self.axis_combobox.currentText()
        shape_data["Match Direction"] = not self.match_dir_checkbox.isChecked()
        shape_data["Group Suffix"] = self.group_suffix_combobox.currentText()
        shape_data["Curve Suffix"] = self.curve_suffix_combobox.currentText()
        shape_data["Scale"] = self.scale_spinbox.value()
        shape_data["Thick Lines"] = self.thick_lines_checkbox.isChecked()
        print(f"shape_data = {shape_data}")
        control_curve = ControlCurve(selection, shape_data)
        control_curve._build()


class ControlCurve():
    def __init__(self, selection, shape_data):
        self.selection = selection
        self.shape_name = shape_data["Name"]
        self.group_suffix = shape_data["Group Suffix"]
        self.curve_suffix = shape_data["Curve Suffix"]
        self.axis = shape_data["Axis"]
        self.degree = 1
        self.match_direction = shape_data["Match Direction"]
        self.points = shape_data["Points"]
        self.scale = shape_data["Scale"]
        self.thick_lines = shape_data["Thick Lines"]

    def _build(self):
        self.parent = self._get_controls_grp()
        for selected_obj in self.selection:
            self.selected_obj = selected_obj
            self.name_stem = ""
            for element in selected_obj.split("_")[:-1]:
                self.name_stem += element
                self.name_stem += "_"
            self.name_stem = self.name_stem[:-1]
            self.curve_obj = self._create_curve()
            self._fix_scale()
            self._fix_axis()
            self._fix_thickness()
            self._create_grp()
            self._fix_position_and_orient()
            self._parent()
            self._create_joint_constraint()
            self.parent = self.curve_obj
        self._place_under_master_grp()

    def _create_curve(self):
        if self.points == 0:
            curve_obj = cmds.circle(n=self.name_stem + self.curve_suffix)
            cmds.rotate(0, 90, 90, curve_obj)
        else:
            curve_obj = cmds.curve(p=self.points,
                                   d=self.degree,
                                   n=self.name_stem + self.curve_suffix)
        cmds.FreezeTransformations(curve_obj)
        return curve_obj

    def _fix_scale(self):
        cmds.scale(self.scale, self.scale, self.scale, self.curve_obj)
        cmds.FreezeTransformations(self.curve_obj)

    def _fix_axis(self):
        if self.axis == "X":
            cmds.rotate(0, 0, 90, self.curve_obj, a=True)
        elif self.axis == "Z":
            cmds.rotate(90, 0, 0, self.curve_obj, a=True)
        cmds.FreezeTransformations(self.curve_obj)

    def _fix_thickness(self):
        if self.thick_lines:
            for s in cmds.listRelatives(self.curve_obj, s=True):
                cmds.setAttr(s + ".lineWidth", 4)

    def _fix_position_and_orient(self):
        constraint = cmds.parentConstraint(self.selected_obj,
                                           self.grp, mo=False)[0]
        cmds.delete(constraint)
        if self.match_direction:
            cmds.rotate(0, 0, 0, self.grp, a=True)

    def _create_grp(self):
        self.grp = cmds.group(n=self.name_stem + self.group_suffix,
                              empty=True)
        cmds.parent(self.curve_obj, self.grp)

    def _get_controls_grp(self):
        controls_grp = cmds.ls("controls")
        if not controls_grp:
            controls_grp = cmds.group(n="controls", empty=True)
        return controls_grp

    def _parent(self):
        cmds.parent(self.grp, self.parent)

    def _create_joint_constraint(self):
        cmds.parentConstraint(self.curve_obj, self.selected_obj, mo=True)

    def _place_under_master_grp(self):
        master_grp = cmds.ls("master")
        if not master_grp:
            master_grp = cmds.group(n="master", empty=True)
        controls_grp = self._get_controls_grp()
        print(f"controls_grp = {controls_grp}")
        cmds.parent(controls_grp, master_grp)
