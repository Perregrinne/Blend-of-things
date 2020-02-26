bl_info = {
    "name": "Add Shuriken",
    "description": "Generates a shuriken mesh.",
    "author": "Austin Jacob",
    "version": (1, 0, 0),
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
import math
import mathutils

from bpy.props import (
        BoolProperty,
        BoolVectorProperty,
        FloatProperty,
        FloatVectorProperty,
        IntProperty,
        )


class AddShuriken(bpy.types.Operator):
    """Add a shuriken mesh"""
    bl_idname = "mesh.shuriken_add"
    bl_label = "Add Shuriken"
    bl_options = {'REGISTER', 'UNDO'}

    radius1 = FloatProperty(
            name="Outter Radius",
            description="How far the points stick out",
            min=0.0001,
            default=1.0,
            )
    radius2 = FloatProperty(
            name="Inner Radius",
            description="How far inner points of shuriken stick out",
            min=0.0001,
            default=0.375,
            )
    thick = FloatProperty(
            name="Thickness",
            description="Thickness of the shuriken",
            min=0.0001,
            default=0.025,
            )
    cutout_rad = FloatProperty(
            name="Cutout Radius",
            description="Radius of the cutouts between each point",
            min=0.0001,
            default=0.125,
            )
    cent_rad = FloatProperty(
            name="Center Cutout",
            description="Radius of the cutout in the center",
            min=0.0,
            default=0.0875,
            )
    cutout_seg = IntProperty(
            name="Cutout Segments",
            description="Number of segments that make up a cutout cylinder",
            min=4,
            default=32,
            )
    points = IntProperty(
            name="Points",
            description="How many points the shuriken has",
            min=2,
            default=6,
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
        col.label(text="Star", icon="SOLO_OFF")
        col.prop(self, "radius1")
        col.prop(self, "radius2")
        col.prop(self, "thick")
        col.prop(self, "points")
        
        box = layout.box()
        col = box.column()
        col.label(text="Cut-Outs", icon="GROUP_VERTEX")
        col.prop(self, "cent_rad")
        col.prop(self, "cutout_rad")
        col.prop(self, "cutout_seg")
        
        box = layout.box()
        col = box.column()
        col.label(text="Placement", icon="NDOF_TURN")
        col.prop(self, "location")
        col.prop(self, "rotation")

    def execute(self, context):
        
        #Rename the variables
        #to something simpler
        r1 = self.radius1
        r2 = self.radius2
        t = self.thick
        cutr = self.cutout_rad
        centr = self.cent_rad
        p = self.points * 2
        pos = self.location
        rotate = self.rotation
        cseg = self.cutout_seg
        
        #Make the shuriken object:
        mesh = bpy.data.meshes.new("shuriken")
        shuriken_obj = bpy.data.objects.new("Shuriken", mesh)
        
        scene = bpy.context.scene
        scene.objects.link(shuriken_obj)
        bm = bmesh.new()
        
        bmesh.ops.create_circle(bm,
                                cap_ends=True,
                                cap_tris=True,
                                diameter=r1,
                                segments=p)
        
        bm.verts.ensure_lookup_table()
        
        #Scale every other point to r2:
        
        #Get every other point:
        inner_verts = []
        for i in range(0, p + 1):
            if i % 2 == 0:
                inner_verts += [bm.verts[i]]
        
        #It's sideways by 90 degrees:
        rot = mathutils.Matrix.Rotation(math.radians(90), 3, 'Z')
        bmesh.ops.rotate(bm,
                         verts=bm.verts,
                         cent=(0.0, 0.0, 0.0),
                         matrix=rot)
        
        #Pull the inner verts inward:
        loc = mathutils.Matrix.Translation((0.0, 0.0, 0.0))
        delta_r = r2 / r1
        scl = (delta_r, delta_r, 1.0)
        bmesh.ops.scale(bm, 
                        vec=scl,
                        verts=inner_verts)
        
        #When the bm is deleted, all vertex coords disappear.
        #When only v.co was saved, after bm.free(), the verts
        #were deleted, so cutout_coords thought all v.co vals
        #came from the new bm, resulting in cut-out cylinders
        #being placed in places that were not in inner_verts.
        #Each x, y, and z value has to be saved individually.
        cutout_coords_x = []
        cutout_coords_y = []
        cutout_coords_z = []
        for v in inner_verts:
            if v.co.x != 0.0 and v.co.y != 0.0:
                cutout_coords_x += [v.co.x]
                cutout_coords_y += [v.co.y]
                cutout_coords_z += [v.co.z]
        
        #Finalize changes:
        bm.to_mesh(mesh)
        bm.free()
        mesh.update()
        
        #Make outter cuttouts:
        c_mesh = bpy.data.meshes.new("cutouts")
        cutouts_obj = bpy.data.objects.new("Cutouts", c_mesh)
        
        scene = bpy.context.scene
        scene.objects.link(cutouts_obj)
        bm = bmesh.new()
        
        #Create the center cutout:
        if centr > 0.0:
            bmesh.ops.create_cone(bm,
                                  cap_ends=True, 
                                  cap_tris=False, 
                                  segments=cseg, 
                                  diameter1=centr, 
                                  diameter2=centr, 
                                  depth=(t + 0.125),)
        
        #Make each cutout cylinder for the
        #coordinates inside cutout_coords:
        for i in range(0, len(cutout_coords_x)):
            x = cutout_coords_x[i]
            y = cutout_coords_y[i]
            z = cutout_coords_z[i]
            co = (x, y, z)
            #Make the cutout cone:
            new_geom = bmesh.ops.create_cone(bm,
                                             cap_ends=True, 
                                             cap_tris=False, 
                                             segments=cseg, 
                                             diameter1=cutr, 
                                             diameter2=cutr, 
                                             depth=(t + 0.125),)
            
            #And move it to co's location:
            bmesh.ops.translate(bm,
                                verts=new_geom["verts"],
                                vec=co)
        
        #Finalize changes:
        bm.to_mesh(c_mesh)
        bm.free()
        c_mesh.update()
        
        #Boolean these cutouts:
        bpy.context.scene.objects.active = shuriken_obj
        cut = shuriken_obj.modifiers.new("cut_holes", type='BOOLEAN')
        cut.operation = 'DIFFERENCE'
        cut.object = cutouts_obj
        bpy.ops.object.modifier_apply(apply_as='DATA', modifier=cut.name)
        
        #Delete the cutouts:
        bpy.ops.object.select_all(action='DESELECT')
        cutouts_obj.select = True
        bpy.ops.object.delete()
        
        #Apply solidify modifier:
        bpy.context.scene.objects.active = shuriken_obj
        thick_mod = shuriken_obj.modifiers.new("thick_mod", type='SOLIDIFY')
        thick_mod.thickness = t
        bpy.ops.object.modifier_apply(apply_as='DATA', modifier=thick_mod.name)
        
        #Move and rotate it:
        shuriken_obj.rotation_euler = rotate
        shuriken_obj.location = pos
        
        bpy.ops.object.transform_apply(location=True, 
                                       rotation=True, 
                                       scale=True)
        
        #And of course, the name change:
        context.active_object.name = 'Shuriken'

        return {'FINISHED'}


def menu_func(self, context):
    self.layout.operator(AddShuriken.bl_idname, icon='MOD_PARTICLES')


def register():
    bpy.utils.register_class(AddShuriken)
    bpy.types.INFO_MT_mesh_add.append(menu_func)


def unregister():
    bpy.utils.unregister_class(AddShuriken)
    bpy.types.INFO_MT_mesh_add.remove(menu_func)

if __name__ == "__main__":
    register()