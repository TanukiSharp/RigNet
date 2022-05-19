#-------------------------------------------------------------------------------
# This is a copy of file maya_save_fbx.py and adjusted to run in Blender.
# RigNet Copyright 2020 University of Massachusetts
# RigNet is made available under General Public License Version 3 (GPLv3), or under a Commercial License.
# Please see the LICENSE README.txt file in the main directory for more information and instruction on using and licensing RigNet.
#-------------------------------------------------------------------------------
#import maya.cmds as cmds
import sys
import bpy
import time

# BONE_LOCATION_FIRST = 0
# BONE_LOCATION_MIDDLE = 1
# BONE_LOCATION_LAST = 2

class Node(object):
    def __init__(self, name, position):
        self.name = name
        self.position = position
        self.children = []
        self.parent = None

    def add_child(self, child_node):
        if child_node.parent is not None:
            raise Exception('Child node must not already have a parent node.')
        self.children.append(child_node)
        child_node.parent = self

    def attach_to_parent(self, parent_node):
        if self.parent is not None:
            raise Exception('Node must not already have a parent node.')
        parent_node.append(self)
        self.parent = parent_node

    def print(self, indentation = 0):
        indentation_str = ' ' * indentation * 4
        print(f'{indentation_str}{self.name}')
        for child in self.children:
            child.print(indentation + 1)

def compute_square_distance(a, b):
    dx = abs(a[0] - b[0])
    dy = abs(a[1] - b[1])
    dz = abs(a[2] - b[2])
    return dx * dx + dy * dy + dz * dz

def find_closest_child_node(node):
    smallest_distance = sys.float_info.max
    closest_node = None

    for child_node in node.children:
        distance = compute_square_distance(node.position, child_node.position)
        if distance < smallest_distance:
            smallest_distance = distance
            closest_node = child_node

    return closest_node


# def create_bone(armature, name, position):
#     bone = armature.edit_bones.new(name)
#     bone.head = position
#     bone.tail = position
#     return bone

# def create_child_bone(armature, parent_bone, name, position):
#     bone = create_bone(armature, name, position)
#     bone.parent = parent_bone
#     bone.use_connect = True
#     return bone

# def create_first_bone(armature, name, source_position, target_position):
#     current_bone = armature.edit_bones.new(name)

#     # create bone at armature origin and set its length
#     current_bone.head = source_position
#     #length = list(bones.values())[i+1][0][1]
#     current_bone.tail = target_position

#     # rotate bone
#     #quat_armature_space = Quaternion(bone[1][1])
#     #current_bone.transform(quat_armature_space.to_matrix())

#     # set position
#     #current_bone.translate(Vector(bone[1][0]))

#     # save bone, its tail position (next bone will be moved to it) and quaternion rotation
#     parent_bone = current_bone
#     parent_bone_tail = current_bone.tail
#     parent_bone_quat_armature_space = quat_armature_space


# def create_bone(location, name, position):


# armature = bpy.data.armatures.new("Armature")
# rig = bpy.data.objects.new("Armature", armature)
# bpy.context.scene.collection.objects.link(rig)

# bpy.context.view_layer.objects.active = rig
# bpy.ops.object.editmode_toggle()

# for i, bone in enumerate(bones.items()):
#     # create new bone
#     current_bone = armature.edit_bones.new(bone[0])

#     # first bone in chain
#     if i == 0:
#         # create bone at armature origin and set its length
#         current_bone.head = [0, 0, 0]
#         length = list(bones.values())[i+1][0][1]
#         current_bone.tail = [0, 0, length]

#         # rotate bone
#         quat_armature_space = Quaternion(bone[1][1])
#         current_bone.transform(quat_armature_space.to_matrix())

#         # set position
#         current_bone.translate(Vector(bone[1][0]))

#         # save bone, its tail position (next bone will be moved to it) and quaternion rotation
#         parent_bone = current_bone
#         parent_bone_tail = current_bone.tail
#         parent_bone_quat_armature_space = quat_armature_space

#     # last bone in chain
#     elif i == (len(bones) - 1):
#         # create bone at armature origin and set its length
#         current_bone.head = [0, 0, 0]
#         current_bone.tail = [0, 0, 1]

