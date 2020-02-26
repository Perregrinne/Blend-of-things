bl_info = {
    "name": "Add Stairs",
    "description": "Generates stairs.",
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
import math
import mathutils

from bpy.props import (
        BoolProperty,
        BoolVectorProperty,
        FloatProperty,
        FloatVectorProperty,
        IntProperty,
        EnumProperty,
        )

#def add_steps(l, w, h, rot, x, y, b, steps, style, t, sn, sl, sw, o, self, context):
    
    
            
#def add_rotated_steps(l, w, h, rot, x, y, z, steps, style, st, sn, sl, sw, o, self, context):
#    add_steps(l, w, h, rot, x, y, z, steps, style, st, sn, sl, sw, o, self, context)

class AddStairs(bpy.types.Operator):
    #Add stairs
    bl_idname = "mesh.stairs_add"
    bl_label = "Add Stairs"
    bl_options = {'REGISTER', 'UNDO'}
    
    length = FloatProperty(
            name="Length",
            description="Length of the staircase",
            min=0.01,
            default=6.0,
            )
    width = FloatProperty(
            name="Width",
            description="Width of the staircase",
            min=0.01,
            default=2.0,
            )
    height = FloatProperty(
            name="Height",
            description="Height of the staircase",
            min=0.01,
            default=3.0,
            )
    steps = IntProperty(
            name="Steps",
            description="How many steps",
            min=1,
            default=10,
            )
    step_type = EnumProperty(
            name="Step Type",
            description="Style or design of the stairs",
            items=(('BOX', 'Box', 'One straight box with steps cut into it'),
                    ('THIN', 'Thin', 'A straight line of thin connected steps'),
                    ('BROT', 'Box Rotated', 'Box stairs rotate back by 180 degrees to meet next floor'),
                    ('TROT', 'Thin Rotated', 'Thin stairs rotate back by 180 degrees to meet next floor'),),
            )
    step_thick = FloatProperty(
            name="Step Thickness",
            description="How thick/tall each step is (only for 'Thin' styles)",
            min=0.01, max=100.0,
            default=0.025,
            )
    rotate = FloatProperty(
            name="Rotation",
            description="Rotates the stairs around the z-axis (degrees)",
            default=0.0,
            min=0.0,
            max=360.0,
            )
    offset = FloatProperty(
            name="Support Offset Shift",
            description="How strongly the support beams intersect the steps (only for 'Thin' styles)",
            default=0.0,
            )
    supportn = IntProperty(
            name="Supports",
            description="How many support beams hold up the steps ('Thin' style only)",
            min=0,
            default=1,
            )
    supportl = FloatProperty(
            name="Support Length",
            description="Length of the stairs supports (only for 'Thin' styles)",
            min=0.01,
            default=0.25,
            )
    supportw = FloatProperty(
            name="Support Width",
            description="Width of the stairs supports (only for 'Thin' styles)",
            min=0.01,
            default=0.05,
            )
    platformw = FloatProperty(
            name="Platform Width",
            description="Width of the platform between stairs (only for 'Rotated' styles)",
            min=0.0,
            default=5.0,
            )
    platforml = FloatProperty(
            name="Platform Length",
            description="Length of the platform between stairs (only for 'Rotated' styles)",
            min=0.0,
            default=2.0,
            )
    platformt = FloatProperty(
            name="Platform Thickness",
            description="Thickness of the platform between stairs (only for 'Rotated' styles)",
            min=0.0,
            default=0.025,
            )
    connector_thick = FloatProperty(
            name="Connector Thickness",
            description="Thickness of the connectors that join the stairs and platform (only for 'Thin Rotated' styles)",
            min=0.0,
            default=0.025,
            )
    location = FloatVectorProperty(
            name="Location",
            subtype='TRANSLATION',
            )
    
    def draw(self, context):
        layout = self.layout
        
        box = layout.box()
        col = box.column()
        col.label(text="Size", icon="ARROW_LEFTRIGHT")
        col.prop(self, "length")
        col.prop(self, "width")
        col.prop(self, "height")
        
        box = layout.box()
        col = box.column()
        col.label(text="Placement", icon="OUTLINER_DATA_EMPTY")
        col.prop(self, "location")
        col.prop(self, "rotate")
        
        box = layout.box()
        col = box.column()
        col.label(text="Steps", icon="POSE_DATA")
        col.prop(self, "steps")
        col.label(text=("length of each step: " + str(self.length / self.steps)))
        col.label(text=("Height of each step: " + str(self.height / self.steps)))
        col.prop(self, "step_type")
        if self.step_type == 'THIN':
            col.prop(self, "offset")
            col.prop(self, "step_thick")
            col.prop(self, "supportn")
            col.prop(self, "supportl")
            col.prop(self, "supportw")
        elif self.step_type == 'BROT':
            col.prop(self, "platformw")
            col.prop(self, "platforml")
        elif self.step_type == 'TROT':
            col.prop(self, "offset")
            col.prop(self, "step_thick")
            col.prop(self, "supportn")
            col.prop(self, "supportl")
            col.prop(self, "supportw")
            col.prop(self, "platformw")
            col.prop(self, "platforml")
            col.prop(self, "platformt")
            col.prop(self, "connector_thick")
    
    def execute(self, context):
        #rename the variables to something easier:
        l = self.length
        w = self.width
        h = self.height
        loc = self.location
        rot = self.rotate
        steps = self.steps
        style = self.step_type
        o = self.offset
        t = self.step_thick
        sn = self.supportn
        sl = self.supportl
        sw = self.supportw
        pw = self.platformw
        pl = self.platforml
        pt = self.platformt
        ct = self.connector_thick
        #Set these:
        x = loc.x
        y = loc.y
        b = loc.z
        
        #Since there're 2 sets of stairs
        #stacked up, h needs to be half:
        if style == 'BROT' or style == 'TROT':
            h /= 2.0
        
        #Box stairs
        if style == 'BOX':
        
            verts = [((l / 2.0), (-w / 2.0), (b)),
                     ((l / 2.0), (w / 2.0), (b)),
                     ((-l / 2.0), (w / 2.0), (b)),
                     ((-l / 2.0), (-w / 2.0), (b)),
                     ((l / 2.0), (-w / 2.0), (b + (h / steps))),
                     ((l / 2.0), (w / 2.0), (b + (h / steps))),
                     ((-l / 2.0), (w / 2.0), (b + (h / steps))),
                     ((-l / 2.0), (-w / 2.0), (b + (h / steps))),
                     (((l / 2.0) - (l / steps)), (w / 2.0), (b + (h / steps))),
                     (((l / 2.0) - (l / steps)), (-w / 2.0), (b + (h / steps))),
                    ]
                    
            faces = [(0, 1, 5, 4),
                     (8, 9, 4, 5),
                     (0, 4, 7, 3),
                     (7, 6, 2, 3),
                     (2, 6, 5, 1),
                    ]
            
            #Create the staircase
            mesh_stairs = bpy.data.meshes.new("Stairs")
            stairs_obj = bpy.data.objects.new("Stairs_Obj", mesh_stairs)

            scene = bpy.context.scene
            scene.objects.link(stairs_obj)

            bm_stairs = bmesh.new()
            
            for v_co in verts:
                bm_stairs.verts.new(v_co)

            bm_stairs.verts.ensure_lookup_table()
            for f_idx in faces:
                bm_stairs.faces.new([bm_stairs.verts[i] for i in f_idx])
            
            #Duplicate the first step till all steps are made
            #Copy the lowest step and duplicate it for each step
            bm_stairs.faces.ensure_lookup_table()
            bm_stairs.verts.ensure_lookup_table()
            
            g = bm_stairs.faces
            step_count = 1
            while step_count < steps:
                dupl = bmesh.ops.duplicate(bm_stairs, geom=g)
                g_dupl = dupl["geom"]
                new_verts = [e for e in g_dupl if isinstance(e, bmesh.types.BMVert)]
                del g_dupl
                bmesh.ops.translate(bm_stairs, verts=new_verts, vec=((-l / steps), 0.0, (h / steps)))
                step_count += 1
            
            #The back-most verts stick out too far,
            #clamp them on the x-axis to (-l / 2.0)
            #also, shift all verts on x and y axis.
            for v in bm_stairs.verts:
                if v.co.x < (-l / 2.0):
                    v.co.x = (-l / 2.0)
                #Now shift along the x and y axis:
                v.co.x += x
                v.co.y += y
            
            #rotate the bmesh by rot on z axis:
            bmesh.ops.rotate(bm_stairs, verts=bm_stairs.verts, cent=(x, y, b), matrix=mathutils.Matrix.Rotation(math.radians(rot), 3, 'Z'))
            
            #Finish up, and it's done!
            bm_stairs.to_mesh(mesh_stairs)
            mesh_stairs.update()
            bm_stairs.free()
        
        #Thin stairs:
        elif style == 'THIN':
            
            verts = [(+(l / 2.0), +(w / 2.0), ((h / steps) + b)),
                     (+(l / 2.0), -(w / 2.0), ((h / steps) + b)),
                     (((l / 2.0) - (l / steps)), -(w / 2.0), ((h / steps) + b)),
                     (((l / 2.0) - (l / steps)), +(w / 2.0), ((h / steps) + b)),
                     (+(l / 2.0), +(w / 2.0), ((h / steps) - t + b)),
                     (+(l / 2.0), -(w / 2.0), ((h / steps) - t + b)),
                     (((l / 2.0) - (l / steps)), -(w / 2.0), ((h / steps) - t + b)),
                     (((l / 2.0) - (l / steps)), +(w / 2.0), ((h / steps) - t + b)),
                    ]
                    
            faces = [(3, 2, 1, 0),
                     (5, 6, 7, 4),
                     (1, 5, 4, 0),
                     (2, 6, 5, 1),
                     (3, 7, 6, 2),
                     (7, 3, 0, 4),
                    ]
            
            #Create the staircase
            mesh_stairs = bpy.data.meshes.new("Stairs")
            stairs_obj = bpy.data.objects.new("Stairs_Obj", mesh_stairs)

            scene = bpy.context.scene
            scene.objects.link(stairs_obj)

            bm_stairs = bmesh.new()
            
            for v_co in verts:
                bm_stairs.verts.new(v_co)

            bm_stairs.verts.ensure_lookup_table()
            for f_idx in faces:
                bm_stairs.faces.new([bm_stairs.verts[i] for i in f_idx])
            
            #Duplicate the first step till all steps are made
            #Copy the lowest step and duplicate it for each step
            bm_stairs.faces.ensure_lookup_table()
            bm_stairs.verts.ensure_lookup_table()
            
            g = bm_stairs.faces
            step_count = 1
            while step_count < steps:
                dupl = bmesh.ops.duplicate(bm_stairs, geom=g)
                g_dupl = dupl["geom"]
                new_verts = [e for e in g_dupl if isinstance(e, bmesh.types.BMVert)]
                del g_dupl
                bmesh.ops.translate(bm_stairs, verts=new_verts, vec=((-l / steps), 0.0, (h / steps)))
                step_count += 1
            
            #Add the support beam(s), if any
            if sn > 0:
                
                mesh_supports = bpy.data.meshes.new("Supports")
                supports_obj = bpy.data.objects.new("Supports_Obj", mesh_supports)

                scene = bpy.context.scene
                scene.objects.link(supports_obj)
                bm_supports = bmesh.new()
                
                verts = [(((+l / 2.0) + o), ((w / 2.0) - (w / (sn * 2.0)) - (sw / 2.0)), b),
                         (((+l / 2.0) + o), ((w / 2.0) - (w / (sn * 2.0)) + (sw / 2.0)), b),
                         (((+l / 2.0) - sl + o), ((w / 2.0) - (w / (sn * 2.0)) - (sw / 2.0)), b),
                         (((+l / 2.0) - sl + o), ((w / 2.0) - (w / (sn * 2.0)) + (sw / 2.0)), b),
                         (((-l / 2.0) + o), ((w / 2.0) - (w / (sn * 2.0)) - (sw / 2.0)), (b + h)),
                         (((-l / 2.0) + o), ((w / 2.0) - (w / (sn * 2.0)) + (sw / 2.0)), (b + h)),
                         (((-l / 2.0) - sl + o), ((w / 2.0) - (w / (sn * 2.0)) - (sw / 2.0)), (b + h)),
                         (((-l / 2.0) - sl + o), ((w / 2.0) - (w / (sn * 2.0)) + (sw / 2.0)), (b + h)),
                        ]
                
                faces = [(4, 6, 2, 0),
                         (5, 4, 0, 1),
                         (7, 5, 1, 3),
                         (6, 7, 3, 2),
                        ]
                
                for v_co in verts:
                    bm_supports.verts.new(v_co)

                bm_supports.verts.ensure_lookup_table()
                for f_idx in faces:
                    bm_supports.faces.new([bm_supports.verts[i] for i in f_idx])
                    
                #Duplicate the mesh for each support
                beams = 1
                g = bm_supports.faces
                while beams < (sn):
                    dupl = bmesh.ops.duplicate(bm_supports, geom=g)
                    g_dupl = dupl["geom"]
                    new_verts = [e for e in g_dupl if isinstance(e, bmesh.types.BMVert)]
                    del g_dupl
                    bmesh.ops.translate(bm_supports, verts=new_verts, vec=(0.0, (-w / sn), 0.0))
                    beams += 1
                
                #Join bm_supports into bm_stairs
                bm_supports.to_mesh(mesh_supports)
                mesh_supports.update()
                bm_stairs.to_mesh(mesh_stairs)
                mesh_stairs.update()
                bm_supports.free()
                bm_stairs.free()
                
                bpy.ops.object.select_all(action='DESELECT')
                supports_obj.select = True
                stairs_obj.select = True
                bpy.context.scene.objects.active = stairs_obj
                bpy.ops.object.join()
                
                #Bring it back to edit mode to finish moving/rotation
                bpy.ops.object.mode_set(mode='EDIT')
                bm_stairs = bmesh.from_edit_mesh(mesh_stairs)
                
            
            #Shift all verts on x and y axis.
            for v in bm_stairs.verts:
                v.co.x += x
                v.co.y += y
            
            #rotate the bmesh by rot on z axis:
            bmesh.ops.rotate(bm_stairs, verts=bm_stairs.verts, cent=(x, y, b), matrix=mathutils.Matrix.Rotation(math.radians(rot), 3, 'Z'))
            
            #Finish up, and it's done!
            if sn > 0:
                bmesh.update_edit_mesh(mesh_stairs)
                bpy.ops.object.mode_set(mode='OBJECT')
            else:
                bm_stairs.to_mesh(mesh_stairs)
                mesh_stairs.update()
                bm_stairs.free()
        
        #Box-Rotated stairs:
        if style == 'BROT':
        
            verts = [(l, ((pw / 2.0) - w), (b)),
                     (l, (pw / 2.0), (b)),
                     (0.0, (pw / 2.0), (b)),
                     (0.0, ((pw / 2.0) - w), (b)),
                     (l, ((pw / 2.0) - w), (b + (h / steps))),
                     (l, (pw / 2.0), (b + (h / steps))),
                     (0.0, (pw / 2.0), (b + (h / steps))),
                     (0.0, ((pw / 2.0) - w), (b + (h / steps))),
                     ((l - (l / steps)), (pw / 2.0), (b + (h / steps))),
                     ((l - (l / steps)), ((pw / 2.0) - w), (b + (h / steps))),
                    ]
                    
            faces = [(0, 1, 5, 4),
                     (8, 9, 4, 5),
                     (0, 4, 7, 3),
                     (7, 6, 2, 3),
                     (2, 6, 5, 1),
                    ]
            
            #Create the lower-stairs
            mesh_stairs1 = bpy.data.meshes.new("Stairs1")
            stairs1_obj = bpy.data.objects.new("Stairs1_Obj", mesh_stairs1)

            scene = bpy.context.scene
            scene.objects.link(stairs1_obj)

            bm_stairs1 = bmesh.new()
            
            for v_co in verts:
                bm_stairs1.verts.new(v_co)

            bm_stairs1.verts.ensure_lookup_table()
            for f_idx in faces:
                bm_stairs1.faces.new([bm_stairs1.verts[i] for i in f_idx])
            
            #Duplicate the first step till all steps are made
            #Copy the lowest step and duplicate it for each step
            bm_stairs1.faces.ensure_lookup_table()
            bm_stairs1.verts.ensure_lookup_table()
            
            g = bm_stairs1.faces
            step_count = 1
            while step_count < steps:
                dupl = bmesh.ops.duplicate(bm_stairs1, geom=g)
                g_dupl = dupl["geom"]
                new_verts = [e for e in g_dupl if isinstance(e, bmesh.types.BMVert)]
                del g_dupl
                bmesh.ops.translate(bm_stairs1, verts=new_verts, vec=((-l / steps), 0.0, (h / steps)))
                step_count += 1
            
            #The back-most verts stick out too far,
            #clamp them on the x-axis to (-l / 2.0)
            #also, shift all verts on x and y axis.
            for v in bm_stairs1.verts:
                if v.co.x < 0.0:
                    v.co.x = 0.0
            
            #Finish up, and it's done!
            bm_stairs1.to_mesh(mesh_stairs1)
            mesh_stairs1.update()
            bm_stairs1.free()
            
            #Make the upper-stairs now
            #These additional stairs need to begin
            #higher than the platform and stairs1:
            b += h
            
            verts = [(l, ((-pw / 2.0) + w), (b)),
                     (l, (-pw / 2.0), (b)),
                     (0.0, (-pw / 2.0), (b)),
                     (0.0, ((-pw / 2.0) + w), (b)),
                     (l, ((-pw / 2.0) + w), (b + (h / steps))),
                     (l, (-pw / 2.0), (b + (h / steps))),
                     (0.0, (-pw / 2.0), (b + (h / steps))),
                     (0.0, ((-pw / 2.0) + w), (b + (h / steps))),
                     ((l - (l / steps)), (-pw / 2.0), (b + (h / steps))),
                     ((l - (l / steps)), ((-pw / 2.0) + w), (b + (h / steps))),
                    ]
                    
            faces = [(4, 5, 1, 0),
                     (5, 4, 9, 8),
                     (3, 7, 4, 0),
                     (3, 2, 6, 7),
                     (1, 5, 6, 2),
                    ]
            
            #Create the staircase
            mesh_stairs2 = bpy.data.meshes.new("Stairs2")
            stairs2_obj = bpy.data.objects.new("Stairs2_Obj", mesh_stairs2)

            scene = bpy.context.scene
            scene.objects.link(stairs2_obj)

            bm_stairs2 = bmesh.new()
            
            for v_co in verts:
                bm_stairs2.verts.new(v_co)

            bm_stairs2.verts.ensure_lookup_table()
            for f_idx in faces:
                bm_stairs2.faces.new([bm_stairs2.verts[i] for i in f_idx])
            
            #Duplicate the first step till all steps are made
            #Copy the lowest step and duplicate it for each step
            bm_stairs2.faces.ensure_lookup_table()
            bm_stairs2.verts.ensure_lookup_table()
            
            g = bm_stairs2.faces
            step_count = 1
            while step_count < steps:
                dupl = bmesh.ops.duplicate(bm_stairs2, geom=g)
                g_dupl = dupl["geom"]
                new_verts = [e for e in g_dupl if isinstance(e, bmesh.types.BMVert)]
                del g_dupl
                bmesh.ops.translate(bm_stairs2, verts=new_verts, vec=((-l / steps), 0.0, (h / steps)))
                step_count += 1
            
            #The back-most verts stick out too far,
            #clamp them on the x-axis to (-l / 2.0)
            #also, shift all verts on x and y axis.
            for v in bm_stairs2.verts:
                if v.co.x < 0.0:
                    v.co.x = 0.0
            
            #Center of the rotation:
            rcent = ((l / 2.0), ((-pw / 2.0) + (w / 2.0)), b)
            #rotate the bmesh by 180 deg. on z axis:
            bmesh.ops.rotate(bm_stairs2, verts=bm_stairs2.verts, cent=rcent, matrix=mathutils.Matrix.Rotation(math.radians(180), 3, 'Z'))
            
            #Finish up, and it's done!
            bm_stairs2.to_mesh(mesh_stairs2)
            mesh_stairs2.update()
            bm_stairs2.free()
            
            
            #Now add the platform:
            
            #Make sure that the platform
            #doesn't raise with stairs2:
            b -= h
            
            verts = [(l, (-pw / 2.0), b),
                     (-pl, (-pw / 2.0), b),
                     (l, ((-pw / 2.0) + w), b),
                     ((0.0), ((-pw / 2.0) + w), b),
                     ((0.0), (pw / 2.0), b),
                     (-pl, (pw / 2.0), b),
                     (l, (-pw / 2.0), (b + h)),
                     (-pl, (-pw / 2.0), (b + h)),
                     (l, ((-pw / 2.0) + w), (b + h)),
                     ((0.0), ((-pw / 2.0) + w), (b + h)),
                     ((0.0), (pw / 2.0), (b + h)),
                     (-pl, (pw / 2.0), (b + h)),
                    ]
            
            faces = [(1, 0, 6, 7),
                     (0, 2, 8, 6),
                     (2, 3, 9, 8),
                     (3, 4, 10, 9),
                     (4, 5, 11, 10),
                     (1, 7, 11, 5),
                     (7, 9, 10, 11),
                     (7, 6, 8, 9),
                    ]
            
            #Create the staircase
            mesh_platform = bpy.data.meshes.new("Platform")
            platform_obj = bpy.data.objects.new("Platform_Obj", mesh_platform)

            scene = bpy.context.scene
            scene.objects.link(platform_obj)

            bm_platform = bmesh.new()
            
            for v_co in verts:
                bm_platform.verts.new(v_co)

            bm_platform.verts.ensure_lookup_table()
            for f_idx in faces:
                bm_platform.faces.new([bm_platform.verts[i] for i in f_idx])
            
            #Finish up, and this one is done!
            bm_platform.to_mesh(mesh_platform)
            mesh_platform.update()
            bm_platform.free()
            
            #Join them all, then move them and rotate them by x, y, and rot
            bpy.ops.object.select_all(action='DESELECT')
            platform_obj.select = True
            stairs1_obj.select = True
            stairs2_obj.select = True
            bpy.context.scene.objects.active = stairs1_obj
            bpy.ops.object.join()
            stairs1_obj.name = "stairs"
            
            #Rotate, move and apply transformations:
            stairs1_obj.rotation_euler = (0, 0, math.radians(rot))
            stairs1_obj.location = (x, y, b)
            bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
            
            
            
            
            
            
        #Thin-rotated stairs:
        elif style == 'TROT':
            
            verts = [(l, (pw / 2.0), ((h / steps) + b)),
                     (l, ((pw / 2.0) - w), ((h / steps) + b)),
                     ((l - (l / steps)), ((pw / 2.0) - w), ((h / steps) + b)),
                     ((l - (l / steps)), (pw / 2.0), ((h / steps) + b)),
                     (l, (pw / 2.0), ((h / steps) - t + b)),
                     (l, ((pw / 2.0) - w), ((h / steps) - t + b)),
                     ((l - (l / steps)), ((pw / 2.0) - w), ((h / steps) - t + b)),
                     ((l - (l / steps)), (pw / 2.0), ((h / steps) - t + b)),
                    ]
                    
            faces = [(3, 2, 1, 0),
                     (5, 6, 7, 4),
                     (1, 5, 4, 0),
                     (2, 6, 5, 1),
                     (3, 7, 6, 2),
                     (7, 3, 0, 4),
                    ]
            
            #Create the staircase
            mesh_stairs = bpy.data.meshes.new("Stairs")
            stairs_obj = bpy.data.objects.new("Stairs_Obj", mesh_stairs)

            scene = bpy.context.scene
            scene.objects.link(stairs_obj)

            bm_stairs = bmesh.new()
            
            for v_co in verts:
                bm_stairs.verts.new(v_co)

            bm_stairs.verts.ensure_lookup_table()
            for f_idx in faces:
                bm_stairs.faces.new([bm_stairs.verts[i] for i in f_idx])
            
            #Duplicate the first step till all steps are made
            #Copy the lowest step and duplicate it for each step
            bm_stairs.faces.ensure_lookup_table()
            bm_stairs.verts.ensure_lookup_table()
            
            g = bm_stairs.faces
            step_count = 1
            while step_count < steps:
                dupl = bmesh.ops.duplicate(bm_stairs, geom=g)
                g_dupl = dupl["geom"]
                new_verts = [e for e in g_dupl if isinstance(e, bmesh.types.BMVert)]
                del g_dupl
                bmesh.ops.translate(bm_stairs, verts=new_verts, vec=((-l / steps), 0.0, (h / steps)))
                step_count += 1
            
            #Add the support beam(s), if any
            if sn > 0:
                
                mesh_supports = bpy.data.meshes.new("Supports")
                supports_obj = bpy.data.objects.new("Supports_Obj", mesh_supports)

                scene = bpy.context.scene
                scene.objects.link(supports_obj)
                bm_supports = bmesh.new()
                
                verts = [((l + o), ((pw / 2.0) - (w / (sn * 2.0)) - (sw / 2.0)), b),
                         ((l + o), ((pw / 2.0) - (w / (sn * 2.0)) + (sw / 2.0)), b),
                         ((l - sl + o), ((pw / 2.0) - (w / (sn * 2.0)) - (sw / 2.0)), b),
                         ((l - sl + o), ((pw / 2.0) - (w / (sn * 2.0)) + (sw / 2.0)), b),
                         (o, ((pw / 2.0) - (w / (sn * 2.0)) - (sw / 2.0)), (b + h)),
                         (o, ((pw / 2.0) - (w / (sn * 2.0)) + (sw / 2.0)), (b + h)),
                         ((-sl + o), ((pw / 2.0) - (w / (sn * 2.0)) - (sw / 2.0)), (b + h)),
                         ((-sl + o), ((pw / 2.0) - (w / (sn * 2.0)) + (sw / 2.0)), (b + h)),
                        ]
                
                faces = [(4, 6, 2, 0),
                         (5, 4, 0, 1),
                         (7, 5, 1, 3),
                         (6, 7, 3, 2),
                        ]
                
                for v_co in verts:
                    bm_supports.verts.new(v_co)

                bm_supports.verts.ensure_lookup_table()
                for f_idx in faces:
                    bm_supports.faces.new([bm_supports.verts[i] for i in f_idx])
                    
                #Duplicate the mesh for each support
                beams = 1
                g = bm_supports.faces
                while beams < (sn):
                    dupl = bmesh.ops.duplicate(bm_supports, geom=g)
                    g_dupl = dupl["geom"]
                    new_verts = [e for e in g_dupl if isinstance(e, bmesh.types.BMVert)]
                    del g_dupl
                    bmesh.ops.translate(bm_supports, verts=new_verts, vec=(0.0, (-w / sn), 0.0))
                    beams += 1
                
                #Join bm_supports into bm_stairs
                bm_supports.to_mesh(mesh_supports)
                mesh_supports.update()
                bm_stairs.to_mesh(mesh_stairs)
                mesh_stairs.update()
                bm_supports.free()
                bm_stairs.free()
                
                bpy.ops.object.select_all(action='DESELECT')
                supports_obj.select = True
                stairs_obj.select = True
                bpy.context.scene.objects.active = stairs_obj
                bpy.ops.object.join()
                
                #Bring it back to edit mode to finish moving/rotation
                bpy.ops.object.mode_set(mode='EDIT')
                bm_stairs = bmesh.from_edit_mesh(mesh_stairs)
                
            
            #rotate the bmesh by rot on z axis:
            #bmesh.ops.rotate(bm_stairs, verts=bm_stairs.verts, cent=(x, y, b), matrix=mathutils.Matrix.Rotation(math.radians(rot), 3, 'Z'))
            
            #Finish up, and it's done!
            if sn > 0:
                bmesh.update_edit_mesh(mesh_stairs)
                bpy.ops.object.mode_set(mode='OBJECT')
            else:
                bm_stairs.to_mesh(mesh_stairs)
                mesh_stairs.update()
                bm_stairs.free()
            
            #Make the upper-stairs:
            mesh_stairs2 = mesh_stairs.copy()
            stairs2_obj = bpy.data.objects.new("Stairs2_Obj", mesh_stairs2)

            scene = bpy.context.scene
            scene.objects.link(stairs2_obj)
            
            bpy.ops.object.select_all(action='DESELECT')
            stairs2_obj.select = True
            bpy.context.scene.objects.active = stairs2_obj
            
            bpy.ops.object.mode_set(mode='EDIT')
            bm_stairs2 = bmesh.from_edit_mesh(mesh_stairs2)
            
            #Rotate it 180 deg:
            bmesh.ops.rotate(bm_stairs2, verts=bm_stairs2.verts, cent=(x, y, b), matrix=mathutils.Matrix.Rotation(math.radians(180), 3, 'Z'))
            
            #Move it back by (l, 0.0, h) amount:
            bmesh.ops.translate(bm_stairs2, verts=bm_stairs2.verts, vec=(l, 0.0, h))
            
            bmesh.update_edit_mesh(mesh_stairs2)
            bpy.ops.object.mode_set(mode='OBJECT')
            
            
            #Add the platform:
            verts = [(0.0, (pw / 2.0), h),
                     (0.0, (-pw / 2.0), h),
                     (-pl, (-pw / 2.0), h),
                     (-pl, (pw / 2.0), h),
                     (0.0, (pw / 2.0), (h - pt)),
                     (0.0, (-pw / 2.0), (h - pt)),
                     (-pl, (-pw / 2.0), (h - pt)),
                     (-pl, (pw / 2.0), (h - pt)),
                    ]

            faces = [(3, 2, 1, 0),
                     (5, 6, 7, 4),
                     (1, 5, 4, 0),
                     (2, 6, 5, 1),
                     (3, 7, 6, 2),
                     (7, 3, 0, 4),
                    ]
                    
            #Create the staircase
            mesh_platform = bpy.data.meshes.new("Platform")
            platform_obj = bpy.data.objects.new("Platform_Obj", mesh_platform)

            scene = bpy.context.scene
            scene.objects.link(platform_obj)

            bm_platform = bmesh.new()
            
            for v_co in verts:
                bm_platform.verts.new(v_co)

            bm_platform.verts.ensure_lookup_table()
            for f_idx in faces:
                bm_platform.faces.new([bm_platform.verts[i] for i in f_idx])
            
            bm_platform.to_mesh(mesh_platform)
            mesh_platform.update()
            bm_platform.free()
            
            #Make the connectors that join
            #the upper stairs and platform
            if sn > 0:
                
                mesh_connector = bpy.data.meshes.new("Connector")
                connector_obj = bpy.data.objects.new("Connector_Obj", mesh_connector)

                scene = bpy.context.scene
                scene.objects.link(connector_obj)
                bm_connector = bmesh.new()
                
                verts = [(0.0, -((pw / 2.0) - (w / (sn * 2.0)) - (sw / 2.0)), (b + h)),
                         (0.0, -((pw / 2.0) - (w / (sn * 2.0)) + (sw / 2.0)), (b + h)),
                         (sl, -((pw / 2.0) - (w / (sn * 2.0)) - (sw / 2.0)), (b + h)),
                         (sl, -((pw / 2.0) - (w / (sn * 2.0)) + (sw / 2.0)), (b + h)),
                         (0.0, -((pw / 2.0) - (w / (sn * 2.0)) - (sw / 2.0)), (b + h - pt)),
                         (0.0, -((pw / 2.0) - (w / (sn * 2.0)) + (sw / 2.0)), (b + h - pt)),
                         (sl, -((pw / 2.0) - (w / (sn * 2.0)) - (sw / 2.0)), (b + h - ct - pt)),
                         (sl, -((pw / 2.0) - (w / (sn * 2.0)) + (sw / 2.0)), (b + h - ct - pt)),
                         ((-pl / 2.0), -((pw / 2.0) - (w / (sn * 2.0)) - (sw / 2.0)), (b + h - pt)),
                         ((-pl / 2.0), -((pw / 2.0) - (w / (sn * 2.0)) + (sw / 2.0)), (b + h - pt)),
                         ((-pl / 2.0), -((pw / 2.0) - (w / (sn * 2.0)) - (sw / 2.0)), (b + h - ct - pt)),
                         ((-pl / 2.0), -((pw / 2.0) - (w / (sn * 2.0)) + (sw / 2.0)), (b + h - ct - pt)),
                        ]
                
                faces = [(11, 10, 6, 7),
                         (6, 10, 8, 4),
                         (0, 2, 6, 4),
                         (2, 3, 7, 6),
                         (10, 11, 9, 8),
                         (11, 7, 5, 9),
                         (5, 7, 3, 1),
                        ]
                
                for v_co in verts:
                    bm_connector.verts.new(v_co)

                bm_connector.verts.ensure_lookup_table()
                for f_idx in faces:
                    bm_connector.faces.new([bm_connector.verts[i] for i in f_idx])
                    
                #Duplicate the mesh for each support
                beams = 1
                g = bm_connector.faces
                while beams < (sn):
                    dupl = bmesh.ops.duplicate(bm_connector, geom=g)
                    g_dupl = dupl["geom"]
                    new_verts = [e for e in g_dupl if isinstance(e, bmesh.types.BMVert)]
                    del g_dupl
                    bmesh.ops.translate(bm_connector, verts=new_verts, vec=(0.0, (w / sn), 0.0))
                    beams += 1
                
                #Cleaning up and finalizing:
                bm_connector.to_mesh(mesh_connector)
                mesh_connector.update()
                bm_connector.free()
            
            #Join them all:
            bpy.ops.object.select_all(action='DESELECT')
            stairs_obj.select = True
            stairs2_obj.select = True
            if sn > 0:
                connector_obj.select = True
            platform_obj.select = True
            bpy.context.scene.objects.active = stairs_obj
            bpy.ops.object.join()
            stairs_obj.name = "stairs"
            
            #Move, rotate, and apply transformations:
            stairs_obj.rotation_euler = (0, 0, math.radians(rot))
            stairs_obj.location = (x, y, b)
            bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
            
        return {'FINISHED'}


def menu_func(self, context):
    self.layout.operator(AddStairs.bl_idname, icon='POSE_DATA')


def register():
    bpy.utils.register_class(AddStairs)
    bpy.types.INFO_MT_mesh_add.append(menu_func)


def unregister():
    bpy.utils.unregister_class(AddStairs)
    bpy.types.INFO_MT_mesh_add.remove(menu_func)

if __name__ == "__main__":
    register()