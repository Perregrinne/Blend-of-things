bl_info = {
    "name": "Door Generator",
    "description": "Generate doors and a boolean cutout",
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
import mathutils

from bpy_extras import object_utils
from bpy.props import (
        BoolProperty,
        BoolVectorProperty,
        FloatProperty,
        FloatVectorProperty,
        IntProperty,
        EnumProperty,
        )

class AddDoor(bpy.types.Operator):
    """Add a simple door mesh, door frame, and boolean box"""
    bl_idname = "mesh.door_add"
    bl_label = "Add Door"
    bl_options = {'REGISTER', 'UNDO'}

    length = FloatProperty(
            name="Length",
            description="Length",
            min=0.01,
            default=1.25,
            )
    door_width = FloatProperty(
            name="Door Width",
            description="Width of the door",
            min=0.01,
            default=0.05,
            )
    frame_width = FloatProperty(
            name="Frame Width",
            description="Width of the door frame",
            min=0.125,
            default=0.15,
            )
    frame_thick = FloatProperty(
            name="Frame Thickness",
            description="Thickness of the door frame",
            min=0.01,
            default=0.0325,
            )
    frame_inner_thick = FloatProperty(
            name="Frame Inner Thickness",
            description="Thickness of the inner door frame (that the door sits against)",
            min=0.001,
            default=0.01,
            )
    frame_inner_width = FloatProperty(
            name="Frame Inner Width",
            description="Width of the inner door frame",
            min=0.001,
            default=0.025,
            )
    door_shift = FloatProperty(
            name="Door Shift",
            description="Moves the door and inner door frame forward or backward",
            default=0.0,
            )
    has_glass = BoolProperty(
            name="Glass Door",
            description="Whether or not to have glass in the door",
            default=False,
            )
    door_glass_thick = FloatProperty(
            name="Glass Thickness",
            description="Thickness of the glass window in the door",
            min=0.001,
            default=0.0125,
            )
    door_glass_w = FloatProperty(
            name="Glass Width",
            description="Width of the door glass",
            min=0.001,
            default=0.5,
            )
    door_glass_h = FloatProperty(
            name="Glass Height",
            description="Height of the door glass",
            min=0.001,
            default=1.0,
            )
    door_glass_x = FloatProperty(
            name="Glass X Position",
            description="Left/Right shift of the door glass",
            default=0.0,
            )
    door_glass_y = FloatProperty(
            name="Glass Y Position",
            description="Up/Down shift of the door glass",
            default=0.0,
            )
    height = FloatProperty(
            name="Height",
            description="Box Depth",
            min=0.01,
            default=2.25,
            )
    gap = FloatProperty(
            name="Gap",
            description="Doors do not sit perfectly inside the frame",
            min=0.0,
            default=0.00325,
            )
    floor_gap = FloatProperty(
            name="Floor Gap",
            description="Hinged doors have a small gap between them and the door",
            min=0.0,
            default=0.0125,
            )
    hinge_diameter = FloatProperty(
            name="Hinge Diameter",
            description="Diameter of the door hinge",
            min=0.001,
            default=0.0075,
            )
    hinge_height = FloatProperty(
            name="Hinge Height",
            description="Height of the door hinge",
            min=0.001,
            default=0.0675,
            )
    hinge_cyl_height = FloatProperty(
            name="Hinge Pin Height",
            description="Height of the pin of the door hinge",
            min=0.001,
            default=0.0725,
            )
    hinge_width = FloatProperty(
            name="Hinge Width",
            description="Width of the door hinge (excluding hinge diameter)",
            min=0.001,
            default=0.04,
            )
    hinge_segments = IntProperty(
            name="Hinge Segments",
            description="How many segments make up the hinge cylinder",
            min=4,
            default=12,
            )
    #Perhaps make garage doors, someday
    door_style = EnumProperty(
            name="Door Style",
            description="Type of roof the building has",
            items=(('HINGE', 'Hinged', 'A door that swings on a hinge'),
                   ('SLIDE', 'Sliding', 'A sliding door'),
                   ('ROTATING', 'Revolving', 'A revolving door'),
                   ('NONE', 'None', 'Just makes the hidden boolean cutout box')),
            default='HINGE',
            )
    open_direction_hinge = EnumProperty(
            name="Open Direction",
            description="Where the hinge is, and which way the door opens from outside",
            items=(('LI', 'Left-Inward', 'The hinge is on the left and the door swings inward'),
                   ('LO', 'Left-Outward', 'The hinge is on the left and the door swings outward'),
                   ('RI', 'Right-Inward', 'The hinge is on the right and the door swings inward'),
                   ('RO', 'Right-Outward', 'The hinge is on the right and the door swings outward')),
            default='RI',
            )
    open_direction_slide = EnumProperty(
            name="Open Direction",
            description="Which way the sliding door opens",
            items=(('LEFT', 'Left', 'From the outside, the door slides left'),
                   ('RIGHT', 'Right', 'From the outside, the door slides right')),
            default='LEFT',
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
    
    #Display the menu sidebar
    def draw(self, context):
        layout = self.layout
        
        box = layout.box()
        col = box.column()
        col.label(text="Dimensions", icon="ARROW_LEFTRIGHT")
        col.prop(self, "length")
        col.prop(self, "door_width")
        col.prop(self, "frame_width")
        col.prop(self, "frame_thick")
        col.prop(self, "height")
        
        box = layout.box()
        col = box.column()
        col.label(text="Style and Orientation", icon="MOD_WIREFRAME")
        col.prop(self, "door_style")
        col.prop(self, "gap")
        if self.door_style == 'HINGE':
            col.prop(self, "open_direction_hinge")
            col.prop(self, "floor_gap")
            col.prop(self, "hinge_segments")
            col.prop(self, "hinge_diameter")
            col.prop(self, "hinge_height")
            col.prop(self, "hinge_cyl_height")
            col.prop(self, "hinge_width")
            col.prop(self, "frame_inner_thick")
            col.prop(self, "frame_inner_width")
            col.prop(self, "door_shift")
        elif self.door_style == 'SLIDE':
            col.prop(self, "open_direction_slide")
        
        box = layout.box()
        col = box.column()
        col.label(text="Glass", icon="MOD_MIRROR")
        col.prop(self, "has_glass")
        if self.has_glass == True:
            col.prop(self, "door_glass_thick")
            col.prop(self, "door_glass_w")
            col.prop(self, "door_glass_h")
            col.prop(self, "door_glass_x")
            col.prop(self, "door_glass_y")
        
        box = layout.box()
        col = box.column()
        col.label(text="Transformations", icon="NDOF_TURN")
        col.prop(self, "location")
        col.prop(self, "rotation")
    
    #Use the values from the menu
    #to generate everything below
    def execute(self, context):
        
        #Rename the variables:
        l = self.length
        dw = self.door_width
        fw = self.frame_width
        ft = self.frame_thick
        h = self.height
        loc = self.location
        rot = self.rotation
        style = self.door_style
        hinge = self.open_direction_hinge
        slide = self.open_direction_slide
        has_glass = self.has_glass
        gap = self.gap
        fgap = self.floor_gap
        hh = self.hinge_height
        hw = self.hinge_width
        hd = self.hinge_diameter
        hs = self.hinge_segments
        hc = self.hinge_cyl_height
        it = self.frame_inner_thick
        iw = self.frame_inner_width
        ds = self.door_shift
        glass_w = self.door_glass_w
        glass_h = self.door_glass_h
        glass_x = self.door_glass_x
        glass_y = self.door_glass_y
        glass_t = self.door_glass_thick
        
        #Create the boolean object to cut
        #a hole in the wall to fit a door
        mesh1 = bpy.data.meshes.new("Door_Boolean")
        door_obj = bpy.data.objects.new("Door_Bool_Obj", mesh1)

        scene = bpy.context.scene
        scene.objects.link(door_obj)

        bm1 = bmesh.new()
        
        verts = [(+((l / 2.0) + ft), +(fw / 2.0), 0.0001),
                 (+((l / 2.0) + ft), -(fw / 2.0), 0.0001),
                 (-((l / 2.0) + ft), -(fw / 2.0), 0.0001),
                 (-((l / 2.0) + ft), +(fw / 2.0), 0.0001),
                 (+((l / 2.0) + ft), +(fw / 2.0), h + ft),
                 (+((l / 2.0) + ft), -(fw / 2.0), h + ft),
                 (-((l / 2.0) + ft), -(fw / 2.0), h + ft),
                 (-((l / 2.0) + ft), +(fw / 2.0), h + ft),
                ]

        faces = [(0, 1, 2, 3),
                 (4, 7, 6, 5),
                 (0, 4, 5, 1),
                 (1, 5, 6, 2),
                 (2, 6, 7, 3),
                 (4, 0, 3, 7),
                ]

        for v_co in verts:
            bm1.verts.new(v_co)

        bm1.verts.ensure_lookup_table()
        for f_idx in faces:
            bm1.faces.new([bm1.verts[i] for i in f_idx])

        bm1.to_mesh(mesh1)
        mesh1.update()
        
        #We wan to hide it so
        #we can see the door.
        door_obj.hide = True
        
        #Now create the door frame
        mesh2 = bpy.data.meshes.new("Door_Frame")
        door_frame_obj = bpy.data.objects.new("Door_Frame_Obj", mesh2)

        scene = bpy.context.scene
        scene.objects.link(door_frame_obj)

        bm2 = bmesh.new()
        
        if style == 'HINGE':
            verts = [(-((l / 2.0) + ft), +(fw / 2.0), 0.0),
                     (+((l / 2.0) + ft), +(fw / 2.0), 0.0),
                     (-((l / 2.0) + ft), -(fw / 2.0), 0.0),
                     (+((l / 2.0) + ft), -(fw / 2.0), 0.0),
                     (-((l / 2.0) + ft), +(fw / 2.0), h + ft),
                     (+((l / 2.0) + ft), +(fw / 2.0), h + ft),
                     (-((l / 2.0) + ft), -(fw / 2.0), h + ft),
                     (+((l / 2.0) + ft), -(fw / 2.0), h + ft),
                     (-(l / 2.0), +(fw / 2.0), 0.0),
                     (+(l / 2.0), +(fw / 2.0), 0.0),
                     (-(l / 2.0), -(fw / 2.0), 0.0),
                     (+(l / 2.0), -(fw / 2.0), 0.0),
                     (-(l / 2.0), +(fw / 2.0), h),
                     (+(l / 2.0), +(fw / 2.0), h),
                     (-(l / 2.0), -(fw / 2.0), h),
                     (+(l / 2.0), -(fw / 2.0), h),
                     
                     (-(l / 2.0), ((fw / 2.0) + ds - dw), 0.0),
                     (+(l / 2.0), ((fw / 2.0) + ds - dw), 0.0),
                     (-(l / 2.0), ((fw / 2.0) - iw + ds - dw), 0.0),
                     (+(l / 2.0), ((fw / 2.0) - iw + ds - dw), 0.0),
                     (-(l / 2.0), ((fw / 2.0) + ds - dw), h),
                     (+(l / 2.0), ((fw / 2.0) + ds - dw), h),
                     (-(l / 2.0), ((fw / 2.0) - iw + ds - dw), h),
                     (+(l / 2.0), ((fw / 2.0) - iw + ds - dw), h),
                     (-((l / 2.0) - it), ((fw / 2.0) + ds - dw), 0.0),
                     (+((l / 2.0) - it), ((fw / 2.0) + ds - dw), 0.0),
                     (-((l / 2.0) - it), ((fw / 2.0) - iw + ds - dw), 0.0),
                     (+((l / 2.0) - it), ((fw / 2.0) - iw + ds - dw), 0.0),
                     (-((l / 2.0) - it), ((fw / 2.0) + ds - dw), h - it),
                     (+((l / 2.0) - it), ((fw / 2.0) + ds - dw), h - it),
                     (-((l / 2.0) - it), ((fw / 2.0) - iw + ds - dw), h - it),
                     (+((l / 2.0) - it), ((fw / 2.0) - iw + ds - dw), h - it),
                    ]
                    
            faces = [(6, 2, 10, 14),
                     (6, 14, 15, 7),
                     (15, 11, 3, 7),
                     (7, 3, 1, 5),
                     (6, 4, 0, 2),
                     (6, 7, 5, 4),
                     (15, 13, 9, 11),
                     (12, 13, 15, 14),
                     (12, 14, 10, 8),
                     (4, 12, 8, 0),
                     (5, 13, 12, 4),
                     (5, 1, 9, 13),
                     
                     (22, 18, 26, 30),
                     (22, 30, 31, 23),
                     (31, 27, 19, 23),
                     (23, 19, 17, 21),
                     (22, 20, 16, 18),
                     (22, 23, 21, 20),
                     (31, 29, 25, 27),
                     (28, 29, 31, 30),
                     (28, 30, 26, 24),
                     (20, 28, 24, 16),
                     (21, 29, 28, 20),
                     (21, 17, 25, 29),
                    ]
                    
        elif style == 'SLIDE':
            verts = [(-((l / 2.0) + ft), +(fw / 2.0), 0.0),
                     (+((l / 2.0) + ft), +(fw / 2.0), 0.0),
                     (-((l / 2.0) + ft), -(fw / 2.0), 0.0),
                     (+((l / 2.0) + ft), -(fw / 2.0), 0.0),
                     (-((l / 2.0) + ft), +(fw / 2.0), h + ft),
                     (+((l / 2.0) + ft), +(fw / 2.0), h + ft),
                     (-((l / 2.0) + ft), -(fw / 2.0), h + ft),
                     (+((l / 2.0) + ft), -(fw / 2.0), h + ft),
                     (-(l / 2.0), +(fw / 2.0), 0.0),
                     (+(l / 2.0), +(fw / 2.0), 0.0),
                     (-(l / 2.0), -(fw / 2.0), 0.0),
                     (+(l / 2.0), -(fw / 2.0), 0.0),
                     (-(l / 2.0), +(fw / 2.0), h),
                     (+(l / 2.0), +(fw / 2.0), h),
                     (-(l / 2.0), -(fw / 2.0), h),
                     (+(l / 2.0), -(fw / 2.0), h),
                     (-((l / 2.0) + (ft / 2.0)), +((fw / 2.0) - (dw / 2.0)), 0.0),
                     (+((l / 2.0) + (ft / 2.0)), +((fw / 2.0) - (dw / 2.0)), 0.0),
                     (-((l / 2.0) + (ft / 2.0)), -((fw / 2.0) - (dw / 2.0)), 0.0),
                     (+((l / 2.0) + (ft / 2.0)), -((fw / 2.0) - (dw / 2.0)), 0.0),
                     (-((l / 2.0) + (ft / 2.0)), +((fw / 2.0) - (dw / 2.0)), h + (ft / 2.0)),
                     (+((l / 2.0) + (ft / 2.0)), +((fw / 2.0) - (dw / 2.0)), h + (ft / 2.0)),
                     (-((l / 2.0) + (ft / 2.0)), -((fw / 2.0) - (dw / 2.0)), h + (ft / 2.0)),
                     (+((l / 2.0) + (ft / 2.0)), -((fw / 2.0) - (dw / 2.0)), h + (ft / 2.0)),
                     (-(l / 2.0), +((fw / 2.0) - (dw / 2.0)), 0.0),
                     (+(l / 2.0), +((fw / 2.0) - (dw / 2.0)), 0.0),
                     (-(l / 2.0), -((fw / 2.0) - (dw / 2.0)), 0.0),
                     (+(l / 2.0), -((fw / 2.0) - (dw / 2.0)), 0.0),
                     (-(l / 2.0), +((fw / 2.0) - (dw / 2.0)), h),
                     (+(l / 2.0), +((fw / 2.0) - (dw / 2.0)), h),
                     (-(l / 2.0), -((fw / 2.0) - (dw / 2.0)), h),
                     (+(l / 2.0), -((fw / 2.0) - (dw / 2.0)), h),
                    ]
                    
            faces = [(6, 2, 10, 14),
                     (6, 14, 15, 7),
                     (15, 11, 3, 7),
                     (7, 3, 1, 5),
                     (6, 4, 0, 2),
                     (6, 7, 5, 4),
                     (4, 12, 8, 0),
                     (5, 13, 12, 4),
                     (5, 1, 9, 13),
                     
                     (12, 28, 24, 8),
                     (28, 20, 16, 24),
                     (20, 22, 18, 16),
                     (22, 30, 26, 18),
                     (30, 14, 10, 26),
                     (29, 13, 9, 25),
                     (21, 29, 25, 17),
                     (23, 21, 17, 19),
                     (31, 23, 19, 27),
                     (15, 31, 27, 11),
                     (30, 22, 23, 31),
                     (20, 28, 29, 21),
                     (21, 23, 22, 20),
                     (12, 13, 29, 28),
                     (31, 15, 14, 30),
                    ]

        for v_co in verts:
            bm2.verts.new(v_co)

        bm2.verts.ensure_lookup_table()
        for f_idx in faces:
            bm2.faces.new([bm2.verts[i] for i in f_idx])
        
        if style == 'HINGE':
            #Flip the door around based on the
                #direction it is supposed to face:
                if hinge == 'LI' or hinge == 'LO':
                    for v in bm2.verts:
                        v.co.x *= -1
                
                if hinge == 'LO' or hinge == 'RO':
                    for v in bm2.verts:
                        v.co.y *= -1
                
                #recalculate normals:
                bmesh.ops.recalc_face_normals(bm2, faces=bm2.faces)

        bm2.to_mesh(mesh2)
        mesh2.update()
        
        #Now make the door
        mesh3 = bpy.data.meshes.new("Door")
        door_obj = bpy.data.objects.new("Door_Obj", mesh3)

        scene = bpy.context.scene
        scene.objects.link(door_obj)

        bm3 = bmesh.new()
        
        #Make the door hinges if
        #the door style is HINGE
        dg = gap / 2.0
        if style == 'HINGE':
            #shift hinges by the door_gap / 2.0
            
            
            verts = [(((-l / 2.0) - 0.0005 + dg), (+hd + (fw / 2.0)), (h / 6.0) - (hh / 2.0)),
                     (((-l / 2.0) - 0.0005 + dg), (-hw + (fw / 2.0)), (h / 6.0) - (hh / 2.0)),
                     (((-l / 2.0) - (hd / 2.0) + dg), (+hd + (fw / 2.0)), (h / 6.0) - (hh / 2.0)),
                     (((-l / 2.0) - (hd / 2.0) + dg), (-hw + (fw / 2.0)), (h / 6.0) - (hh / 2.0)),
                     (((-l / 2.0) - 0.0005 + dg), (+hd + (fw / 2.0)), (h / 6.0) + (hh / 2.0)),
                     (((-l / 2.0) - 0.0005 + dg), (-hw + (fw / 2.0)), (h / 6.0) + (hh / 2.0)),
                     (((-l / 2.0) - (hd / 2.0) + dg), (+hd + (fw / 2.0)), (h / 6.0) + (hh / 2.0)),
                     (((-l / 2.0) - (hd / 2.0) + dg), (-hw + (fw / 2.0)), (h / 6.0) + (hh / 2.0)),
                     
                     (((-l / 2.0) + (hd / 2.0) + dg), (+hd + (fw / 2.0)), (h / 6.0) - (hh / 2.0)),
                     (((-l / 2.0) + (hd / 2.0) + dg), (-hw + (fw / 2.0)), (h / 6.0) - (hh / 2.0)),
                     (((-l / 2.0) + 0.0005 + dg), (+hd + (fw / 2.0)), (h / 6.0) - (hh / 2.0)),
                     (((-l / 2.0) + 0.0005 + dg), (-hw + (fw / 2.0)), (h / 6.0) - (hh / 2.0)),
                     (((-l / 2.0) + (hd / 2.0) + dg), (+hd + (fw / 2.0)), (h / 6.0) + (hh / 2.0)),
                     (((-l / 2.0) + (hd / 2.0) + dg), (-hw + (fw / 2.0)), (h / 6.0) + (hh / 2.0)),
                     (((-l / 2.0) + 0.0005 + dg), (+hd + (fw / 2.0)), (h / 6.0) + (hh / 2.0)),
                     (((-l / 2.0) + 0.0005 + dg), (-hw + (fw / 2.0)), (h / 6.0) + (hh / 2.0)),
                     
                     (+((l / 2.0) - gap), ((fw / 2.0) + ds), fgap),
                     (+((l / 2.0) - gap), ((fw / 2.0) - dw + ds), fgap),
                     (-((l / 2.0) - gap), ((fw / 2.0) - dw + ds), fgap),
                     (-((l / 2.0) - gap), ((fw / 2.0) + ds), fgap),
                     (+((l / 2.0) - gap), ((fw / 2.0) + ds), +(h - gap)),
                     (+((l / 2.0) - gap), ((fw / 2.0) - dw + ds), +(h - gap)),
                     (-((l / 2.0) - gap), ((fw / 2.0) - dw + ds), +(h - gap)),
                     (-((l / 2.0) - gap), ((fw / 2.0) + ds), +(h - gap)),
                     
                     (((-l / 2.0) - 0.0005 + dg), (+hd + (fw / 2.0)), (h / 2.0) - (hh / 2.0)),
                     (((-l / 2.0) - 0.0005 + dg), (-hw + (fw / 2.0)), (h / 2.0) - (hh / 2.0)),
                     (((-l / 2.0) - (hd / 2.0) + dg), (+hd + (fw / 2.0)), (h / 2.0) - (hh / 2.0)),
                     (((-l / 2.0) - (hd / 2.0) + dg), (-hw + (fw / 2.0)), (h / 2.0) - (hh / 2.0)),
                     (((-l / 2.0) - 0.0005 + dg), (+hd + (fw / 2.0)), (h / 2.0) + (hh / 2.0)),
                     (((-l / 2.0) - 0.0005 + dg), (-hw + (fw / 2.0)), (h / 2.0) + (hh / 2.0)),
                     (((-l / 2.0) - (hd / 2.0) + dg), (+hd + (fw / 2.0)), (h / 2.0) + (hh / 2.0)),
                     (((-l / 2.0) - (hd / 2.0) + dg), (-hw + (fw / 2.0)), (h / 2.0) + (hh / 2.0)),
                     
                     (((-l / 2.0) + (hd / 2.0) + dg), (+hd + (fw / 2.0)), (h / 2.0) - (hh / 2.0)),
                     (((-l / 2.0) + (hd / 2.0) + dg), (-hw + (fw / 2.0)), (h / 2.0) - (hh / 2.0)),
                     (((-l / 2.0) + 0.0005 + dg), (+hd + (fw / 2.0)), (h / 2.0) - (hh / 2.0)),
                     (((-l / 2.0) + 0.0005 + dg), (-hw + (fw / 2.0)), (h / 2.0) - (hh / 2.0)),
                     (((-l / 2.0) + (hd / 2.0) + dg), (+hd + (fw / 2.0)), (h / 2.0) + (hh / 2.0)),
                     (((-l / 2.0) + (hd / 2.0) + dg), (-hw + (fw / 2.0)), (h / 2.0) + (hh / 2.0)),
                     (((-l / 2.0) + 0.0005 + dg), (+hd + (fw / 2.0)), (h / 2.0) + (hh / 2.0)),
                     (((-l / 2.0) + 0.0005 + dg), (-hw + (fw / 2.0)), (h / 2.0) + (hh / 2.0)),
                     
                     (((-l / 2.0) - 0.0005 + dg), (+hd + (fw / 2.0)), ((5 * h) / 6.0) - (hh / 2.0)),
                     (((-l / 2.0) - 0.0005 + dg), (-hw + (fw / 2.0)), ((5 * h) / 6.0) - (hh / 2.0)),
                     (((-l / 2.0) - (hd / 2.0) + dg), (+hd + (fw / 2.0)), ((5 * h) / 6.0) - (hh / 2.0)),
                     (((-l / 2.0) - (hd / 2.0) + dg), (-hw + (fw / 2.0)), ((5 * h) / 6.0) - (hh / 2.0)),
                     (((-l / 2.0) - 0.0005 + dg), (+hd + (fw / 2.0)), ((5 * h) / 6.0) + (hh / 2.0)),
                     (((-l / 2.0) - 0.0005 + dg), (-hw + (fw / 2.0)), ((5 * h) / 6.0) + (hh / 2.0)),
                     (((-l / 2.0) - (hd / 2.0) + dg), (+hd + (fw / 2.0)), ((5 * h) / 6.0) + (hh / 2.0)),
                     (((-l / 2.0) - (hd / 2.0) + dg), (-hw + (fw / 2.0)), ((5 * h) / 6.0) + (hh / 2.0)),
                     
                     (((-l / 2.0) + (hd / 2.0) + dg), (+hd + (fw / 2.0)), ((5 * h) / 6.0) - (hh / 2.0)),
                     (((-l / 2.0) + (hd / 2.0) + dg), (-hw + (fw / 2.0)), ((5 * h) / 6.0) - (hh / 2.0)),
                     (((-l / 2.0) + 0.0005 + dg), (+hd + (fw / 2.0)), ((5 * h) / 6.0) - (hh / 2.0)),
                     (((-l / 2.0) + 0.0005 + dg), (-hw + (fw / 2.0)), ((5 * h) / 6.0) - (hh / 2.0)),
                     (((-l / 2.0) + (hd / 2.0) + dg), (+hd + (fw / 2.0)), ((5 * h) / 6.0) + (hh / 2.0)),
                     (((-l / 2.0) + (hd / 2.0) + dg), (-hw + (fw / 2.0)), ((5 * h) / 6.0) + (hh / 2.0)),
                     (((-l / 2.0) + 0.0005 + dg), (+hd + (fw / 2.0)), ((5 * h) / 6.0) + (hh / 2.0)),
                     (((-l / 2.0) + 0.0005 + dg), (-hw + (fw / 2.0)), ((5 * h) / 6.0) + (hh / 2.0)),
                    ]
            
            faces = [(0, 1, 3, 2),
                     (4, 6, 7, 5),
                     (5, 1, 0, 4),
                     (6, 4, 0, 2),
                     (7, 6, 2, 3),
                     (5, 7, 3, 1),
                     (8, 9, 11, 10),
                     (12, 14, 15, 13),
                     (13, 9, 8, 12),
                     (14, 12, 8, 10),
                     (15, 14, 10, 11),
                     (13, 15, 11, 9),
                     
                     (16, 17, 18, 19),
                     (20, 23, 22, 21),
                     (16, 20, 21, 17),
                     (17, 21, 22, 18),
                     (18, 22, 23, 19),
                     (20, 16, 19, 23),
                     
                     (24, 25, 27, 26),
                     (28, 30, 31, 29),
                     (29, 25, 24, 28),
                     (30, 28, 24, 26),
                     (31, 30, 26, 27),
                     (29, 31, 27, 25),
                     (32, 33, 35, 34),
                     (36, 38, 39, 37),
                     (37, 33, 32, 36),
                     (38, 36, 32, 34),
                     (39, 38, 34, 35),
                     (37, 39, 35, 33),
                     
                     (40, 41, 43, 42),
                     (44, 46, 47, 45),
                     (45, 41, 40, 44),
                     (46, 44, 40, 42),
                     (47, 46, 42, 43),
                     (45, 47, 43, 41),
                     (48, 49, 51, 50),
                     (52, 54, 55, 53),
                     (53, 49, 48, 52),
                     (54, 52, 48, 50),
                     (55, 54, 50, 51),
                     (53, 55, 51, 49),
                    ]
            
            for v_co in verts:
                bm3.verts.new(v_co)

            bm3.verts.ensure_lookup_table()
            for f_idx in faces:
                bm3.faces.new([bm3.verts[i] for i in f_idx])
                
            
            if style == 'HINGE':
                #Flip the door around based on the
                #direction it is supposed to face:
                if hinge == 'LI' or hinge == 'LO':
                    for v in bm3.verts:
                        v.co.x *= -1
                
                if hinge == 'LO' or hinge == 'RO':
                    for v in bm3.verts:
                        v.co.y *= -1
                
                #recalculate normals:
                bmesh.ops.recalc_face_normals(bm3, faces=bm3.faces)
            
            bm3.to_mesh(mesh3)
            mesh3.update()
            
            #Now for the hinge pins
            mesh4 = bpy.data.meshes.new("Hinge")
            hinge_obj = bpy.data.objects.new("Hinge_Obj", mesh4)
            
            scene.objects.link(hinge_obj)
            
            bm4 = bmesh.new()
            
            #Bottom hinge pin:
            cyl_loc = mathutils.Matrix.Translation((((-l / 2.0) + dg), (+(fw / 2.0) + hd), (h / 6.0)))
            bmesh.ops.create_cone(bm4, cap_ends=False, cap_tris=False, segments=hs, diameter1=hd, diameter2=hd, depth=hc, matrix=cyl_loc, calc_uvs=False)
            #Middle hinge pin:
            cyl_loc = mathutils.Matrix.Translation((((-l / 2.0) + dg), (+(fw / 2.0) + hd), (h / 2.0)))
            bmesh.ops.create_cone(bm4, cap_ends=False, cap_tris=False, segments=hs, diameter1=hd, diameter2=hd, depth=hc, matrix=cyl_loc, calc_uvs=False)
            #Top hinge pin:
            cyl_loc = mathutils.Matrix.Translation((((-l / 2.0) + dg), (+(fw / 2.0) + hd), ((5 * h) / 6.0)))
            bmesh.ops.create_cone(bm4, cap_ends=False, cap_tris=False, segments=hs, diameter1=hd, diameter2=hd, depth=hc, matrix=cyl_loc, calc_uvs=False)
            
            #Now smooth all faces
            for f in bm4.faces:
                f.smooth = True
                
            #Add the top and bottom faces
            hinge_top=mathutils.Matrix.Translation((((-l / 2.0) + dg), (+(fw / 2.0) + hd), ((h / 6.0) + (hc / 2.0))))
            hinge_bottom=mathutils.Matrix.Translation((((-l / 2.0) + dg), (+(fw / 2.0) + hd), ((h / 6.0) - (hc / 2.0))))
            bmesh.ops.create_circle(bm4, cap_ends=True, cap_tris=False, segments=hs, diameter=hd, matrix=hinge_top, calc_uvs=False)
            bmesh.ops.create_circle(bm4, cap_ends=True, cap_tris=False, segments=hs, diameter=hd, matrix=hinge_bottom, calc_uvs=False)
            
            #Middle hinge pin faces:
            hinge_top=mathutils.Matrix.Translation((((-l / 2.0) + dg), (+(fw / 2.0) + hd), ((h / 2.0) + (hc / 2.0))))
            hinge_bottom=mathutils.Matrix.Translation((((-l / 2.0) + dg), (+(fw / 2.0) + hd), ((h / 2.0) - (hc / 2.0))))
            bmesh.ops.create_circle(bm4, cap_ends=True, cap_tris=False, segments=hs, diameter=hd, matrix=hinge_top, calc_uvs=False)
            bmesh.ops.create_circle(bm4, cap_ends=True, cap_tris=False, segments=hs, diameter=hd, matrix=hinge_bottom, calc_uvs=False)
            
            #Top hinge pin faces:
            hinge_top=mathutils.Matrix.Translation((((-l / 2.0) + dg), (+(fw / 2.0) + hd), (((5 * h) / 6.0) + (hc / 2.0))))
            hinge_bottom=mathutils.Matrix.Translation((((-l / 2.0) + dg), (+(fw / 2.0) + hd), (((5 * h) / 6.0) - (hc / 2.0))))
            bmesh.ops.create_circle(bm4, cap_ends=True, cap_tris=False, segments=hs, diameter=hd, matrix=hinge_top, calc_uvs=False)
            bmesh.ops.create_circle(bm4, cap_ends=True, cap_tris=False, segments=hs, diameter=hd, matrix=hinge_bottom, calc_uvs=False)
            
            #Flip the door around based on the
            #direction it is supposed to face:
            if hinge == 'LI' or hinge == 'LO':
                for v in bm4.verts:
                    v.co.x *= -1
            
            if hinge == 'LO' or hinge == 'RO':
                for v in bm4.verts:
                    v.co.y *= -1
            
            #recalculate normals:
            bmesh.ops.recalc_face_normals(bm4, faces=bm4.faces)
            
            #make the bmesh data into mesh data
            bm4.to_mesh(mesh4)
            mesh4.update()
            
            #Combine the hinge object with the door
            bpy.ops.object.select_all(action='DESELECT')
            hinge_obj.select=True
            door_obj.select=True
            bpy.context.scene.objects.active = door_obj
            bpy.ops.object.join()
            bpy.ops.object.select_all(action='DESELECT')
        
        #Otherwise, if it's a SLIDE door:
        elif style == 'SLIDE':
            
            verts = [(+((l / 2.0) + (ft / 2.0) - dg), +((fw / 2.0) - dg - ft), 0.0),
                     (+((l / 2.0) + (ft / 2.0) - dg), -((fw / 2.0) - dg - ft), 0.0),
                     (-((l / 2.0) + (ft / 2.0) - dg), +((fw / 2.0) - dg - ft), 0.0),
                     (-((l / 2.0) + (ft / 2.0) - dg), -((fw / 2.0) - dg - ft), 0.0),
                     (+((l / 2.0) + (ft / 2.0) - dg), +((fw / 2.0) - dg - ft), +(h + (ft / 2.0) - dg)),
                     (+((l / 2.0) + (ft / 2.0) - dg), -((fw / 2.0) - dg - ft), +(h + (ft / 2.0) - dg)),
                     (-((l / 2.0) + (ft / 2.0) - dg), +((fw / 2.0) - dg - ft), +(h + (ft / 2.0) - dg)),
                     (-((l / 2.0) + (ft / 2.0) - dg), -((fw / 2.0) - dg - ft), +(h + (ft / 2.0) - dg)),
                    ]
                    
            faces = [(0, 1, 3, 2),
                     (4, 6, 7, 5),
                     (5, 1, 0, 4),
                     (6, 4, 0, 2),
                     (7, 6, 2, 3),
                     (5, 7, 3, 1),
                    ]
            
            for v_co in verts:
                bm3.verts.new(v_co)

            bm3.verts.ensure_lookup_table()
            for f_idx in faces:
                bm3.faces.new([bm3.verts[i] for i in f_idx])
            
            bm3.to_mesh(mesh3)
            mesh3.update()
        
        #boolean out space for glass if needed:
        if has_glass == True:
            
            #If they want the whole door to be
            #glass then just swap the material
            if glass_w < l and glass_h < h:
                
                mesh5 = bpy.data.meshes.new("Glass_Bool")
                glass_bool_obj = bpy.data.objects.new("Glass_Bool_Obj", mesh5)
                
                scene.objects.link(glass_bool_obj)
                
                bm5 = bmesh.new()
                
                verts = [(((glass_w / 2.0) + glass_x), +((fw + 0.125) / 2.0), +((-glass_h / 2.0) + glass_y + (h / 2.0))),
                         (((glass_w / 2.0) + glass_x), -((fw + 0.125) / 2.0), +((-glass_h / 2.0) + glass_y + (h / 2.0))),
                         (((-glass_w / 2.0) + glass_x), +((fw + 0.125) / 2.0), +((-glass_h / 2.0) + glass_y + (h / 2.0))),
                         (((-glass_w / 2.0) + glass_x), -((fw + 0.125) / 2.0), +((-glass_h / 2.0) + glass_y + (h / 2.0))),
                         (((glass_w / 2.0) + glass_x), +((fw + 0.125) / 2.0), +((glass_h / 2.0) + glass_y + (h / 2.0))),
                         (((glass_w / 2.0) + glass_x), -((fw + 0.125) / 2.0), +((glass_h / 2.0) + glass_y + (h / 2.0))),
                         (((-glass_w / 2.0) + glass_x), +((fw + 0.125) / 2.0), +((glass_h / 2.0) + glass_y + (h / 2.0))),
                         (((-glass_w / 2.0) + glass_x), -((fw + 0.125) / 2.0), +((glass_h / 2.0) + glass_y + (h / 2.0))),
                        ]
                
                faces = [(0, 1, 3, 2),
                         (4, 6, 7, 5),
                         (5, 1, 0, 4),
                         (6, 4, 0, 2),
                         (7, 6, 2, 3),
                         (5, 7, 3, 1),
                        ]
                
                for v_co in verts:
                    bm5.verts.new(v_co)

                bm5.verts.ensure_lookup_table()
                for f_idx in faces:
                    bm5.faces.new([bm5.verts[i] for i in f_idx])
                
                bm5.to_mesh(mesh5)
                mesh5.update()
                
                bpy.ops.object.select_all(action='DESELECT')
                bpy.context.scene.objects.active = door_obj
                door_obj.data = door_obj.data.copy()
                cut = door_obj.modifiers.new("cut_window", type='BOOLEAN')
                cut.operation = 'DIFFERENCE'
                cut.object = glass_bool_obj
                bpy.ops.object.modifier_apply(apply_as='DATA', modifier=cut.name)
                bpy.ops.object.select_all(action='DESELECT')
                glass_bool_obj.select = True
                bpy.ops.object.delete()
                
                #Make the glass that goes in that space
                mesh6 = bpy.data.meshes.new("Glass")
                glass_obj = bpy.data.objects.new("Glass_Obj", mesh6)
                
                scene.objects.link(glass_obj)
                
                bm6 = bmesh.new()
                
                if style == 'HINGE':
                    verts = [(((glass_w / 2.0) + glass_x), ((glass_t / 2.0) + dw + ds), ((glass_h / 2.0) + glass_y + (h / 2.0))),
                             (((glass_w / 2.0) + glass_x), ((glass_t / 2.0) + dw + ds), ((-glass_h / 2.0) + glass_y + (h / 2.0))),
                             (((-glass_w / 2.0) + glass_x), ((glass_t / 2.0) + dw + ds), ((-glass_h / 2.0) + glass_y + (h / 2.0))),
                             (((-glass_w / 2.0) + glass_x), ((glass_t / 2.0) + dw + ds), ((glass_h / 2.0) + glass_y + (h / 2.0))),
                             (((glass_w / 2.0) + glass_x), ((-glass_t / 2.0) + dw + ds), ((glass_h / 2.0) + glass_y + (h / 2.0))),
                             (((glass_w / 2.0) + glass_x), ((-glass_t / 2.0) + dw + ds), ((-glass_h / 2.0) + glass_y + (h / 2.0))),
                             (((-glass_w / 2.0) + glass_x), ((-glass_t / 2.0) + dw + ds), ((-glass_h / 2.0) + glass_y + (h / 2.0))),
                             (((-glass_w / 2.0) + glass_x), ((-glass_t / 2.0) + dw + ds), ((glass_h / 2.0) + glass_y + (h / 2.0))),
                            ]
                elif style == 'SLIDE':
                    verts = [(((glass_w / 2.0) + glass_x), (glass_t / 2.0), ((glass_h / 2.0) + glass_y + (h / 2.0))),
                             (((glass_w / 2.0) + glass_x), (glass_t / 2.0), ((-glass_h / 2.0) + glass_y + (h / 2.0))),
                             (((-glass_w / 2.0) + glass_x), (glass_t / 2.0), ((-glass_h / 2.0) + glass_y + (h / 2.0))),
                             (((-glass_w / 2.0) + glass_x), (glass_t / 2.0), ((glass_h / 2.0) + glass_y + (h / 2.0))),
                             (((glass_w / 2.0) + glass_x), (-glass_t / 2.0), ((glass_h / 2.0) + glass_y + (h / 2.0))),
                             (((glass_w / 2.0) + glass_x), (-glass_t / 2.0), ((-glass_h / 2.0) + glass_y + (h / 2.0))),
                             (((-glass_w / 2.0) + glass_x), (-glass_t / 2.0), ((-glass_h / 2.0) + glass_y + (h / 2.0))),
                             (((-glass_w / 2.0) + glass_x), (-glass_t / 2.0), ((glass_h / 2.0) + glass_y + (h / 2.0))),
                            ]
                
                faces = [(0, 1, 2, 3),
                         (7, 6, 5, 4),
                        ]
                
                for v_co in verts:
                    bm6.verts.new(v_co)

                bm6.verts.ensure_lookup_table()
                for f_idx in faces:
                    bm6.faces.new([bm6.verts[i] for i in f_idx])
                
                bm6.to_mesh(mesh6)
                mesh6.update()
                
                bpy.ops.object.select_all(action='DESELECT')
                door_obj.select = True
                glass_obj.select = True
                bpy.context.scene.objects.active = door_obj
                bpy.ops.object.join()
                bpy.ops.object.select_all(action='DESELECT')

        return {'FINISHED'}


def menu_func(self, context):
    self.layout.operator(AddDoor.bl_idname, icon='MOD_WIREFRAME')


def register():
    bpy.utils.register_class(AddDoor)
    bpy.types.INFO_MT_mesh_add.append(menu_func)


def unregister():
    bpy.utils.unregister_class(AddDoor)
    bpy.types.INFO_MT_mesh_add.remove(menu_func)

if __name__ == "__main__":
    register()
