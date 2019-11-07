# This file is part of project Sverchok. It's copyrighted by the contributors
# recorded in the version control history of the file, available from
# its original location https://github.com/nortikin/sverchok/commit/master
#
# SPDX-License-Identifier: GPL3
# License-Filename: LICENSE


import bpy

from sverchok.node_tree import SverchCustomTreeNode
from sverchok.data_structure import updateNode
from sverchok.utils.geom_2d.merge_mesh import crop_mesh


class SvCropMesh2D(bpy.types.Node, SverchCustomTreeNode):
    """
    Triggers: Crop mesh by another mesh
    Tooltip: Can create holes or crop mesh by boundary contours

    Has hidden output socket, look N panel
    """
    bl_idname = 'SvCropMesh2D'
    bl_label = 'Crop mesh 2D'
    bl_icon = 'MOD_BOOLEAN'

    def update_sockets(self, context):
        [self.outputs.remove(sock) for sock in self.outputs[2:]]
        if self.face_index:
            self.outputs.new('SvStringsSocket', 'Face index')
        updateNode(self, context)

    enum_items = [('inner', 'Inner', 'Fit mesh', 'SELECT_INTERSECT', 0),
                  ('outer', 'Outer', 'Make hole', 'SELECT_SUBTRACT', 1)]

    mode: bpy.props.EnumProperty(items=enum_items, name='Mode of cropping mesh', update=updateNode, 
                                 description='Switch between creating holes and fitting mesh into another mesh')
    face_index: bpy.props.BoolProperty(name="Show face mask", update=update_sockets,
                                       description="Show output socket of index face mask")
    accuracy: bpy.props.IntProperty(name='Accuracy', update=updateNode, default=5, min=3, max=12,
                                    description='Some errors of the node can be fixed by changing this value')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'mode', expand=True)

    def draw_buttons_ext(self, context, layout):
        layout.prop(self, 'face_index', toggle=True)
        layout.prop(self, 'accuracy')

    def sv_init(self, context):
        self.inputs.new('SvVerticesSocket', 'Verts')
        self.inputs.new('SvStringsSocket', "Faces")
        self.inputs.new('SvVerticesSocket', 'Verts Crop')
        self.inputs.new('SvStringsSocket', "Faces Crop")
        self.outputs.new('SvVerticesSocket', 'Verts')
        self.outputs.new('SvStringsSocket', "Faces")

    def process(self):
        if not all([sock.is_linked for sock in self.inputs]):
            return
        out = []
        for sv_verts, sv_faces, sv_verts_crop, sv_faces_crop in zip(self.inputs['Verts'].sv_get(),
                                                                    self.inputs['Faces'].sv_get(),
                                                                    self.inputs['Verts Crop'].sv_get(),
                                                                    self.inputs['Faces Crop'].sv_get()):
            out.append(crop_mesh(sv_verts, sv_faces, sv_verts_crop, sv_faces_crop, self.face_index, self.mode,
                                 self.accuracy))
        if self.face_index:
            out_verts, out_faces, face_index = zip(*out)
            self.outputs['Face index'].sv_set(face_index)
        else:
            out_verts, out_faces = zip(*out)
        self.outputs['Verts'].sv_set(out_verts)
        self.outputs['Faces'].sv_set(out_faces)


def register():
    bpy.utils.register_class(SvCropMesh2D)


def unregister():
    bpy.utils.unregister_class(SvCropMesh2D)
