bl_info = {
    "name": "Rock Wall Generator",
    "description": "Generates a simple rock wall.",
    "author": "Austin Jacob",
    "version": (1, 0, 0),
    "blender": (2, 79, 0),
    "location": "View3D > Add > Mesh",
    "warning": "", # used for warning icon and text in addons panel
    "wiki_url": "",
    "tracker_url": "",
    "category": "Add Mesh"}

# Copyright 2019 Austin Jacob
# 
# Permission is hereby granted, free of charge, to any person 
# obtaining a copy of this software and associated documentation 
# files (the "Software"), to deal in the Software without 
# restriction, including without limitation the rights to use, 
# copy, modify, merge, publish, distribute, sublicense, and/or 
# sell copies of the Software, and to permit persons to whom the 
# Software is furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be 
# included in all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, 
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES 
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND 
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS 
# BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN 
# ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN 
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE 
# SOFTWARE.

import bpy
import bmesh
import random

from bpy.props import (
        BoolProperty,
        BoolVectorProperty,
        FloatProperty,
        FloatVectorProperty,
        IntProperty,
        )


class AddRockWall(bpy.types.Operator):
    """Add a rock wall mesh"""
    bl_idname = "mesh.rock_wall_add"
    bl_label = "Add Rock Wall"
    bl_options = {'REGISTER', 'UNDO'}

    length = FloatProperty(
            name="Length",
            description="Length of the wall",
            min=0.001,
            default=0.025,
            )
    width = FloatProperty(
            name="Width",
            description="Width of the wall",
            min=0.001,
            default=1.0,
            )
    height = FloatProperty(
            name="Height",
            description="Height of the wall",
            min=0.001,
            default=3.0,
            )
    rock_num = IntProperty(
            name="Number of Rocks",
            description="Number of rocks on the wall",
            min=1,
            default=16,
            )
    size_min = FloatProperty(
            name="Min Rock Size",
            description="Minimum size a rock can be",
            min=0.001,
            default=0.125,
            )
    size_max = FloatProperty(
            name="Max Rock Size",
            description="Maximum size a rock can be",
            min=0.001,
            default=0.25,
            )
    subdivs = IntProperty(
            name="Rock Subdivisions",
            description="Affects the poly count of each rock",
            min=1,
            default=3,
            )
    seed = IntProperty(
            name="Random Seed",
            description="Influences the randomly generated values",
            default=0,
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
        l = self.length
        w = self.width
        h = self.height
        n = self.rock_num
        min = self.size_min
        max = self.size_max
        sub = self.subdivs
        seed = self.seed
        pos = self.location
        rotate = self.rotation
        
        
       #Make the wall object:
        w_mesh = bpy.data.meshes.new("wall")
        wall_obj = bpy.data.objects.new("Wall_Obj", w_mesh)

        scene = bpy.context.scene
        scene.objects.link(wall_obj)
        bm = bmesh.new()
        
        #Create the wall as a cube
        bmesh.ops.create_cube(bm, size=0.5,)
        
        #Resize the wall:
        bmesh.ops.scale(bm, 
                        vec=(l, w, h), 
                        verts=bm.verts)
        
        #Finalize changes:
        bm.to_mesh(w_mesh)
        bm.free()
        w_mesh.update()
        
        #Make each rock:
        rocks = []
        r_mesh = bpy.data.meshes.new("rocks")
        rocks_obj = bpy.data.objects.new("Rocks_Obj", r_mesh)
        
        scene = bpy.context.scene
        scene.objects.link(rocks_obj)
        bm = bmesh.new()
        
        #Create the rock as an ico sphere
        bmesh.ops.create_icosphere(bm, 
                                   subdivisions=sub, 
                                   diameter=max,)
        
        bm.verts.ensure_lookup_table()
        bm.faces.ensure_lookup_table()
        
        for f in bm.faces:
            f.smooth = True
        
        #Grab random verts:
        vert_list = []
        i = random.randint(5, 11 * sub)
        while i >= 0:
            v = bm.verts[random.randint(0, len(bm.verts)-1)]
            #Check for duplicates:
            duplicate = False
            for vl in vert_list:
                if v == vl:
                    duplicate = True
            if not duplicate:
                vert_list += [v]
                i -= 1
        
        #Resize the rock:
        scl = (min / max, min / max, min / max)
        
        bmesh.ops.scale(bm, 
                        vec=scl, 
                        verts=vert_list)
        
        #Finalize changes:
        bm.to_mesh(r_mesh)
        bm.free()
        r_mesh.update()
        
        #Make the screw cutout for each rock:
        
        
        #Move and rotate it:
        wall_obj.rotation_euler = rotate
        wall_obj.location = pos
        
        bpy.ops.object.transform_apply(location=True, 
                                       rotation=True, 
                                       scale=True)

        return {'FINISHED'}


def menu_func(self, context):
    self.layout.operator(AddRockWall.bl_idname, icon='MESH_PLANE')


def register():
    bpy.utils.register_class(AddRockWall)
    bpy.types.INFO_MT_mesh_add.append(menu_func)


def unregister():
    bpy.utils.unregister_class(AddRockWall)
    bpy.types.INFO_MT_mesh_add.remove(menu_func)

if __name__ == "__main__":
    register()