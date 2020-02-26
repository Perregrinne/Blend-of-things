bl_info = {
    "name": "Structure Generator",
    "description": "Generate Structures",
    "author": "Austin Jacob",
    "version": (4, 0, 0),
    "blender": (2, 79, 0),
    "location": "View3D > Add > Mesh",
    "warning": "", # used for warning icon and text in addons panel
    "wiki_url": "",
    "tracker_url": "",
    "category": "Add Mesh"}

import bpy
import bmesh

from bpy_extras import object_utils




#Generate a box at the coordinates of where the structures overlap. Boolean all objects (of 'MESH' type) that the box touches.
#Iterate through all objects and compare: objectType = bpy.context.object.type  to see if type == 'MESH' and if so, check to see if it's
#Overlapping the current object, using a boolean modifier. If the list of vertices returned from that boolean is empty, they do no overlap.
#If they do, get the location of each, dimensions, calculate where the overlap would be, and then add a boolean box accordingly.
"""
for o in bpy.data.object:
    overlapping_verts = get_verts()
    if len(overlapping_verts) > 0:
        #generate a box here
        #do boolean stuff (use the box to cut itself out of both structures)
        """



#Returns a list of all vertices within specified bounds
#x, y, and z are the center of the bounds,
#length, width, and height are the dimensions of the bounds
#verts is the list of vertices the function will look through to see if any are within bounds
def get_verts(x, y, z, length, width, height, verts, context, self):
    
    within_bounds = []
    for v in verts:
        #Check to see if it's within the x-axis range
        if v.co.x <= (x + (length / 2.0)) and v.co.x >= -(x + (length / 2.0)):
            #Now check the y-axis
            if v.co.y <= (y + (width / 2.0)) and v.co.y >= -(y + (width / 2.0)):
                #And finally, check the z-axis
                if v.co.z <= (z + (height / 2.0)) and v.co.z >= -(z + (height / 2.0)):
                    within_bounds += [v]
                    
    return within_bounds

#Selects all vertices within specified bounds
#x, y, and z are the center of the bounds,
#length, width, and height are the dimensions of the bounds
#verts is the list of vertices the function will look through to see if any are within bounds
def select_v_in_bounds(x, y, z, length, width, height, verts):
    
    for v in verts:
        #Check to see if it's within the x-axis range
        if v.co.x <= (x + (length / 2.0)) and v.co.x >= (x - (length / 2.0)):
            #Now check the y-axis
            if v.co.y <= (y + (width / 2.0)) and v.co.y >= (y - (width / 2.0)):
                #And finally, check the z-axis
                if v.co.z <= (z + (height / 2.0)) and v.co.z >= (z - (height / 2.0)):
                    v.select = True

#Selcts edges within specified bounds, if both of its vertices are within bounds
#x, y, and z are the center of the bounds
#length, width, height, determine the size of the bounds
#edges is the list of edges to check
def select_e_in_bounds(x, y, z, length, width, height, edges):
    
    for e in edges:
        v = e.verts[0]
        #Check to see if it's within the x-axis range
        if v.co.x <= (x + (length / 2.0)) and v.co.x >= (x - (length / 2.0)):
            #Now check the y-axis
            if v.co.y <= (y + (width / 2.0)) and v.co.y >= (y - (width / 2.0)):
                #And finally, check the z-axis
                if v.co.z <= (z + (height / 2.0)) and v.co.z >= (z - (height / 2.0)):
                    v.select = True
        v = e.verts[1]
        #Check to see if it's within the x-axis range
        if v.co.x <= (x + (length / 2.0)) and v.co.x >= (x - (length / 2.0)):
            #Now check the y-axis
            if v.co.y <= (y + (width / 2.0)) and v.co.y >= (y - (width / 2.0)):
                #And finally, check the z-axis
                if v.co.z <= (z + (height / 2.0)) and v.co.z >= (z - (height / 2.0)):
                    v.select = True
        if e.verts[0].select and e.verts[1].select:
            e.select = True

#Generates only the exterior portion of the building, no floors or rooms
#The shell of the building can have its corners individually beveled to create different shapes
def generate_exterior(length, width, fcd, floors, f_thick, lf_bev, rf_bev, lr_bev, rr_bev, lf_str, lf_seg, rf_str, rf_seg, lr_str, lr_seg, rr_str, rr_seg, context, self):
    print("Placeholder")
    
