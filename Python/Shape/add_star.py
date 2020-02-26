bl_info = {
    "name": "Add Star",
    "description": "Generates a simple star shape (outline or filled).",
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


class AddStar(bpy.types.Operator):
    """Add a simple star shape"""
    bl_idname = "mesh.star_add"
    bl_label = "Add Star"
    bl_options = {'REGISTER', 'UNDO'}

    radius1 = FloatProperty(
            name="Outter Radius",
            description="How far the points stick out",
            min=0.0001,
            default=1.0,
            )
    radius2 = FloatProperty(
            name="Inner Radius",
            description="How far inner points of star stick out",
            min=0.0001,
            default=0.375,
            )
    points = IntProperty(
            name="Points",
            description="How many points the star has",
            min=2,
            default=5,
            )
    fill = BoolProperty(
            name="Fill Mesh",
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
        
        #Rename the variables
        #to something simpler
        r1 = self.radius1
        r2 = self.radius2
        p = self.points * 2
        fill = self.fill
        pos = self.location
        rotate = self.rotation
        
        #Make the star object:
        mesh = bpy.data.meshes.new("star")
        star_obj = bpy.data.objects.new("Star", mesh)
        
        scene = bpy.context.scene
        scene.objects.link(star_obj)
        bm = bmesh.new()
        
        bmesh.ops.create_circle(bm,
                                cap_ends=fill,
                                cap_tris=True,
                                diameter=r1,
                                segments=p)
        
        bm.verts.ensure_lookup_table()
        
        #Scale every other point to r2:
        
        #Get every other point:
        inner_verts = []
        for i in range(0, p + 1):
            if not fill:
                if i % 2 == 1:
                    inner_verts += [bm.verts[i]]
            else:
                if i % 2 == 0:
                    inner_verts += [bm.verts[i]]
        #Scale:
        loc = mathutils.Matrix.Translation((0.0, 0.0, 0.0))
        delta_r = r2 / r1
        scl = (delta_r, delta_r, 1.0)
        bmesh.ops.scale(bm, 
                        vec=scl, 
                        space=loc, 
                        verts=inner_verts)
        
        #Rotate and move:
        rot_x = mathutils.Matrix.Rotation((rotate.x), 3, 'X')
        bmesh.ops.rotate(bm,
                         verts=bm.verts,
                         cent=(0.0, 0.0, 0.0),
                         matrix=rot_x)
        
        rot_y = mathutils.Matrix.Rotation((rotate.y), 3, 'Y')
        bmesh.ops.rotate(bm,
                         verts=bm.verts,
                         cent=(0.0, 0.0, 0.0),
                         matrix=rot_y)
        
        rot_z = mathutils.Matrix.Rotation((rotate.z), 3, 'Z')
        bmesh.ops.rotate(bm,
                         verts=bm.verts,
                         cent=(0.0, 0.0, 0.0),
                         matrix=rot_z)
        
        bmesh.ops.translate(bm,
                            verts=bm.verts,
                            vec=pos)
        
        #Finalize changes:
        bm.to_mesh(mesh)
        bm.free()
        mesh.update()

        return {'FINISHED'}


def menu_func(self, context):
    self.layout.operator(AddStar.bl_idname, icon='SOLO_OFF')


def register():
    bpy.utils.register_class(AddStar)
    bpy.types.INFO_MT_mesh_add.append(menu_func)


def unregister():
    bpy.utils.unregister_class(AddStar)
    bpy.types.INFO_MT_mesh_add.remove(menu_func)

if __name__ == "__main__":
    register()