# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
import bpy

bl_info = {
    "name": "Geometry-nodes-get-bone-info",
    "author": "SFY",
    "description": "",
    "blender": (2, 80, 0),
    "version": (0, 0, 1),
    "location": "",
    "warning": "",
    "category": "Generic",
}


def Add_to_Node_Menu(self, context):
    if context.area.type == "NODE_EDITOR" and context.space_data.tree_type == "GeometryNodeTree":
        layout = self.layout
        layout.menu("SNA_MT_GEO_NODE_Menu", text="bone info", icon_value=0)


class SNA_MT_GEO_NODE_Menu(bpy.types.Menu):
    bl_idname = "SNA_MT_GEO_NODE_Menu"
    bl_label = "bone info"

    @classmethod
    def poll(cls, context):
        return not (False)

    def draw(self, context):
        layout = self.layout.column_flow(columns=1)
        layout.operator_context = "INVOKE_DEFAULT"
        layout.operator("ops.add_bone_info_node", text="Add Bone Info Node")


class AddBoneInfoNodeOperator(bpy.types.Operator):
    """添加骨骼信息节点组"""

    bl_idname = "ops.add_bone_info_node"  # 操作符 ID
    bl_label = "Add Bone Info Node"  # 按钮上的名称
    bl_options = {"REGISTER", "UNDO"}
    # 属性定义
    blender_version = bpy.app.version

    def create_node_driver(self, driver, type, val_type, target_object, target_path):
        driver.type = type
        driver.expression = "var"
        # 设置驱动器的变量
        variable = driver.variables.new()
        variable.name = "var"  # 变量名
        variable.type = "SINGLE_PROP"  # 变量类型为变换数据
        variable.targets[0].id_type = val_type
        variable.targets[0].id = target_object
        variable.targets[0].data_path = target_path

    def add_vector_node_with_driver(self, node_tree, armature, bone, var_path1, var_path2, var_path3, location=(0, 0)):
        vector_node = node_tree.nodes.new(type="FunctionNodeInputVector")
        vector_node.location = location
        driver = vector_node.driver_add("vector", 0).driver
        driver2 = vector_node.driver_add("vector", 1).driver
        driver3 = vector_node.driver_add("vector", 2).driver
        self.create_node_driver(driver, "SCRIPTED", "OBJECT", armature, var_path1)
        self.create_node_driver(driver2, "SCRIPTED", "OBJECT", armature, var_path2)
        self.create_node_driver(driver3, "SCRIPTED", "OBJECT", armature, var_path3)
        return vector_node

    def add_float_node_with_driver(self, node_tree, armature, bone, var_path, location=(0, 0)):
        float_node = node_tree.nodes.new(type="ShaderNodeValue")
        float_node.location = location
        driver = float_node.outputs[0].driver_add("default_value").driver
        self.create_node_driver(driver, "SCRIPTED", "OBJECT", armature, var_path)
        return float_node

    def creat_node_group(self, bone, armature):
        context = bpy.context
        # 创建一个新的节点组
        group = bpy.data.node_groups.new(type="GeometryNodeTree", name=f"{bone.name}_Info")
        group_input = group.nodes.new("NodeGroupInput")
        group_output = group.nodes.new("NodeGroupOutput")
        group_input.location = (-300, 0)
        group_output.location = (300, 0)

        # # 定义节点组的输入和输出
        if bpy.app.version < (4, 0, 0):
            armature_name_socket = group.inputs.new("NodeSocketString", name=f"_{armature.name}")
            bone_name_socket = group.inputs.new("NodeSocketString", name=f"_{bone.name}")
            armature_name_socket.hide_value = True
            bone_name_socket.hide_value = True

        else:
            armature_name_socket = group.interface.new_socket(name=f"_{armature.name}", socket_type="NodeSocketString", in_out="INPUT")
            bone_name_socket = group.interface.new_socket(name=f"_{bone.name}", socket_type="NodeSocketString", in_out="INPUT")
            armature_name_socket.hide_value = True
            bone_name_socket.hide_value = True
        head_location_node = self.add_vector_node_with_driver(group, armature, bone, f'pose.bones["{bone.name}"].head[0]', f'pose.bones["{bone.name}"].head[1]', f'pose.bones["{bone.name}"].head[2]')
        tail_location_node = self.add_vector_node_with_driver(group, armature, bone, f'pose.bones["{bone.name}"].tail[0]', f'pose.bones["{bone.name}"].tail[1]', f'pose.bones["{bone.name}"].tail[2]', (0, -150))
        rotation_node = self.add_vector_node_with_driver(group, armature, bone, f'pose.bones["{bone.name}"].rotation_euler[0]', f'pose.bones["{bone.name}"].rotation_euler[1]', f'pose.bones["{bone.name}"].rotation_euler[2]', (0, -300))
        length_node = self.add_float_node_with_driver(group, armature, bone, f'pose.bones["{bone.name}"].length', (0, -450))

        if bpy.app.version < (4, 0, 0):
            group.outputs.new("NodeSocketVector", "头部位置")
            group.links.new(head_location_node.outputs[0], group_output.inputs[0])

            group.outputs.new("NodeSocketVector", "尾部位置")
            group.links.new(tail_location_node.outputs[0], group_output.inputs[1])

            group.outputs.new("NodeSocketVector", "欧拉角XYZ")
            group.links.new(rotation_node.outputs[0], group_output.inputs[2])

            group.outputs.new("NodeSocketFloat", "长度")
            group.links.new(length_node.outputs[0], group_output.inputs[3])
        else:
            group.interface.new_socket(name="头部位置", socket_type="NodeSocketVector", in_out="OUTPUT")
            group.links.new(head_location_node.outputs[0], group_output.inputs[0])
            group.interface.new_socket(name="尾部位置", socket_type="NodeSocketVector", in_out="OUTPUT")
            group.links.new(tail_location_node.outputs[0], group_output.inputs[1])
            group.interface.new_socket(name="欧拉角XYZ", socket_type="NodeSocketVector", in_out="OUTPUT")
            group.links.new(rotation_node.outputs[0], group_output.inputs[2])
            group.interface.new_socket(name="长度", socket_type="NodeSocketFloat", in_out="OUTPUT")
            group.links.new(length_node.outputs[0], group_output.inputs[3])

        return group

    def execute(self, context):
        context = bpy.context
        active_bone = context.active_pose_bone
        if not active_bone:
            self.report({"WARNING"}, "没有选中的骨骼")
            return {"CANCELLED"}
        armature = active_bone.id_data
        print(active_bone.name, armature.name)
        self.report({"INFO"}, "Bone name: " + active_bone.name)
        # 确保在几何节点编辑器中操作
        if context.area.type == "NODE_EDITOR" and context.space_data.tree_type == "GeometryNodeTree":
            # 获取活动的节点树
            node_tree = context.space_data.edit_tree
            active_node = bpy.context.active_node
            if node_tree is None:
                self.report({"WARNING"}, "No active node tree")
                return {"CANCELLED"}
            if active_node:
                print(active_node.bl_idname)
            is_repeat = False
            group = None
            node_groups = bpy.data.node_groups
            if bpy.app.version < (4, 0, 0):
                for group_temp in node_groups:
                    if group_temp.bl_idname == "GeometryNodeTree" and group_temp.name == f"{active_bone.name}_Info":
                        if len(group_temp.inputs) == 2 and len(group_temp.outputs) == 4:
                            if group_temp.inputs[0].name == f"_{armature.name}" and group_temp.inputs[1].name == f"_{active_bone.name}":
                                is_repeat = True
                                group = group_temp
                                break
            else:
                for group_temp in node_groups:
                    if group_temp.bl_idname == "GeometryNodeTree" and group_temp.name == f"{active_bone.name}_Info":
                        if len(group_temp.interface.items_tree) == 6:
                            is_repeat = True
                            group = group_temp
            print(is_repeat)
            if not is_repeat:
                group = self.creat_node_group(active_bone, armature)
            # # 在活动的节点树中创建节点组实例
            node_group = node_tree.nodes.new("GeometryNodeGroup")
            node_group.node_tree = group

            # 设置节点组的创建位置为鼠标位置
            mouse_pos = context.space_data.cursor_location
            node_group.location = mouse_pos
            self.report({"INFO"}, "已创建骨骼信息节点组")
            return {"FINISHED"}

        else:
            self.report({"WARNING"}, "Not in Geometry Node Editor")
            return {"CANCELLED"}


panel_list = [
    SNA_MT_GEO_NODE_Menu,
]
operator_list = [
    AddBoneInfoNodeOperator,
]


def register():
    bpy.types.NODE_MT_add.append(Add_to_Node_Menu)
    for panel in panel_list:
        bpy.utils.register_class(panel)
    for operator in operator_list:
        bpy.utils.register_class(operator)


def unregister():
    bpy.types.NODE_MT_add.remove(Add_to_Node_Menu)
    for panel in panel_list:
        bpy.utils.unregister_class(panel)
    for operator in operator_list:
        bpy.utils.unregister_class(operator)
