bl_info = {
    "name": "Add Slide",
    "description": "Generates 1 of 4 different kinds of slides",
    "author": "Austin Jacob",
    "version": (4, 0, 0),
    "blender": (2, 79, 0),
    "location": "View3D > Add > Mesh",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Add Mesh"}

# License for this script is GNU GPL Version 3
# The text for this license can be found here:
# https://www.gnu.org/licenses/gpl-3.0.en.html

import bpy
import bmesh
import mathutils
import math

#Return the coordinates of the
#vert with the furthest y-val.
def get_furthest_y(verts):
    max_vert = verts[0]
    for v in verts:
        if v.co.y <= max_vert.co.y:
            max_vert = v
    return max_vert.co

#Calculates the central z-point of the geometry
#and then returns all the verts at or under it.
def all_beneath_center(geom):
    #List of all verts at or below center
    sel_verts = []
    
    #All of these verts will be checked:
    verts_list = []
    
    #Sum of all z values in geom:
    z_center = 0.0
    
    #The number of verts in geom:
    v_num = 0
    
    for ele in geom:
        #If it's a vert, add it to the sums:
        if isinstance(ele, bmesh.types.BMVert):
            verts_list += [ele]
            z_center += ele.co.z
            v_num += 1
    #Now get the average by dividing by v_num:
    z_center /= v_num
    #Now use our center z-point to
    #find all verts at or under z:
    for v in verts_list:
        if v.co.z <= z_center:
            sel_verts += [v]
            
    return sel_verts

#Generate a slide in the
#shape of a coiled tube.
def make_tube_helix(maj_rad, min_rad, rad_seg, loop_h, loop_seg, loops, thick, ent, ending):
    
    #Make the object:
    mesh1 = bpy.data.meshes.new("slide")
    slide_obj = bpy.data.objects.new("Slide_Obj", mesh1)

    scene = bpy.context.scene
    scene.objects.link(slide_obj)
    
    bm = bmesh.new()
    #How much to rotate each new circle:
    rot = -360.0 / loop_seg
    #How much to move each new cirlce:
    mov = -loop_h / loop_seg
    
    #Make the first piece of the loop:
    bmesh.ops.create_circle(
        bm,
        cap_ends=False,
        diameter=min_rad,
        segments=rad_seg)
    
    #Properly orient the circle:
    bmesh.ops.rotate(bm, 
            verts=bm.verts,
            cent=(0.0, 0.0, 0.0),
            matrix=mathutils.Matrix.Rotation(math.radians(90.0), 3, 'X'))
    
    #Extrude the entrance:
    new_mesh = bmesh.ops.extrude_edge_only(bm, edges=bm.edges)
    extr_geom = new_mesh["geom"]
    del new_mesh
    
    #Holds data on the edges to extrude:
    extr_verts = [v for v in extr_geom if isinstance(v, bmesh.types.BMVert)]
    extr_edges = [e for e in extr_geom if isinstance(e, bmesh.types.BMEdge)]
    
    #Move the entrance forward:
    bmesh.ops.translate(
            bm,
            verts=extr_verts,
            vec=(0.0, -ent, 0.0))
    
    #Move it by maj_rad amount:
    bmesh.ops.translate(
        bm,
        verts=bm.verts,
        vec=(maj_rad, 0.0, 0.0))
    
    #Make a loop that extrudes,
    #rotates the extruded mesh,
    #and raises the new circle:
    iterations = loop_seg * loops
    
    for i in range(0, iterations):
        #Extrude the circle and
        #store that new data so
        #it can be transformed:
        new_mesh = bmesh.ops.extrude_edge_only(bm, edges=extr_edges)
        extr_geom = new_mesh["geom"]
        del new_mesh
        
        extr_verts = [v for v in extr_geom if isinstance(v, bmesh.types.BMVert)]
        extr_edges = [e for e in extr_geom if isinstance(e, bmesh.types.BMEdge)]
        
        #Rotate that new data around
        #the center and move it down
        bmesh.ops.rotate(bm, 
            verts=extr_verts,
            cent=(0.0, -ent, 0.0),
            matrix=mathutils.Matrix.Rotation(math.radians(rot), 3, 'Z'))
        
        bmesh.ops.translate(
            bm,
            verts=extr_verts,
            vec=(0.0, 0.0, mov))
    
    #Now extrude the ending:
    new_mesh = bmesh.ops.extrude_edge_only(bm, edges=extr_edges)
    extr_geom = new_mesh["geom"]
    del new_mesh
    
    extr_verts = [v for v in extr_geom if isinstance(v, bmesh.types.BMVert)]
    extr_edges = [e for e in extr_geom if isinstance(e, bmesh.types.BMEdge)]
    
    #The amount to move the
    #2 halves of the ending
    seg_mov = -ending / 2.0
    
    #Since slides typically have
    #a curved opening, only move
    #forward by 1/2, and extrude
    bmesh.ops.translate(
            bm,
            verts=extr_verts,
            vec=(0.0, seg_mov, 0.0))
    
    #Now make the curved sides:
    
    #For the slope, only the bottom half
    #of the vertices have to be selected
    extr_verts = all_beneath_center(extr_geom)
    
    #Now move the segment:
    bmesh.ops.translate(
            bm,
            verts=extr_verts,
            vec=(0.0, seg_mov, 0.0))
    
    #Smooth the geometry:
    for f in bm.faces:
        f.smooth = True
    
    #Now update the mesh object:
    bm.to_mesh(mesh1)
    mesh1.update()
    
    #Return slide_obj so it can have 
    #modifiers applied in execute():
    return slide_obj

#Make a straight tube slide. 
def make_tube_straight(min_rad, height, length, rad_seg, t_seg, thick, ent, ending):
    
    #Make the object:
    mesh1 = bpy.data.meshes.new("slide")
    slide_obj = bpy.data.objects.new("Slide_Obj", mesh1)

    scene = bpy.context.scene
    scene.objects.link(slide_obj)
    
    bm = bmesh.new()
    
    #Make the first piece of the loop:
    bmesh.ops.create_circle(
        bm,
        cap_ends=False,
        diameter=min_rad,
        segments=rad_seg)
    
    #Properly orient the circle:
    bmesh.ops.rotate(bm, 
            verts=bm.verts,
            cent=(0.0, 0.0, 0.0),
            matrix=mathutils.Matrix.Rotation(math.radians(90.0), 3, 'X'))
    
    #Extrude the entrance:
    new_mesh = bmesh.ops.extrude_edge_only(bm, edges=bm.edges)
    extr_geom = new_mesh["geom"]
    del new_mesh
    
    #Holds data on the edges to extrude:
    extr_verts = [v for v in extr_geom if isinstance(v, bmesh.types.BMVert)]
    extr_edges = [e for e in extr_geom if isinstance(e, bmesh.types.BMEdge)]
    
    #Move the entrance forward:
    bmesh.ops.translate(
            bm,
            verts=extr_verts,
            vec=(0.0, -ent, 0.0))
    
    #To not skew the shape
    #add a segment between
    #the entrance and main
    #section of the slide:
    
    #The angle to rotate that section:
    rot = (45 / -(length / height)) / t_seg
    
    #Extrude and rotate for every t_seg
    for i in range(0, t_seg):
        
        #Now extrude it:
        new_mesh = bmesh.ops.extrude_edge_only(bm, edges=extr_edges)
        extr_geom = new_mesh["geom"]
        del new_mesh
        
        #Holds data on the edges to extrude:
        extr_verts = [v for v in extr_geom if isinstance(v, bmesh.types.BMVert)]
        extr_edges = [e for e in extr_geom if isinstance(e, bmesh.types.BMEdge)]
        
        #Rotate it by "rot":
        bmesh.ops.rotate(bm, 
            verts=extr_verts,
            cent=(0.0, -ent, -min_rad),
            matrix=mathutils.Matrix.Rotation(math.radians(-rot), 3, 'X'))
    
    #Extrude the main section now:
    new_mesh = bmesh.ops.extrude_edge_only(bm, edges=extr_edges)
    extr_geom = new_mesh["geom"]
    del new_mesh
    
    #Holds data on the edges to extrude:
    extr_verts = [v for v in extr_geom if isinstance(v, bmesh.types.BMVert)]
    extr_edges = [e for e in extr_geom if isinstance(e, bmesh.types.BMEdge)]
    
    #Move it down by the height and length
    bmesh.ops.translate(
            bm,
            verts=extr_verts,
            vec=(0.0, -length, -height))
    
    #The location needed to rotate
    #is the vert with the furthest 
    #y-value so return that vertex
    rot_loc = get_furthest_y(extr_verts)
    
    #Make another rotated extrusion that
    #corrects the difference between the
    #main section and the ending section
    
    #Repeat the extrusion/rotation for all t_seg
    for i in range(0, t_seg):
        new_mesh = bmesh.ops.extrude_edge_only(bm, edges=extr_edges)
        extr_geom = new_mesh["geom"]
        del new_mesh
        
        #Holds data on the edges to extrude:
        extr_verts = [v for v in extr_geom if isinstance(v, bmesh.types.BMVert)]
        extr_edges = [e for e in extr_geom if isinstance(e, bmesh.types.BMEdge)]
        
        #Rotate it by "rot":
        bmesh.ops.rotate(bm, 
            verts=extr_verts,
            cent=rot_loc,
            matrix=mathutils.Matrix.Rotation(math.radians(rot), 3, 'X'))
    
    #Now extrude the ending:
    new_mesh = bmesh.ops.extrude_edge_only(bm, edges=extr_edges)
    extr_geom = new_mesh["geom"]
    del new_mesh
    
    extr_verts = [v for v in extr_geom if isinstance(v, bmesh.types.BMVert)]
    extr_edges = [e for e in extr_geom if isinstance(e, bmesh.types.BMEdge)]
    
    #The amount to move the
    #2 halves of the ending
    seg_mov = -ending / 2.0
    
    #Since slides typically have
    #a curved opening, only move
    #forward by 1/2, and extrude
    bmesh.ops.translate(
            bm,
            verts=extr_verts,
            vec=(0.0, seg_mov, 0.0))
    
    #Now make the curved sides:
    
    #For the slope, only the bottom half
    #of the vertices have to be selected
    extr_verts = all_beneath_center(extr_geom)
    
    #Now move the segment:
    bmesh.ops.translate(
            bm,
            verts=extr_verts,
            vec=(0.0, seg_mov, 0.0))
    
    #Smooth the geometry:
    for f in bm.faces:
        f.smooth = True
    
    #Update it, and it's done!
    bm.to_mesh(mesh1)
    mesh1.update()
    
    #Return slide_obj so it can have 
    #modifiers applied in execute():
    return slide_obj
    

#Make a coiled, open slide.
def make_open_helix(maj_rad, width, g_height, loop_h, loop_seg, loops, thick, ent, ending):
    #It works pretty much the same
    #as the tube helix slide, only 
    #instead of a circle, the mesh
    #is made using just four verts
    
    #Make the object:
    mesh1 = bpy.data.meshes.new("slide")
    slide_obj = bpy.data.objects.new("Slide_Obj", mesh1)

    scene = bpy.context.scene
    scene.objects.link(slide_obj)
    
    bm = bmesh.new()
    #How much to rotate each new circle:
    rot = -360.0 / loop_seg
    #How much to move each new cirlce:
    mov = -loop_h / loop_seg
    
    #Make the first piece of the segment:
    verts = [(-width / 2.0, 0.0, g_height),
             (-width / 2.0, 0.0, 0.0),
             (width / 2.0, 0.0, 0.0),
             (width / 2.0, 0.0, g_height),
            ]
    
    edges = [(0, 1), (1, 2), (2, 3)]
    
    for v in verts:
            bm.verts.new(v)

    bm.verts.ensure_lookup_table()
    for e in edges:
        bm.edges.new([bm.verts[v] for v in e])
    
    #Extrude the entrance:
    new_mesh = bmesh.ops.extrude_edge_only(bm, edges=bm.edges)
    extr_geom = new_mesh["geom"]
    del new_mesh
    
    #Holds data on the edges to extrude:
    extr_verts = [v for v in extr_geom if isinstance(v, bmesh.types.BMVert)]
    extr_edges = [e for e in extr_geom if isinstance(e, bmesh.types.BMEdge)]
    
    #Move the entrance forward:
    bmesh.ops.translate(
            bm,
            verts=extr_verts,
            vec=(0.0, -ent, 0.0))
    
    #Move it by maj_rad amount:
    bmesh.ops.translate(
        bm,
        verts=bm.verts,
        vec=(maj_rad, 0.0, 0.0))
    
    #Make a loop that extrudes,
    #rotates the extruded mesh,
    #and raises the new circle:
    iterations = loop_seg * loops
    
    for i in range(0, iterations):
        #Extrude the circle and
        #store that new data so
        #it can be transformed:
        new_mesh = bmesh.ops.extrude_edge_only(bm, edges=extr_edges)
        extr_geom = new_mesh["geom"]
        del new_mesh
        
        extr_verts = [v for v in extr_geom if isinstance(v, bmesh.types.BMVert)]
        extr_edges = [e for e in extr_geom if isinstance(e, bmesh.types.BMEdge)]
        
        #Rotate that new data around
        #the center and move it down
        bmesh.ops.rotate(bm, 
            verts=extr_verts,
            cent=(0.0, -ent, 0.0),
            matrix=mathutils.Matrix.Rotation(math.radians(rot), 3, 'Z'))
        
        bmesh.ops.translate(
            bm,
            verts=extr_verts,
            vec=(0.0, 0.0, mov))
    
    #Now extrude the ending:
    new_mesh = bmesh.ops.extrude_edge_only(bm, edges=extr_edges)
    extr_geom = new_mesh["geom"]
    del new_mesh
    
    extr_verts = [v for v in extr_geom if isinstance(v, bmesh.types.BMVert)]
    extr_edges = [e for e in extr_geom if isinstance(e, bmesh.types.BMEdge)]
    
    bmesh.ops.translate(
            bm,
            verts=extr_verts,
            vec=(0.0, -ending, 0.0))
    
    #Smooth the geometry:
    for f in bm.faces:
        f.smooth = True
    
    #Now update the mesh object:
    bm.to_mesh(mesh1)
    mesh1.update()
    
    #Return slide_obj so it can have 
    #modifiers applied in execute():
    return slide_obj


#Make a straight, open slide.
def make_open_straight(width, g_height, height, length, t_seg, thick, ent, ending):
    #It works the same way
    #as the straight tube,
    #but without a circle.
    
    #Make the object:
    mesh1 = bpy.data.meshes.new("slide")
    slide_obj = bpy.data.objects.new("Slide_Obj", mesh1)

    scene = bpy.context.scene
    scene.objects.link(slide_obj)
    
    bm = bmesh.new()
    
    #Make the first piece of the segment:
    verts = [(-width / 2.0, 0.0, g_height),
             (-width / 2.0, 0.0, 0.0),
             (width / 2.0, 0.0, 0.0),
             (width / 2.0, 0.0, g_height),
            ]
    
    edges = [(0, 1), (1, 2), (2, 3)]
    
    for v in verts:
            bm.verts.new(v)

    bm.verts.ensure_lookup_table()
    for e in edges:
        bm.edges.new([bm.verts[v] for v in e])
    
    #Extrude the entrance:
    new_mesh = bmesh.ops.extrude_edge_only(bm, edges=bm.edges)
    extr_geom = new_mesh["geom"]
    del new_mesh
    
    #Holds data on the edges to extrude:
    extr_verts = [v for v in extr_geom if isinstance(v, bmesh.types.BMVert)]
    extr_edges = [e for e in extr_geom if isinstance(e, bmesh.types.BMEdge)]
    
    #Move the entrance forward:
    bmesh.ops.translate(
            bm,
            verts=extr_verts,
            vec=(0.0, -ent, 0.0))
    
    #To not skew the shape
    #add a segment between
    #the entrance and main
    #section of the slide:
    
    #The angle to rotate that section:
    rot = (45 / -(length / height)) / t_seg
    
    #Extrude and rotate for every t_seg
    for i in range(0, t_seg):
        
        #Now extrude it:
        new_mesh = bmesh.ops.extrude_edge_only(bm, edges=extr_edges)
        extr_geom = new_mesh["geom"]
        del new_mesh
        
        #Holds data on the edges to extrude:
        extr_verts = [v for v in extr_geom if isinstance(v, bmesh.types.BMVert)]
        extr_edges = [e for e in extr_geom if isinstance(e, bmesh.types.BMEdge)]
        
        #Unlike the other type that rotates 
        #around -min_rad, this type rotates 
        #on the z-axis by 0.0, and later by 
        #g_height amount at the ending part
        
        #Rotate it by "rot":
        bmesh.ops.rotate(bm, 
            verts=extr_verts,
            cent=(0.0, -ent, 0.0),
            matrix=mathutils.Matrix.Rotation(math.radians(-rot), 3, 'X'))
    
    #Extrude the main section now:
    new_mesh = bmesh.ops.extrude_edge_only(bm, edges=extr_edges)
    extr_geom = new_mesh["geom"]
    del new_mesh
    
    #Holds data on the edges to extrude:
    extr_verts = [v for v in extr_geom if isinstance(v, bmesh.types.BMVert)]
    extr_edges = [e for e in extr_geom if isinstance(e, bmesh.types.BMEdge)]
    
    #Move it down by the height and length
    bmesh.ops.translate(
            bm,
            verts=extr_verts,
            vec=(0.0, -length, -height))
    
    #The location needed to rotate
    #is the vert with the furthest 
    #y-value so return that vertex
    rot_loc = get_furthest_y(extr_verts)[1]
    
    #Make another rotated extrusion that
    #corrects the difference between the
    #main section and the ending section
    
    #Repeat the extrusion/rotation for all t_seg
    for i in range(0, t_seg):
        new_mesh = bmesh.ops.extrude_edge_only(bm, edges=extr_edges)
        extr_geom = new_mesh["geom"]
        del new_mesh
        
        #Holds data on the edges to extrude:
        extr_verts = [v for v in extr_geom if isinstance(v, bmesh.types.BMVert)]
        extr_edges = [e for e in extr_geom if isinstance(e, bmesh.types.BMEdge)]
        
        #Rotate it by "rot":
        bmesh.ops.rotate(bm, 
            verts=extr_verts,
            cent=(0.0, rot_loc, -height + g_height),
            matrix=mathutils.Matrix.Rotation(math.radians(rot), 3, 'X'))
    
    #Now extrude the ending:
    new_mesh = bmesh.ops.extrude_edge_only(bm, edges=extr_edges)
    extr_geom = new_mesh["geom"]
    del new_mesh
    
    extr_verts = [v for v in extr_geom if isinstance(v, bmesh.types.BMVert)]
    extr_edges = [e for e in extr_geom if isinstance(e, bmesh.types.BMEdge)]
    
    bmesh.ops.translate(
            bm,
            verts=extr_verts,
            vec=(0.0, -ending, 0.0))
    
    #Smooth the geometry:
    for f in bm.faces:
        f.smooth = True
    
    #Update it, and it's done!
    bm.to_mesh(mesh1)
    mesh1.update()
    
    #Return slide_obj so it can have 
    #modifiers applied in execute():
    return slide_obj
                                 

from bpy.props import (
        BoolProperty,
        BoolVectorProperty,
        FloatProperty,
        FloatVectorProperty,
        IntProperty,
        EnumProperty,
        )


class AddSlide(bpy.types.Operator):
    """Add any of 4 types of a simple slide"""
    bl_idname = "mesh.slide_add"
    bl_label = "Add Slide"
    bl_options = {'REGISTER', 'UNDO'}
    
    type = EnumProperty(
            name="Type",
            description="What type of slide to make",
            items=(('TH', 'Tube-helix', 'Tube slide that curls around as it goes down'),
                   ('TS', 'Tube-straight', 'Tube slide that goes down in one direction'),
                   ('OH', 'Open-helix', 'Open slide that curls around as it goes down'),
                   ('OS', 'Open-straight', 'Open slide that goes down in one direction')),
            default='TH',
            )
    #For tube slides:
    maj_rad = FloatProperty(
            name="Major Radius",
            description="The radius of the whole slide",
            min=0.01,
            default=1.25,
            )
    min_rad = FloatProperty(
            name="Minor Radius",
            description="The radius of the tube of the slide",
            min=0.01,
            default=1.0,
            )
    rad_seg = IntProperty(
            name="Radius Segments",
            description="How many segments make up the circle of the tube",
            min=4,
            default=32,
            )
    #For helix slides:
    loop_h = FloatProperty(
            name="Loop Height",
            description="The change in height every 360 degrees",
            min=0.01,
            default=2.25,
            )
    loop_seg = IntProperty(
            name="Loop Segments",
            description="How many segments make up every 360 degree loop",
            min=4,
            default=32,
            )
    loops = IntProperty(
            name="Loops",
            description="How many loops make up the slide",
            min=1,
            default=3,
            )
    #For open slides:
    guard_height = FloatProperty(
            name="Guard Height",
            description="How high the left and right sides of the slide come up",
            min=0.01,
            default=0.325,
            )
    width = FloatProperty(
            name="Width",
            description="How wide the slide is",
            min=0.01,
            default=0.75,
            )
    tran_seg = IntProperty(
            name="Transition Segments",
            description="How many segments make up the transition from the main slide to the angled entrance or ending",
            min=1,
            default=3,
            )
    #For simple slides:
    height = FloatProperty(
            name="Height",
            description="The height of the slide",
            min=0.01,
            default=2.0,
            )
    length = FloatProperty(
            name="Length",
            description="The length of the slide",
            min=0.01,
            default=4.0,
            )
    #For all slides:
    thick = FloatProperty(
            name="Thickness",
            description="The thickness of the slide",
            min=0.01,
            default=0.0325,
            )
    entrance = FloatProperty(
            name="Entrance",
            description="The length of the entrance of the slide",
            min=0.01,
            default=0.5,
            )
    ending = FloatProperty(
            name="Ending",
            description="The length of the ending of the slide",
            min=0.01,
            default=0.75,
            )
    
    #Other stuff:
    layers = BoolVectorProperty(
            name="Layers",
            description="Object Layers",
            size=20,
            options={'HIDDEN', 'SKIP_SAVE'},
            )

    #Generic transform props:
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
        #The menu will change, 
        #depending on the type 
        #of slide user selects
        layout = self.layout
        
        if self.type == 'TH':
            display_name = "Tube-Helix"
            display_icon = "FORCE_MAGNETIC"
        elif self.type == 'OH':
            display_name = "Open-Helix"
            display_icon = "FORCE_MAGNETIC"
        elif self.type == 'OS':
            display_name = "Open-Straight"
            display_icon = "IPO_SINE"
        else:
            display_name = "Tube-Straight"
            display_icon = "IPO_SINE"
        
        #Display the type selector:
        box = layout.box()
        col = box.column()
        col.label(text=display_name, icon=display_icon)
        col.prop(self, "type")
        
        #Depending on type's value,
        #display the properties for
        #that particular slide type
        box = layout.box()
        col = box.column()
        
        if self.type == 'TH':
            col.prop(self, "maj_rad")
            col.prop(self, "min_rad")
            col.prop(self, "rad_seg")
            col.prop(self, "loop_h")
            col.prop(self, "loop_seg")
            col.prop(self, "loops")
            col.prop(self, "thick")
            col.prop(self, "entrance")
            col.prop(self, "ending")
            
        elif self.type == 'TS':
            col.prop(self, "min_rad")
            col.prop(self, "height")
            col.prop(self, "length")
            col.prop(self, "rad_seg")
            col.prop(self, "tran_seg")
            col.prop(self, "thick")
            col.prop(self, "entrance")
            col.prop(self, "ending")
        
        elif self.type == 'OH':
            col.prop(self, "maj_rad")
            col.prop(self, "width")
            col.prop(self, "g_height")
            col.prop(self, "loop_h")
            col.prop(self, "loop_seg")
            col.prop(self, "loops")
            col.prop(self, "thick")
            col.prop(self, "entrance")
            col.prop(self, "ending")
        
        else:
            col.prop(self, "width")
            col.prop(self, "g_height")
            col.prop(self, "height")
            col.prop(self, "length")
            col.prop(self, "t_seg")
            col.prop(self, "thick")
            col.prop(self, "entrance")
            col.prop(self, "ending")
        
    def execute(self, context):
        
        #Renaming the variables
        #to be a little simpler
        type = self.type
        maj_rad = self.maj_rad
        min_rad = self.min_rad
        rad_seg = self.rad_seg
        loop_h = self.loop_h
        loop_seg = self.loop_seg
        loops = self.loops
        g_height = self.guard_height
        width = self.width
        height = self.height
        length = self.length
        t_seg = self.tran_seg
        thick = self.thick
        ent = self.entrance
        ending = self.ending
        
        #Make the slide based off
        #the selected slide type:
        if type == 'TH':
            slide_obj = make_tube_helix(maj_rad,
                                        min_rad,
                                        rad_seg,
                                        loop_h,
                                        loop_seg,
                                        loops,
                                        thick,
                                        ent,
                                        ending)
            
        elif type == 'TS':
            slide_obj = make_tube_straight(min_rad,
                                           height,
                                           length,
                                           rad_seg,
                                           t_seg,
                                           thick,
                                           ent,
                                           ending)
            
        elif type == 'OH':
            slide_obj = make_open_helix(maj_rad,
                                        width,
                                        g_height,
                                        loop_h,
                                        loop_seg,
                                        loops,
                                        thick,
                                        ent,
                                        ending)
            
        #If none of the others
        #it must be type 'OS':
        else:
            slide_obj = make_open_straight(width,
                                           g_height,
                                           height,
                                           length,
                                           t_seg,
                                           thick,
                                           ent,
                                           ending)
        
        #Apply the thickness modifier:
        bpy.context.scene.objects.active = slide_obj
        sol_mod = slide_obj.modifiers.new("Solidify", 'SOLIDIFY')
        sol_mod.thickness = thick
        
        bpy.ops.object.modifier_apply(modifier=sol_mod.name)
        

        return {'FINISHED'}


def menu_func(self, context):
    self.layout.operator(AddSlide.bl_idname, icon='FORCE_MAGNETIC')


def register():
    bpy.utils.register_class(AddSlide)
    bpy.types.INFO_MT_mesh_add.append(menu_func)


def unregister():
    bpy.utils.unregister_class(AddSlide)
    bpy.types.INFO_MT_mesh_add.remove(menu_func)

if __name__ == "__main__":
    register()