#Generates each floor that makes up the interior part of the structure
#If the exterior corners are beveled, then the interior corners will match
def generate_interior(length, width, fcd, floors, w_thick, f_thick, lf_bev, rf_bev, lr_bev, rr_bev, lf_str, lf_seg, rf_str, rf_seg, lr_str, lr_seg, rr_str, rr_seg, context, self):
    print("Hi")

#Creates a roof to sit on top of the open exterior section
#Selecting 'NONE' for roof type simply puts a plane on top of the open exterior
#It also matches the bevel of the rest of the building
def generate_roof(length, width, fcd, floors, r_thick, w_thick, f_thick, lf_bev, rf_bev, lr_bev, rr_bev, lf_str, lf_seg, rf_str, rf_seg, lr_str, lr_seg, rr_str, rr_seg, roof, context, self):
    print("Nothing actually calls this function anymore")
    

from bpy.props import (
        BoolProperty,
        BoolVectorProperty,
        FloatProperty,
        FloatVectorProperty,
        IntProperty,
        EnumProperty,
        )


class AddStructure(bpy.types.Operator):
    """Add a structure mesh"""
    bl_idname = "mesh.structure_add"
    bl_label = "Add Structure"
    bl_options = {'REGISTER', 'UNDO'}

    length = FloatProperty(
            name="Length",
            description="Structure Length (x-axis)",
            min=4.0,
            default=6.0,
            )
    width = FloatProperty(
            name="Width",
            description="Structure Width (y-axis)",
            min=4.0,
            default=10.0,
            )
    floor_ceil_dist = FloatProperty(
            name="Floor Height",
            description="Distance from the floor to the ceiling",
            min=1.0,
            default=2.5,
            )
    floors = IntProperty(
            name="Floors",
            description="Number of floors in the structure",
            min=1,
            default=3,
            )
    lf_seg = IntProperty(
            name="Left-Front Bevel Segments",
            description="Number of segments that make up the bevel applied to the left-front corner",
            min=0,
            default=0,
            )
    lf_str = FloatProperty(
            name="Left-Front Bevel Strength",
            description="How much to bevel the left-front corner",
            min=0.0, max=100,
            default=0.0,
            )
    rf_seg = IntProperty(
            name="Right-Front Bevel Segments",
            description="Number of segments that make up the bevel applied to the right-front corner",
            min=0,
            default=0,
            )
    rf_str = FloatProperty(
            name="Right-Front Bevel Strength",
            description="How much to bevel the right-front corner",
            min=0.0, max=100,
            default=0.0,
            )
    lr_seg = IntProperty(
            name="Left-Rear Bevel Segments",
            description="Number of segments that make up the bevel applied to the left-rear corner",
            min=0,
            default=0,
            )
    lr_str = FloatProperty(
            name="Left-Rear Bevel Strength",
            description="How much to bevel the left-rear corner",
            min=0.0, max=100,
            default=0.0,
            )
    rr_seg = IntProperty(
            name="Right-Rear Bevel Segments",
            description="Number of segments that make up the bevel applied to the right-rear corner",
            min=0,
            default=0,
            )
    rr_str = FloatProperty(
            name="Right-Rear Bevel Strength",
            description="How much to bevel the right-rear corner",
            min=0.0, max=100,
            default=0.0,
            )
    lf_bev = EnumProperty(
            name="Left-Right Bevel Method",
            description="Changes the offset type of the bevel",
            items=(('WIDTH', 'Width', 'The bevel is based off of the width of the new faces'),
                   ('PERCENT', 'Percent', 'Uses a percentage of the adjacent edges')),
            default='PERCENT',
            )
    rf_bev = EnumProperty(
            name="Right-Front Bevel Method",
            description="Changes the offset type of the bevel",
            items=(('WIDTH', 'Width', 'The bevel is based off of the width of the new faces'),
                   ('PERCENT', 'Percent', 'Uses a percentage of the adjacent edges')),
            default='PERCENT',
            )
    lr_bev = EnumProperty(
            name="Left-Rear Bevel Method",
            description="Changes the offset type of the bevel",
            items=(('WIDTH', 'Width', 'The bevel is based off of the width of the new faces'),
                   ('PERCENT', 'Percent', 'Uses a percentage of the adjacent edges')),
            default='PERCENT',
            )
    rr_bev = EnumProperty(
            name="Right-Rear Bevel Method",
            description="Changes the offset type of the bevel",
            items=(('WIDTH', 'Width', 'The bevel is based off of the width of the new faces'),
                   ('PERCENT', 'Percent', 'Uses a percentage of the adjacent edges')),
            default='PERCENT',
            )
    floor_thickness = FloatProperty(
            name="Floor Thickness",
            description="How far apart each floor is from one another",
            min=0.01,
            default=0.3,
            )
    wall_thickness = FloatProperty(
            name="Wall Thickness",
            description="How thick the walls are",
            min=0.01,
            default=0.15,
            )
    roof_type = EnumProperty(
            name="Roof Type",
            description="Type of roof the building has",
            items=(('FLAT', 'Flat', 'A flat roof'),
                   ('GABLE', 'Gable', 'A gable roof'),
                   ('BEVEL', 'Bevel', 'A beveled roof'),
                   ('NONE', 'None', 'Just a flat plane to cover the top')),
            default='FLAT',
            )
    roof_height = FloatProperty(
            name="Roof Height",
            description="How tall the roof is",
            min=0.0,
            default=0.3,
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
    
    def draw(self, context):
        layout = self.layout
        
        box = layout.box()
        col = box.column()
        col.label(text="Structure", icon="VIEW3D")
        col.prop(self, "length")
        col.prop(self, "width")
        col.prop(self, "wall_thickness")
        col.prop(self, "location")
        col.prop(self, "rotation")
        col.prop(self, "view_align")
        
        box = layout.box()
        col = box.column()
        col.label(text="Floors", icon="MOD_ARRAY")
        col.prop(self, "floors")
        col.prop(self, "floor_ceil_dist")
        col.prop(self, "floor_thickness")
        
        box = layout.box()
        col = box.column()
        col.label(text="Roof", icon="NOCURVE")
        col.prop(self, "roof_type")
        col.prop(self, "roof_height")
        
        box = layout.box()
        col = box.column()
        col.label(text="Bevel", icon="MOD_BEVEL")
        col.prop(self, "lf_bev")
        col.prop(self, "lf_str")
        col.prop(self, "lf_seg")
        col.prop(self, "rf_bev")
        col.prop(self, "rf_str")
        col.prop(self, "rf_seg")
        col.prop(self, "lr_bev")
        col.prop(self, "lr_str")
        col.prop(self, "lr_seg")
        col.prop(self, "rr_bev")
        col.prop(self, "rr_str")
        col.prop(self, "rr_seg")

    def execute(self, context):
        
        #rename the variables to something easier
        length = self.length
        width = self.width
        fcd = self.floor_ceil_dist
        floors = self.floors
        f_thick = self.floor_thickness
        r_thick = self.roof_height
        w_thick = self.wall_thickness
        roof = self.roof_type
        lf_seg = self.lf_seg
        lf_str = self.lf_str
        lr_seg = self.lr_seg
        lr_str = self.lr_str
        rf_seg = self.rf_seg
        rf_str = self.rf_str
        rr_seg = self.rr_seg
        rr_str = self.rr_str
        lf_bev = self.lf_bev
        rf_bev = self.rf_bev
        lr_bev = self.lr_bev
        rr_bev = self.rr_bev
        
        #Make the exterior:
        height = floors * (fcd + f_thick)
        
        verts = [(+(length / 2.0), +(width / 2.0), +0.0),
                 (+(length / 2.0), +0.0, +0.0),
                 (+(length / 2.0), -(width / 2.0), +0.0),
                 (+0.0, -(width / 2.0), +0.0),
                 (-(length / 2.0), -(width / 2.0), +0.0),
                 (-(length / 2.0), +0.0, +0.0),
                 (-(length / 2.0), +(width / 2.0), +0.0),
                 (+0.0, +(width / 2.0), +0.0),
                 (+(length / 2.0), +(width / 2.0), +(height)),
                 (+(length / 2.0), +0.0, +(height)),
                 (+(length / 2.0), -(width / 2.0), +(height)),
                 (+0.0, -(width / 2.0), +(height)),
                 (-(length / 2.0), -(width / 2.0), +(height)),
                 (-(length / 2.0), +0.0, +(height)),
                 (-(length / 2.0), +(width / 2.0), +(height)),
                 (+0.0, +(width / 2.0), +(height)),
                 ]

        faces = [(0, 1, 9, 8),
                 (1, 2, 10, 9),
                 (2, 3, 11, 10),
                 (3, 4, 12, 11),
                 (4, 5, 13, 12),
                 (5, 6, 14, 13),
                 (6, 7, 15, 14),
                 (7, 0, 8, 15),
                ]

        ext_mesh = bpy.data.meshes.new("ext_mesh")
        ext_obj = bpy.data.objects.new("Ext_Obj", ext_mesh)
        
        scene = bpy.context.scene
        scene.objects.link(ext_obj)

        bm_ext = bmesh.new()

        for v_co in verts:
            bm_ext.verts.new(v_co)

        bm_ext.verts.ensure_lookup_table()
        for f_idx in faces:
            bm_ext.faces.new([bm_ext.verts[i] for i in f_idx])

        bm_ext.to_mesh(ext_mesh)
        ext_mesh.update()

        # add the mesh as an object into the scene with this utility module
        mesh_ext = object_utils.object_data_add(context, ext_mesh, operator=self)
        
        #Now bevel it:
        bpy.ops.object.mode_set(mode='EDIT')
        bm_ext = bmesh.from_edit_mesh(context.object.data)
        
        bpy.ops.mesh.select_all(action='DESELECT')
        
        bpy.ops.mesh.select_mode(type='EDGE')
        bm_ext.verts.ensure_lookup_table()
        
        #+,+
        if lf_seg > 0:
            select_e_in_bounds((length / 2.0), (width / 2.0), (height / 2.0), 0.00125, 0.00125, height + 0.00125, bm_ext.edges)
            bpy.ops.mesh.bevel(offset_type=lf_bev, offset=lf_str, segments=lf_seg, profile=0.5, clamp_overlap=False, material=-1)
            bm_ext.verts.ensure_lookup_table()
            bpy.ops.mesh.select_all(action='DESELECT')
        
        #+,-
        if lr_seg > 0:
            select_e_in_bounds((length / 2.0), (-width / 2.0), (height / 2.0), 0.00125, 0.00125, height + 0.00125, bm_ext.edges)
            bpy.ops.mesh.bevel(offset_type=lr_bev, offset=lr_str, segments=lr_seg, profile=0.5, clamp_overlap=False, material=-1)
            bm_ext.verts.ensure_lookup_table()
            bpy.ops.mesh.select_all(action='DESELECT')
        
        #-,+
        if rf_seg > 0:
            select_e_in_bounds((-length / 2.0), (width / 2.0), (height / 2.0), 0.00125, 0.00125, height + 0.00125, bm_ext.edges)
            bpy.ops.mesh.bevel(offset_type=rf_bev, offset=rf_str, segments=rf_seg, profile=0.5, clamp_overlap=False, material=-1)
            bm_ext.verts.ensure_lookup_table()
            bpy.ops.mesh.select_all(action='DESELECT')
        
        #-,-
        if rr_seg > 0:
            select_e_in_bounds((-length / 2.0), (-width / 2.0), (height / 2.0), 0.00125, 0.00125, height + 0.00125, bm_ext.edges)
            bpy.ops.mesh.bevel(offset_type=rr_bev, offset=rr_str, segments=rr_seg, profile=0.5, clamp_overlap=False, material=-1)
            bm_ext.verts.ensure_lookup_table()
            bpy.ops.mesh.select_all(action='DESELECT')
        
        bmesh.ops.recalc_face_normals(bm_ext, faces=bm_ext.faces)
        
        bm_ext.verts.ensure_lookup_table()
        bmesh.update_edit_mesh(context.active_object.data)
        bpy.ops.object.mode_set(mode='OBJECT')
        
        #Generate the interior:
        height = fcd
        
        verts = [(+((length / 2.0) - w_thick), +((width / 2.0) - w_thick), +0.0),
                 (+((length / 2.0) - w_thick), +0.0, +0.0),
                 (+((length / 2.0) - w_thick), -((width / 2.0) - w_thick), +0.0),
                 (+0.0, -((width / 2.0) - w_thick), +0.0),
                 (-((length / 2.0) - w_thick), -((width / 2.0) - w_thick), +0.0),
                 (-((length / 2.0) - w_thick), +0.0, +0.0),
                 (-((length / 2.0) - w_thick), +((width / 2.0) - w_thick), +0.0),
                 (+0.0, +((width / 2.0) - w_thick), +0.0),
                 (+((length / 2.0) - w_thick), +((width / 2.0) - w_thick), +(height)),
                 (+((length / 2.0) - w_thick), +0.0, +(height)),
                 (+((length / 2.0) - w_thick), -((width / 2.0) - w_thick), +(height)),
                 (+0.0, -((width / 2.0) - w_thick), +(height)),
                 (-((length / 2.0) - w_thick), -((width / 2.0) - w_thick), +(height)),
                 (-((length / 2.0) - w_thick), +0.0, +(height)),
                 (-((length / 2.0) - w_thick), +((width / 2.0) - w_thick), +(height)),
                 (+0.0, +((width / 2.0) - w_thick), +(height)),
                 (+0.0, +0.0, +0.0),
                 (+0.0, +0.0, +(height)),
                 ]

        faces = [(0, 1, 9, 8),
                 (1, 2, 10, 9),
                 (2, 3, 11, 10),
                 (3, 4, 12, 11),
                 (4, 5, 13, 12),
                 (5, 6, 14, 13),
                 (6, 7, 15, 14),
                 (7, 0, 8, 15),
                 (0, 1, 16, 7),
                 (1, 2, 3, 16),
                 (3, 4, 5, 16),
                 (5, 6, 7, 16),
                 (8, 9, 17, 15),
                 (9, 10, 11, 17),
                 (11, 12, 13, 17),
                 (13, 14, 15, 17),
                ]

        int_mesh = bpy.data.meshes.new("int_mesh")
        int_obj = bpy.data.objects.new("Int_Obj", int_mesh)
        
        scene = bpy.context.scene
        scene.objects.link(int_obj)

        bm_int = bmesh.new()

        for v_co in verts:
            bm_int.verts.new(v_co)

        bm_int.verts.ensure_lookup_table()
        for f_idx in faces:
            bm_int.faces.new([bm_int.verts[i] for i in f_idx])

        bm_int.to_mesh(int_mesh)
        int_mesh.update()

        # add the mesh as an object into the scene with this utility module
        mesh_int = object_utils.object_data_add(context, int_mesh, operator=self)
        
        #Now bevel it:
        bpy.ops.object.mode_set(mode='EDIT')
        bm_int = bmesh.from_edit_mesh(context.object.data)
        
        bpy.ops.mesh.select_all(action='DESELECT')
        
        bpy.ops.mesh.select_mode(type='EDGE')
        bm_int.verts.ensure_lookup_table()
        
        #+,+
        if lf_seg > 0:
            select_e_in_bounds(((length / 2.0) - w_thick), ((width / 2.0) - w_thick), (height / 2.0), 0.00125, 0.00125, height + 0.00125, bm_int.edges)
            bpy.ops.mesh.bevel(offset_type=lf_bev, offset=lf_str, segments=lf_seg, profile=0.5, clamp_overlap=False, material=-1)
            bm_int.verts.ensure_lookup_table()
            bpy.ops.mesh.select_all(action='DESELECT')
        
        #+,-
        if lr_seg > 0:
            select_e_in_bounds(((length / 2.0) - w_thick), -((width / 2.0) - w_thick), (height / 2.0), 0.00125, 0.00125, height + 0.00125, bm_int.edges)
            bpy.ops.mesh.bevel(offset_type=lr_bev, offset=lr_str, segments=lr_seg, profile=0.5, clamp_overlap=False, material=-1)
            bm_int.verts.ensure_lookup_table()
            bpy.ops.mesh.select_all(action='DESELECT')
        
        #-,+
        if rf_seg > 0:
            select_e_in_bounds(-((length / 2.0) - w_thick), ((width / 2.0) - w_thick), (height / 2.0), 0.00125, 0.00125, height + 0.00125, bm_int.edges)
            bpy.ops.mesh.bevel(offset_type=rf_bev, offset=rf_str, segments=rf_seg, profile=0.5, clamp_overlap=False, material=-1)
            bm_int.verts.ensure_lookup_table()
            bpy.ops.mesh.select_all(action='DESELECT')
        
        #-,-
        if rr_seg > 0:
            select_e_in_bounds(-((length / 2.0) - w_thick), -((width / 2.0) - w_thick), (height / 2.0), 0.00125, 0.00125, height + 0.00125, bm_int.edges)
            bpy.ops.mesh.bevel(offset_type=rr_bev, offset=rr_str, segments=rr_seg, profile=0.5, clamp_overlap=False, material=-1)
            bm_int.verts.ensure_lookup_table()
            bpy.ops.mesh.select_all(action='DESELECT')
        
        #Recalculate normals to make them consistent inside
        bmesh.ops.recalc_face_normals(bm_int, faces=bm_int.faces)
        bmesh.ops.reverse_faces(bm_int, faces=bm_int.faces, flip_multires=True)
        
        #Duplicate the lower floor to make each floor above it
        if floors > 1:
            duplication_verts = bm_int.verts[:]
            duplication_edges = bm_int.edges[:]
            duplication_faces = bm_int.faces[:]
            f = 1
            
            #Duplicate the bottom floor and move it up f-number of floors
            while f < floors:
                bmesh.ops.duplicate(bm_int, geom=duplication_verts[:] + duplication_edges[:] + duplication_faces[:])
                bmesh.ops.translate(bm_int, vec=(0.0, 0.0, (height + f_thick)), verts=duplication_verts[:])
                f += 1
        
        bm_int.verts.ensure_lookup_table()
        bmesh.update_edit_mesh(context.active_object.data)
        bpy.ops.object.mode_set(mode='OBJECT')
        
        #Generate the roof:
        height = floors * (fcd + f_thick)
        
        if roof == 'NONE':
            verts = [(+0.0, +0.0, +(height)),
                     (+(length / 2.0), +(width / 2.0), +(height)),
                     (+(length / 2.0), +0.0, +(height)),
                     (+(length / 2.0), -(width / 2.0), +(height)),
                     (+0.0, -(width / 2.0), +(height)),
                     (-(length / 2.0), -(width / 2.0), +(height)),
                     (-(length / 2.0), +0.0, +(height)),
                     (-(length / 2.0), +(width / 2.0), +(height)),
                     (+0.0, +(width / 2.0), +(height)),
                    ]
            
            faces = [(0, 2, 1, 8),
                     (0, 4, 3, 2),
                     (0, 6, 5, 4),
                     (0, 8, 7, 6),
                    ]
            
        else:
            verts = [(+0.0, +0.0, +(height)),
                     (+((length / 2.0) - w_thick), +0.0, +(height)),
                     (+((length / 2.0) - w_thick), +0.0, +(height + r_thick)),
                     (+(length / 2.0), +0.0, +(height + r_thick)),
                     (+(length / 2.0), +0.0, +(height)),
                     (+(length / 2.0), +(width / 2.0), +(height)),
                     (+(length / 2.0), +(width / 2.0), +(height + r_thick)),
                     (+((length / 2.0) - w_thick), +((width / 2.0) - w_thick), +(height + r_thick)),
                     (+((length / 2.0) - w_thick), +((width / 2.0) - w_thick), +(height)),
                     (+0.0, +((width / 2.0) - w_thick), +(height)),
                     (+0.0, +((width / 2.0) - w_thick), +(height + r_thick)),
                     (+0.0, +(width / 2.0), +(height + r_thick)),
                     (+0.0, +(width / 2.0), +(height)),
                     (-(length / 2.0), +(width / 2.0), +(height)),
                     (-(length / 2.0), +(width / 2.0), +(height + r_thick)),
                     (-((length / 2.0) - w_thick), +((width / 2.0) - w_thick), +(height + r_thick)),
                     (-((length / 2.0) - w_thick), +((width / 2.0) - w_thick), +(height)),
                     (-((length / 2.0) - w_thick), +0.0, +(height)),
                     (-((length / 2.0) - w_thick), +0.0, +(height + r_thick)),
                     (-(length / 2.0), +0.0, +(height + r_thick)),
                     (-(length / 2.0), +0.0, +(height)),
                     (-(length / 2.0), -(width / 2.0), +(height)),
                     (-(length / 2.0), -(width / 2.0), +(height + r_thick)),
                     (-((length / 2.0) - w_thick), -((width / 2.0) - w_thick), +(height + r_thick)),
                     (-((length / 2.0) - w_thick), -((width / 2.0) - w_thick), +(height)),
                     (+0.0, -((width / 2.0) - w_thick), +(height)),
                     (+0.0, -((width / 2.0) - w_thick), +(height + r_thick)),
                     (+0.0, -(width / 2.0), +(height + r_thick)),
                     (+0.0, -(width / 2.0), +(height)),
                     (+(length / 2.0), -(width / 2.0), +(height)),
                     (+(length / 2.0), -(width / 2.0), +(height + r_thick)),
                     (+((length / 2.0) - w_thick), -((width / 2.0) - w_thick), +(height + r_thick)),
                     (+((length / 2.0) - w_thick), -((width / 2.0) - w_thick), +(height)),
                     ]

            faces = [(0, 1, 8, 9),
                     (1, 2, 7, 8),
                     (2, 3, 6, 7),
                     (3, 4, 5, 6),
                     (5, 12, 11, 6),
                     (11, 10, 7, 6),
                     (10, 9, 8, 7),
                     (0, 9, 16, 17),
                     (9, 10, 15, 16),
                     (10, 11, 14, 15),
                     (11, 12, 13, 14),
                     (13, 20, 19, 14),
                     (14, 19, 18, 15),
                     (18, 17, 16, 15),
                     (0, 17, 24, 25),
                     (17, 18, 23, 24),
                     (18, 19, 22, 23),
                     (19, 20, 21, 22),
                     (21, 28, 27, 22),
                     (27, 26, 23, 22),
                     (26, 25, 24, 23),
                     (0, 25, 32, 1),
                     (25, 26, 31, 32),
                     (26, 27, 30, 31),
                     (27, 28, 29, 30),
                     (30, 29, 4, 3),
                     (3, 2, 31, 30),
                     (2, 1, 32, 31),
                    ]

        roof_mesh = bpy.data.meshes.new("roof_mesh")
        roof_obj = bpy.data.objects.new("Roof_Obj", roof_mesh)
        
        scene = bpy.context.scene
        scene.objects.link(roof_obj)

        bm_roof = bmesh.new()

        for v_co in verts:
            bm_roof.verts.new(v_co)

        bm_roof.verts.ensure_lookup_table()
        for f_idx in faces:
            bm_roof.faces.new([bm_roof.verts[i] for i in f_idx])

        bm_roof.to_mesh(roof_mesh)
        roof_mesh.update()

        # add the mesh as an object into the scene with this utility module
        mesh_roof = object_utils.object_data_add(context, roof_mesh, operator=self)
        
        #Now bevel it:
        bpy.ops.object.mode_set(mode='EDIT')
        bm_roof = bmesh.from_edit_mesh(context.object.data)
        
        bpy.ops.mesh.select_all(action='DESELECT')
        
        bpy.ops.mesh.select_mode(type='EDGE')
        bm_roof.verts.ensure_lookup_table()
        
        #If roof == 'None', only a single vert for a corner can be beveled, not an edge
        if roof == 'NONE':
            vert_only = True
        else:
            vert_only = False
        
        #Adding 0.0125 to the bound-checks below helps ensure that
        #verts that would otherwise be at the edge of the bounds
        #are for sure included. I was having trouble with this
        #because floats tend to not be exactly what I set them
        #to, at certain times. It shouldn't catch any wrong verts,
        #as long as the user doesn't set lf_seg = something huge
        
        #+,+
        if lf_seg > 0:
            if roof == 'NONE':
                select_v_in_bounds(((length - w_thick) / 2.0), ((width - w_thick) / 2.0), (height + (r_thick / 2.0)), (w_thick + 0.00125), (w_thick + 0.00125), (r_thick + 0.00125), bm_roof.verts)
            else:
                select_e_in_bounds(((length - w_thick) / 2.0), ((width - w_thick) / 2.0), (height + (r_thick / 2.0)), (w_thick + 0.00125), (w_thick + 0.00125), (r_thick + 0.00125), bm_roof.edges)
            bpy.ops.mesh.bevel(offset_type=lf_bev, offset=lf_str, segments=lf_seg, profile=0.5, clamp_overlap=False, vertex_only=vert_only, loop_slide=False, material=-1)
            bm_roof.verts.ensure_lookup_table()
            bpy.ops.mesh.select_all(action='DESELECT')
        
         #+,-
        if lr_seg > 0:
            if roof == 'NONE':
                select_v_in_bounds(((length - w_thick) / 2.0), ((width - w_thick) / -2.0), (height + (r_thick / 2.0)), (w_thick + 0.00125), (w_thick + 0.00125), (r_thick + 0.00125), bm_roof.verts)
            else:
                select_e_in_bounds(((length - w_thick) / 2.0), ((width - w_thick) / -2.0), (height + (r_thick / 2.0)), (w_thick + 0.00125), (w_thick + 0.00125), (r_thick + 0.00125), bm_roof.edges)
            bpy.ops.mesh.bevel(offset_type=lr_bev, offset=lr_str, segments=lr_seg, profile=0.5, clamp_overlap=False, vertex_only=vert_only, loop_slide=False, material=-1)
            bm_roof.verts.ensure_lookup_table()
            bpy.ops.mesh.select_all(action='DESELECT')
        
        #-,+
        if rf_seg > 0:
            if roof == 'NONE':
                select_v_in_bounds(((length - w_thick) / -2.0), ((width - w_thick) / 2.0), (height + (r_thick / 2.0)), (w_thick + 0.00125), (w_thick + 0.00125), (r_thick + 0.00125), bm_roof.verts)
            else:
                select_e_in_bounds(((length - w_thick) / -2.0), ((width - w_thick) / 2.0), (height + (r_thick / 2.0)), (w_thick + 0.00125), (w_thick + 0.00125), (r_thick + 0.00125), bm_roof.edges)
            bpy.ops.mesh.bevel(offset_type=rf_bev, offset=rf_str, segments=rf_seg, profile=0.5, clamp_overlap=False, vertex_only=vert_only, loop_slide=False, material=-1)
            bm_roof.verts.ensure_lookup_table()
            bpy.ops.mesh.select_all(action='DESELECT')
        
        #-,-
        if rr_seg > 0:
            if roof == 'NONE':
                select_v_in_bounds(((length - w_thick) / -2.0), ((width - w_thick) / -2.0), (height + (r_thick / 2.0)), (w_thick + 0.00125), (w_thick + 0.00125), (r_thick + 0.00125), bm_roof.verts)
            else:
                select_e_in_bounds(((length - w_thick) / -2.0), ((width - w_thick) / -2.0), (height + (r_thick / 2.0)), (w_thick + 0.00125), (w_thick + 0.00125), (r_thick + 0.00125), bm_roof.edges)
            bpy.ops.mesh.bevel(offset_type=rr_bev, offset=rr_str, segments=rr_seg, profile=0.5, clamp_overlap=False, vertex_only=vert_only, loop_slide=False, material=-1)
            bm_roof.verts.ensure_lookup_table()
            bpy.ops.mesh.select_all(action='DESELECT')
        
        bmesh.ops.recalc_face_normals(bm_roof, faces=bm_roof.faces)
        bm_roof.verts.ensure_lookup_table()
        
        bmesh.update_edit_mesh(context.active_object.data)
        bpy.ops.object.mode_set(mode='OBJECT')
        
        #Don't need these, I'll get rid of them:
        bpy.ops.object.select_all(action='DESELECT')
        mesh_ext.select = True
        mesh_int.select = True
        mesh_roof.select = True
        bpy.ops.object.delete()
        
        #Join all 3 parts of the building, into a singular mesh called "Structure"
        bpy.ops.object.select_all(action='DESELECT')
        ext_obj.select = True
        int_obj.select = True
        roof_obj.select = True
        bpy.context.scene.objects.active = ext_obj
        bpy.ops.object.join()   
        ext_obj.name = "Structure"
        
        ext_obj.location = (self.location[0], self.location[1], self.location[2])
        ext_obj.rotation_euler = (self.rotation[0], self.rotation[1], self.rotation[2])
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        
        #TODO: make_UV_map()
        #TODO: generate_textures()
        #TODO: make_material()

        return {'FINISHED'}


def menu_func(self, context):
    self.layout.operator(AddStructure.bl_idname, icon='MOD_BUILD')


def register():
    bpy.utils.register_class(AddStructure)
    bpy.types.INFO_MT_mesh_add.append(menu_func)


def unregister():
    bpy.utils.unregister_class(AddStructure)
    bpy.types.INFO_MT_mesh_add.remove(menu_func)

if __name__ == "__main__":
    register()