#         # rotate bone
#         current_bone_quat_parent_space = Quaternion(bone[1][1])
#         # like matrices, quaternions can be multiplied to accumulate rotational values
#         transform_quat = parent_bone_quat_armature_space @ current_bone_quat_parent_space
#         current_bone.transform(transform_quat.to_matrix())

#         # set position
#         current_bone.translate(Vector(parent_bone_tail))

#         # connect
#         current_bone.parent = parent_bone
#         current_bone.use_connect = True

#     else:
#         # create bone at armature origin and set its length
#         current_bone.head = [0, 0, 0]
#         length = list(bones.values())[i+1][0][1]
#         current_bone.tail = [0, 0, length]

#         # rotate bone
#         current_bone_quat_parent_space = Quaternion(bone[1][1])
#         # like matrices, quaternions can be multiplied to accumulate rotational values
#         transform_quat = parent_bone_quat_armature_space @ current_bone_quat_parent_space
#         current_bone.transform(transform_quat.to_matrix())

#         # set position
#         current_bone.translate(Vector(parent_bone_tail))

#         # connect
#         current_bone.parent = parent_bone
#         current_bone.use_connect = True

#         # save bone, its tail position (next bone will be moved to it) and quaternion rotation
#         parent_bone = current_bone
#         parent_bone_tail = current_bone.tail
#         parent_bone_quat_armature_space = transform_quat

# bpy.ops.object.editmode_toggle()











def load_skeleton_info(rig_filename):
    lines = []

    with open(rig_filename, 'r') as rig_info:
        for line in rig_info:
            lines.append(line.split())

    joint_positions = {}
    joint_skin = []

    for line in lines:
        keyword = line[0]

        if keyword == 'joints':
            joint_name = line[1]
            x = float(line[2])
            y = float(line[3])
            z = float(line[4])
            joint_positions[joint_name] = [x, y, z]

        elif keyword == 'root':
            root_name = line[1]

        elif keyword == 'skin':
            skin_item = line[1:]
            joint_skin.append(skin_item)

    joint_hierarchy = {}
    nodes = {}

    for line in lines:
        keyword = line[0]

        if keyword != 'hier':
            continue

        source_joint_name = line[1]
        target_joint_name = line[2]

        if source_joint_name not in nodes.keys():
            source_node = Node(source_joint_name, joint_positions[source_joint_name])
            nodes[source_joint_name] = source_node

        if target_joint_name not in nodes.keys():
            target_node = Node(target_joint_name, joint_positions[target_joint_name])
            nodes[target_joint_name] = target_node

        nodes[source_joint_name].add_child(nodes[target_joint_name])

    return nodes[root_name], joint_skin


def create_bone(armature, mesh, current_node):
    bone = armature.edit_bones.new(current_node.name)

    # TODO: Need to understand this.
    if bone.name not in mesh.vertex_groups:
        mesh.vertex_groups.new(name=bone.name)

    bone.head.x = current_node.position[0]
    bone.head.y = current_node.position[1]
    bone.head.z = current_node.position[2]

    if current_node.parent:
        bone.parent = armature.edit_bones[current_node.parent.name]
        #if bone.parent.tail == bone.head:
            #print(f'bone.use_connect = True ("{bone.parent.name}", "{bone.name}")')
        bone.use_connect = True
        #else:
        #    print(f'wut!? {bone.parent.name} ({bone.parent.tail}) -> {bone.name} ({bone.head})')

    if len(current_node.children) == 1:
        #print(f'node "{current_node.name}" as only one child ({current_node.children[0].name})')
        child_position = current_node.children[0].position
        bone.tail.x = child_position[0]
        bone.tail.y = child_position[1]
        bone.tail.z = child_position[2]

    elif len(current_node.children) > 1:
        #print(f'node "{current_node.name}" as more than one child')
        closest_node = find_closest_child_node(current_node)
        bone.tail.x = closest_node.position[0]
        bone.tail.y = closest_node.position[1]
        bone.tail.z = closest_node.position[2]

    elif bone.parent:
        offset = bone.head - bone.parent.head
        bone.tail = bone.head + offset / 2

    else:
        raise Exception(f'Node {current_node.name} has no parent and no children.')

    for child_node in current_node.children:
        create_bone(armature, mesh, child_node)


