bl_info = {
    "name": "Add Table",
    "description": "Generates a table.",
    "author": "Austin Jacob",
    "version": (1, 0, 0),
    "blender": (2, 79, 0),
    "location": "View3D > Add > Mesh",
    "warning": "", # used for warning icon and text in addons panel
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

from bpy.props import (
        BoolProperty,
        BoolVectorProperty,
        FloatProperty,
        FloatVectorProperty,
        IntProperty,
        )

#Takes a vert, and adds a table leg
#to the bmesh at vert's coordinates
#and finally, it returns the bmesh:
def add_table_leg(bm, v, ln, lt, ts, h, t, r):
    #bm is the bmesh, v is the vert, 
    #ln is the number of legs, lt is
    #leg thickness, while r contains
    #the rotation to use on each leg
    
    #Location of the new leg
    loc = mathutils.Matrix.Translation(v.co)
    
    #Bmesh that holds the new leg data
    bm_leg = bmesh.new()
    
    #If ts is 4, make the leg a cube
    if ts == 4:
        bmesh.ops.create_cube(bm_leg, size=1.0)
    else:
        #Otherwise, it can be made a cylinder:
        bmesh.ops.create_cone(bm_leg, 
                              cap_ends=True, 
                              cap_tris=False, 
                              segments=ts, 
                              diameter1=0.5, 
                              diameter2=0.5,
                              depth=1.0)
    
    #Resize the table leg:
    bmesh.ops.scale(bm_leg, vec=(lt, lt, (h - t)), verts=bm_leg.verts)
    
    bmesh.ops.translate(bm_leg, vec=v.co, verts=bm_leg.verts)
    
    #Dump the new leg into bm:
    for v in bm_leg.verts:
        bm.verts.new(v.co)
    
    bm.verts.index_update()
    bm.verts.ensure_lookup_table()
    
    #With the newest verts now in bm,
    #create the new faces using them:
    for f in bm_leg.faces:
        vert_list = []
        for v in f.verts:
            vert_list += [v.index + len(bm.verts) - len(bm_leg.verts)]
        bm.faces.new(bm.verts[i] for i in vert_list)
    
    bm.faces.index_update()
    bm_leg.free()
    
    return bm
    
class AddTable(bpy.types.Operator):
    """Add a simple table mesh"""
    bl_idname = "mesh.table_add"
    bl_label = "Add Table"
    bl_options = {'REGISTER', 'UNDO'}

    length = FloatProperty(
            name="Length",
            description="Table's length (x-axis)",
            min=1.0,
            default=1.0,
            )
    width = FloatProperty(
            name="Width",
            description="Table's width (y-axis)",
            min=1.0,
            default=1.0,
            )
    height = FloatProperty(
            name="Height",
            description="Table top's height off the ground",
            min=0.01,
            default=1.0,
            )
    thick = FloatProperty(
            name="Table Thickness",
            description="Thickness of the table top",
            min=0.01,
            default=0.025,
            )
    table_seg = IntProperty(
            name="Table Top Segments",
            description="Number of segments that make the table top",
            min=4,
            default=4,
            )
    leg_thick = FloatProperty(
            name="Table Leg Thickness",
            description="Thickness of the table legs",
            min=0.01,
            default=0.075,
            )
    legs = IntProperty(
            name="Table Legs",
            description="Number of table legs holding up the table",
            min=0,
            default=4,
            )
    leg_seg = IntProperty(
            name="Leg Segments",
            description="Number of segments that make up a table leg",
            min=3,
            default=4,
            )
    leg_offset = FloatProperty(
            name="Table Leg Offset",
            description="Offset of each leg from the table's center",
            min=0.0,
            default=0.75,
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
        col.label(text="Table Top", icon="MESH_PLANE")
        col.prop(self, "length")
        col.prop(self, "width")
        col.prop(self, "height")
        col.prop(self, "thick")
        col.prop(self, "table_seg")
        
        box = layout.box()
        col = box.column()
        col.label(text="Table Legs", icon="PAUSE")
        col.prop(self, "legs")
        col.prop(self, "leg_seg")
        col.prop(self, "leg_thick")
        col.prop(self, "leg_offset")
        
        box = layout.box()
        col = box.column()
        col.label(text="Placement", icon="NDOF_TURN")
        col.prop(self, "location")
        col.prop(self, "rotation")
    
    def execute(self, context):

        #Rename the variables
        #to something simpler
        l = self.length
        w = self.width
        h = self.height
        ts = self.table_seg
        t = self.thick
        legs = self.legs
        lt = self.leg_thick
        ls = self.leg_seg
        lo = self.leg_offset / 2.0
        
        #Create the tabletop object:
        mesh1 = bpy.data.meshes.new("tabletop")
        tabletop_obj = bpy.data.objects.new("Tabletop_Obj", mesh1)

        scene = bpy.context.scene
        scene.objects.link(tabletop_obj)

        bm = bmesh.new()
        
        #Make the table top:
        
        #If ts == 4, then a cylinder
        #comes out rotated by 45deg,
        #and rotating it screws with
        #the size so it must be made
        #as a cube if table_seg is 4
        
        #If ts == 4, make a square table top:
        if ts == 4:
            bmesh.ops.create_cube(bm, size=1.0)
        #Otherwise, make it a cylinder table top:
        else:
            bmesh.ops.create_cone(bm, 
                                  cap_ends=True, 
                                  cap_tris=False, 
                                  segments=ts, 
                                  diameter1=0.5, 
                                  diameter2=0.5, 
                                  depth=1.0)
                              
        #Apply their sizes (l, w, and t):
        bmesh.ops.scale(bm, vec=(l, w, t), verts=bm.verts)
        
        #Move it up by the table height:
        bmesh.ops.translate(bm,
                            verts=bm.verts,
                            vec=(0.0, 0.0, h - (t / 2.0)))
        
        #Make the table legs (If any):
        if legs > 0:
            #Holds locations for each leg
            bm_loc = bmesh.new()
            
            #Rotation amount:
            r = 360.0 / legs
            m = mathutils.Matrix.Rotation(math.radians(r), 3, 'Z')
            
            #Position the first leg based
            #off the number of table legs
            if legs == 1:
                #if only 1 leg, it goes
                #in the table's center:
                bm_loc.verts.new((0.0 , 0.0, ((h / 2.0) - (t / 2.0))))
            
            elif legs == 4:
                #If just 4 legs, one
                #goes on each corner
                bm_loc.verts.new((lo , lo, ((h / 2.0) - (t / 2.0))))
            else:
                #Otherwise, we always want at least
                #one leg to line up with the x-axis
                bm_loc.verts.new((lo , 0.0, ((h / 2.0) - (t / 2.0))))
            
            #Skip if there's only 1 leg:
            if legs > 1:
                #Duplicate the vert, and
                #rotate it for each leg:
                geom_v = bm_loc.verts[:]
                
                for i in range(0, legs):
                    #Add a new leg:
                    geom_ret = bmesh.ops.duplicate(bm_loc, geom=geom_v)
                    
                    #Rotate it:
                    geom_v = [e for e in geom_ret["geom"] 
                              if isinstance(e, bmesh.types.BMVert)]
                    del geom_ret
                    
                    bmesh.ops.rotate(bm_loc,
                                     verts=geom_v,
                                     cent=(0.0, 0.0, 0.0),
                                     matrix=m)
            
            #Resize the leg placement by
            #multiplying x and y scales:
            bmesh.ops.scale(bm_loc, vec=(l, w, 1.0), verts=bm_loc.verts)
            
            #Now create the table legs at the
            #location of each vert in bm_loc:
            for v in bm_loc.verts:
                bm = add_table_leg(bm, v, legs, lt, ls, h, t, m)
        
        
        #Now update the mesh object:
        bm.to_mesh(mesh1)
        mesh1.update()
        bm.free()
        
        return {'FINISHED'}


def menu_func(self, context):
    self.layout.operator(AddTable.bl_idname, icon='NOCURVE')


def register():
    bpy.utils.register_class(AddTable)
    bpy.types.INFO_MT_mesh_add.append(menu_func)


def unregister():
    bpy.utils.unregister_class(AddTable)
    bpy.types.INFO_MT_mesh_add.remove(menu_func)

if __name__ == "__main__":
    register()