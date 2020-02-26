bl_info = {
    "name": "Window Generator",
    "description": "Generate Window Arrays",
    "author": "Austin Jacob",
    "version": (1, 0, 0),
    "blender": (2, 79, 0),
    "location": "View3D > Add > Mesh",
    "warning": "", # used for warning icon and text in addons panel
    "wiki_url": "",
    "tracker_url": "",
    "category": "Add Mesh"}

import bpy
import bmesh

from bpy.props import (
        BoolProperty,
        BoolVectorProperty,
        FloatProperty,
        FloatVectorProperty,
        IntProperty,
        EnumProperty,
        )

class AddWindows(bpy.types.Operator):
    """Add an array of windows to a mesh"""
    bl_idname = "mesh.windows_add"
    bl_label = "Add Windows"
    bl_options = {'REGISTER', 'UNDO'}

    length = FloatProperty(
            name="Length",
            description="Window Length",
            min=0.01,
            default=2,
            )
    width = FloatProperty(
            name="Width",
            description="Window Width",
            min=0.01,
            default=0.325,
            )
    height = FloatProperty(
            name="Height",
            description="Window Height",
            min=0.01,
            default=1.5,
            )
    thick = FloatProperty(
            name="Thickness",
            description="How thick each window pane is",
            min=0.01,
            default=0.05,
            )
    #No boxes can touch because then booleans don't work
    #So shift minimums can never quite be 0.
    x_shift = FloatProperty(
            name="Distance Apart (X)",
            description="How far apart each window is on the x-axis",
            min=0.0001,
            default=0.0001,
            )
    y_shift = FloatProperty(
            name="Distance Apart (Y)",
            description="How far apart each window is on the y-axis",
            min=0.0001,
            default=0.0001,
            )
    x_win = IntProperty(
            name="Windows Per Row",
            description="How many windows per row",
            min=1,
            default=1,
            )
    y_win = IntProperty(
            name="Windows Per Column",
            description="How many windows per column",
            min=1,
            default=1,
            )
    layers = BoolVectorProperty(
            name="Layers",
            description="Object Layers",
            size=20,
            options={'HIDDEN', 'SKIP_SAVE'},
            )

    # generic transform props
    view_align = BoolProperty(
            name="Align to View",
            default=False,
            )
    location = FloatVectorProperty(
            name="Location",
            subtype='TRANSLATION',
            )
    rotation = FloatVectorProperty(
            name="Rotation",
            subtype='EULER',
            )

    def execute(self, context):
        
        #Rename the variables to be easier to work with
        x_win = self.x_win
        y_win = self.y_win
        l = self.length
        w = self.width
        h = self.height
        t = self.thick
        x_shift = self.x_shift
        y_shift = self.y_shift
        x_loc = 0
        y_loc = 0
        loc = self.location
        rot = self.rotation
        
        #Make the window object
        mesh1 = bpy.data.meshes.new("windows")
        windows_obj = bpy.data.objects.new("Windows_Obj", mesh1)

        scene = bpy.context.scene
        scene.objects.link(windows_obj)

        bm1 = bmesh.new()
        verts = [(-(l / 2.0), +(w / 2.0), +(h / 2.0)),
                 (-((l / 2.0) - t), +(w / 2.0), +((h / 2.0) - t)),
                 (+((l / 2.0) - t), +(w / 2.0), +((h / 2.0) - t)),
                 (+(l / 2.0), +(w / 2.0), +(h / 2.0)),
                 (+(l / 2.0), +(w / 2.0), -(h / 2.0)),
                 (+((l / 2.0) - t), +(w / 2.0), -((h / 2.0) - t)),
                 (-((l / 2.0) - t), +(w / 2.0), -((h / 2.0) - t)),
                 (-(l / 2.0), +(w / 2.0), -(h / 2.0)),
                 
                 (-(l / 2.0), -(w / 2.0), +(h / 2.0)),
                 (-((l / 2.0) - t), -(w / 2.0), +((h / 2.0) - t)),
                 (+((l / 2.0) - t), -(w / 2.0), +((h / 2.0) - t)),
                 (+(l / 2.0), -(w / 2.0), +(h / 2.0)),
                 (+(l / 2.0), -(w / 2.0), -(h / 2.0)),
                 (+((l / 2.0) - t), -(w / 2.0), -((h / 2.0) - t)),
                 (-((l / 2.0) - t), -(w / 2.0), -((h / 2.0) - t)),
                 (-(l / 2.0), -(w / 2.0), -(h / 2.0)),
                ]
        
        faces = [(3, 2, 1, 0),
                 (4, 5, 2, 3),
                 (7, 6, 5, 4),
                 (0, 1, 6, 7),
                 (8, 9, 10, 11),
                 (11, 10, 13, 12),
                 (12, 13, 14, 15),
                 (15, 14, 9, 8),
                 (0, 7, 15, 8),
                 (3, 0, 8, 11),
                 (4, 3, 11, 12),
                 (7, 4, 12, 15),
                 (9, 14, 6, 1),
                 (1, 2, 10, 9),
                 (2, 5, 13, 10),
                 (5, 6, 14, 13),
                ]
        
        for v_co in verts:
            bm1.verts.new(v_co)

        bm1.verts.ensure_lookup_table()
        for f_idx in faces:
            bm1.faces.new([bm1.verts[i] for i in f_idx])
        
        bm1.to_mesh(mesh1)
        mesh1.update()
        
        #Apply array modifier twice on the window mesh to make a grid of windows
        x_array = bpy.data.objects[windows_obj.name].modifiers.new(name='x_window_array', type='ARRAY')
        x_array.count = x_win
        x_array.use_relative_offset = False
        x_array.use_constant_offset = True
        x_array.constant_offset_displace = (x_shift + l, 0.0, 0.0)
        
        y_array = bpy.data.objects[windows_obj.name].modifiers.new(name='y_window_array', type='ARRAY')
        y_array.count = y_win
        y_array.use_relative_offset = False
        y_array.use_constant_offset = True
        y_array.constant_offset_displace = (0.0, 0.0, y_shift + h)
        
        #Now make the boolean cutout boxes
        #These boxes are used to cut holes
        #in the wall where the windows fit
        mesh2 = bpy.data.meshes.new("window_boolean")
        window_boolean_obj = bpy.data.objects.new("Window_Boolean_Obj", mesh2)

        scene = bpy.context.scene
        scene.objects.link(window_boolean_obj)

        bm2 = bmesh.new()
        
        verts = [(+(l / 2.0), +w / 2.0, -(h / 2.0)),
                 (+(l / 2.0), -w / 2.0, -(h / 2.0)),
                 (-(l / 2.0), -w / 2.0, -(h / 2.0)),
                 (-(l / 2.0), +w / 2.0, -(h / 2.0)),
                 (+(l / 2.0), +w / 2.0, +(h / 2.0)),
                 (+(l / 2.0), -w / 2.0, +(h / 2.0)),
                 (-(l / 2.0), -w / 2.0, +(h / 2.0)),
                 (-(l / 2.0), +w / 2.0, +(h / 2.0)),
                ]

        faces = [(0, 1, 2, 3),
                 (4, 7, 6, 5),
                 (0, 4, 5, 1),
                 (1, 5, 6, 2),
                 (2, 6, 7, 3),
                 (4, 0, 3, 7),
                ]
        
        for v_co in verts:
            bm2.verts.new(v_co)

        bm2.verts.ensure_lookup_table()
        for f_idx in faces:
            bm2.faces.new([bm2.verts[i] for i in f_idx])
        
        bm2.to_mesh(mesh2)
        mesh2.update()
        
        #Apply array modifier twice to make a grid of window cutouts
        x_array2 = bpy.data.objects[window_boolean_obj.name].modifiers.new(name='x_window_array2', type='ARRAY')
        x_array2.count = x_win
        x_array2.use_relative_offset = False
        x_array2.use_constant_offset = True
        x_array2.constant_offset_displace = (x_shift + l, 0.0, 0.0)
        
        y_array2 = bpy.data.objects[window_boolean_obj.name].modifiers.new(name='y_window_array2', type='ARRAY')
        y_array2.count = y_win
        y_array2.use_relative_offset = False
        y_array2.use_constant_offset = True
        y_array2.constant_offset_displace = (0.0, 0.0, y_shift + h)
        
        #Transform both objects (translate, rotate)
        windows_obj.location = loc
        windows_obj.rotation_euler = rot
        window_boolean_obj.location = loc
        window_boolean_obj.rotation_euler = rot
        
        #Hide the cutout objects to only see the windows
        window_boolean_obj.hide = True
        
        #Apply all array modifiers on both objects
        #Also apply location, rotation, and scale.
        bpy.context.scene.objects.active = windows_obj
        bpy.ops.object.modifier_apply(apply_as='DATA', modifier='x_window_array')
        bpy.ops.object.modifier_apply(apply_as='DATA', modifier='y_window_array')
        bpy.ops.object.transform_apply(location = True, scale = True, rotation = True)
        
        bpy.context.scene.objects.active = window_boolean_obj
        bpy.ops.object.modifier_apply(apply_as='DATA', modifier='x_window_array2')
        bpy.ops.object.modifier_apply(apply_as='DATA', modifier='y_window_array2')
        bpy.ops.object.transform_apply(location = True, scale = True, rotation = True)

        return {'FINISHED'}


def menu_func(self, context):
    self.layout.operator(AddWindows.bl_idname, icon='MOD_LATTICE')


def register():
    bpy.utils.register_class(AddWindows)
    bpy.types.INFO_MT_mesh_add.append(menu_func)


def unregister():
    bpy.utils.unregister_class(AddWindows)
    bpy.types.INFO_MT_mesh_add.remove(menu_func)

if __name__ == "__main__":
    register()