def create_skeleton(armature, mesh, root_node):
    bpy.ops.object.mode_set(mode='EDIT')
    create_bone(armature, mesh, root_node)

    #cmds.joint(root_name, e=True, oj='xyz', sao='yup', ch=True, zso=True)
    #cmds.skinCluster( root_name, geo_name)
    #print len(joint_skin)
    # for i in range(len(joint_skin)):
    #     vtx_name = geo_name + '.vtx['+joint_skin[i][0]+']'
    #     transValue = []
    #     for j in range(1,len(joint_skin[i]),2):
    #         transValue_item = (joint_skin[i][j], float(joint_skin[i][j+1]))
    #         transValue.append(transValue_item)
    #     #print vtx_name, transValue
    #     cmds.skinPercent( 'skinCluster1', vtx_name, transformValue=transValue)
    # cmds.skinPercent( 'skinCluster1', geo_name, pruneWeights=0.01, normalize=False )


# def getGeometryGroups():
#     geo_list = []
#     geometries = cmds.ls(type='surfaceShape')
#     for geo in geometries:
#         if 'ShapeOrig' in geo:
#             '''
#             we can also use cmds.ls(geo, l=True)[0].split("|")[0]
#             to get the upper level node name, but stick on this way for now
#             '''
#             geo_name = geo.replace('ShapeOrig', '')
#             geo_list.append(geo_name)
#     if not geo_list:
#         geo_list = cmds.ls(type='surfaceShape')
#     return geo_list

def create_skinning(rig, mesh, joint_skin):
    bpy.ops.object.mode_set(mode='POSE')

    for skin_parts in joint_skin:
        index = int(skin_parts.pop(0))

        for i in range(0, len(skin_parts), 2):
            name = skin_parts[i]
            weight = float(skin_parts[i + 1])

            mesh.vertex_groups[name].add([index], weight, 'REPLACE')

    rig.matrix_world = mesh.matrix_world
    mod = mesh.modifiers.new('rignet', 'ARMATURE')
    mod.object = rig


if __name__ == '__main__':
    start_time = time.perf_counter()

    #bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.wm.read_homefile(use_empty=True)

    #model_id = "17872"
    #model_id = "smith"
    #print(model_id)
    obj_name = 'D:\\ax\\_customers\\world-scan-project\\RigNet\\quick_start\\tpose_lady1_flr.obj'
    info_name = 'D:\\ax\\_customers\\world-scan-project\\RigNet\\quick_start\\tpose_lady1_flr_rig.txt'
    out_name = 'D:\\ax\\_customers\\world-scan-project\\RigNet\\quick_start\\tpose_lady1_flr_from_blender.fbx'

    root_node, joint_skin = load_skeleton_info(info_name)
    root_node.print()

    # import obj
    #cmds.file(new=True,force=True)
    #cmds.file(obj_name, o=True)

    bpy.ops.import_scene.obj(
        filepath=obj_name,
        # use_edges=True,
        # use_smooth_groups=True,
        # use_groups_as_vgroups=False,
        # use_image_search=True,
        # split_mode='OFF',
        axis_forward='-Z',
        axis_up='Y'
    )

    #print('bpy.data.scenes[0]: ', bpy.data.scenes[0])
    print('bpy.data.objects[0]: ', bpy.data.objects[0])
    print('--------------------------------------------')

    mesh = bpy.data.objects[0]
    mesh.vertex_groups.clear()

    for obj in bpy.data.objects:
        obj.select_set(False)

    armature = bpy.data.armatures.new(f'{mesh.name}_armature')
    rig = bpy.data.objects.new("rignet_rig", armature)
    bpy.context.collection.objects.link(rig)
    bpy.context.view_layer.objects.active = rig

    create_skeleton(armature, mesh, root_node)
    create_skinning(rig, mesh, joint_skin)

    # export fbx
    bpy.ops.export_scene.fbx(filepath=out_name)

    print(f'Done in {time.perf_counter() - start_time:.2f}s')
