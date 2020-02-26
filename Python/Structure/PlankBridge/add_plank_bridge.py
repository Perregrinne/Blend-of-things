bl_info = {
    "name": "Add Plank Bridge",
    "description": "Generates a simple bridge made of planks and rope.",
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
import mathutils
import math

from bpy.props import (
        BoolProperty,
        BoolVectorProperty,
        FloatProperty,
        FloatVectorProperty,
        IntProperty,
        )


class AddPlankBridge(bpy.types.Operator):
    """Add a simple bridge mesh"""
    bl_idname = "mesh.plank_bridge_add"
    bl_label = "Add Plank Bridge"
    bl_options = {'REGISTER', 'UNDO'}

    bridge_length = FloatProperty(
            name="Bridge Length",
            description="Bridge Length",
            min=0.01,
            default=3.0,
            )
    plank_num = IntProperty(
            name="Planks",
            description="Number of planks",
            min=2,
            default=12,
            )
    plank_length = FloatProperty(
            name="Plank Length",
            description="Length of a single plank",
            min=0.01,
            default=0.425,
            )
    plank_width = FloatProperty(
            name="Plank Width",
            description="Width of a single plank",
            min=0.01,
            default=1.25,
            )
    plank_height = FloatProperty(
            name="Plank Height",
            description="Height of a single plank",
            min=0.01,
            default=0.05,
            )
    rope_num = IntProperty(
            name="Rope Number",
            description="Number of ropes that hold the planks together",
            min=0,
            default=2,
            )
    rope_width = FloatProperty(
            name="Rope Width",
            description="Distance between the two furthest ropes",
            min=0.01,
            default=0.5,
            )
    rope_drop = FloatProperty(
            name="Rope Drop",
            description="How far up or down the bridge rises or sinks",
            default=-0.125,
            )
    bridge_curve = FloatProperty(
            name="Bridge Curvature",
            description="Affects the curved shape of the bridge",
            min=0.0, max=1.0,
            default=1.0,
            )
    rope_z_offset = FloatProperty(
            name="Rope Z-Offset",
            description="Moves the ropes up or down",
            default= -0.025,
            )
    rope_thick = FloatProperty(
            name="Rope Thickness",
            description="Thickness of a rope",
            min=0.001,
            default=0.0125,
            )
    rope_seg = IntProperty(
            name="Rope Segments",
            description="Number of rope pieces that make up the length of rope",
            min=2,
            default=32,
            )
    ring_seg = IntProperty(
            name="Ring Segments",
            description="Number of segments that make up a piece of rope",
            min=3,
            default=16,
            )
    bev_seg = IntProperty(
            name="Bevel Segments",
            description="Bevel segments for the planks",
            min=0,
            default=2,
            )
    bev_str = FloatProperty(
            name="Bevel Offset",
            description="Offset of the plank beveling",
            min=0.0,
            default=0.005,
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
        col.label(text="Bridge", icon="ZOOMOUT")
        col.prop(self, "bridge_length")
        col.prop(self, "bridge_curve")
        col.prop(self, "location")
        col.prop(self, "rotation")
        
        box = layout.box()
        col = box.column()
        col.label(text="Planks", icon="COLLAPSEMENU")
        col.prop(self, "plank_num")
        col.prop(self, "plank_length")
        col.prop(self, "plank_width")
        col.prop(self, "plank_height")
        col.prop(self, "bev_seg")
        col.prop(self, "bev_str")
        
        box = layout.box()
        col = box.column()
        col.label(text="Ropes", icon="GRIP")
        col.prop(self, "rope_num")
        col.prop(self, "rope_seg")
        col.prop(self, "ring_seg")
        col.prop(self, "rope_width")
        col.prop(self, "rope_thick")
        col.prop(self, "rope_drop")
        col.prop(self, "rope_z_offset")

    def execute(self, context):
        #Rename the variables
        #to something simpler:
        pn = self.plank_num
        pl = self.plank_length
        pw = self.plank_width
        ph = self.plank_height
        bl = self.bridge_length
        rn = self.rope_num
        rw = self.rope_width
        rd = self.rope_drop
        rz = self.rope_z_offset
        rt = self.rope_thick
        rs = self.rope_seg
        str = self.bev_str
        seg = self.bev_seg
        ring = self.ring_seg
        bc = self.bridge_curve
        pos = self.location
        rotate = self.rotation
        
        #Make the curve object:
        
        #Make the bezier curve:
        bpy.ops.curve.primitive_bezier_curve_add(enter_editmode=True)
        curve_obj = bpy.context.active_object
        
        #It needs to have 3 total points
        bpy.ops.curve.subdivide(number_cuts=1)

        #Get the list of points:
        center_x = bl / 2.0
        handle_x = (bl / 4.0) * bc
        curve_points = curve_obj.data.splines[0].bezier_points
        curve_points[0].co.x = -bl / 2.0
        curve_points[0].co.y = 0.0
        curve_points[0].co.z = 0.0
        curve_points[0].handle_left = (-center_x - handle_x, 0.0, 0.0)
        curve_points[0].handle_right = (-center_x + handle_x, 0.0, 0.0)
        
        curve_points[1].co.x = 0.0
        curve_points[1].co.y = 0.0
        curve_points[1].co.z = rd
        curve_points[1].handle_left = (-bl / 4.0, 0.0, rd)
        curve_points[1].handle_right = (bl / 4.0, 0.0, rd)
        
        curve_points[2].co.x = bl / 2.0
        curve_points[2].co.y = 0.0
        curve_points[2].co.z = 0.0
        curve_points[2].handle_left = (center_x - handle_x, 0.0, 0.0)
        curve_points[2].handle_right = (center_x + handle_x, 0.0, 0.0)
        
        #Finalize changes:
        bpy.ops.object.mode_set(mode='OBJECT')
        
        #Make the first plank:
        p_mesh = bpy.data.meshes.new("plank")
        plank_obj = bpy.data.objects.new("Plank_Obj", p_mesh)

        scene = bpy.context.scene
        scene.objects.link(plank_obj)
        bm = bmesh.new()
        
        #Create the plank as a cube
        bmesh.ops.create_cube(bm, size=0.5,)
        
        #Resize the plank:
        loc = mathutils.Matrix.Translation((0.0, 0.0, 0.0))
        bmesh.ops.scale(bm, 
                        vec=(pl, pw, ph), 
                        space=loc, 
                        verts=bm.verts)
        
        #Bevel it:
        if str > 0.0 and seg > 0:
            new_geom = bmesh.ops.bevel(bm, 
                                       geom=bm.verts[:] + bm.edges[:], 
                                       offset=str, 
                                       offset_type=0, 
                                       segments=seg, 
                                       profile=0.5, 
                                       clamp_overlap=True)
            
            #Get the new, beveled faces:
            face_geom = new_geom["faces"]
            
            #And then smooth them:
            for f in face_geom:
                f.smooth = True
        
        #Finalize changes:
        bm.to_mesh(p_mesh)
        bm.free()
        p_mesh.update()
        
        #To copy the curve in arc_length(),
        #the curve object has to be active:
        bpy.ops.object.select_all(action='DESELECT')
        curve_obj.select = True
        bpy.context.scene.objects.active = curve_obj
        bpy.ops.object.convert(target='MESH')
        bpy.ops.object.mode_set(mode='EDIT')
        
        bm = bmesh.new()
        bm = bmesh.from_edit_mesh(curve_obj.data)
        
        #Sum of the edges
        sum = 0.0
        
        for e in bm.edges:
            #Trying to make my code more 
            #PEP-8 friendly or something
            v0 = e.verts[0].co
            v1 = e.verts[1].co
            x = (v1.x - v0.x)**2
            y = (v1.y - v0.y)**2
            z = (v1.z - v0.z)**2
            #All confusing simplifications aside,
            #it is still the 3D distance formula:
            sum += math.sqrt(x + y + z)
        
        bm.free()
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.convert(target='CURVE')
        
        #With the length of the 
        #curve, make the ropes:
        if rn > 0:
            r_mesh = bpy.data.meshes.new("rope")
            rope_obj = bpy.data.objects.new("Rope_Obj", r_mesh)
            
            scene = bpy.context.scene
            scene.objects.link(rope_obj)
            bm = bmesh.new()
            
            #Make the first segment:
            bmesh.ops.create_cone(bm, 
                                  cap_ends=False,
                                  segments=ring, 
                                  diameter1=rt, 
                                  diameter2=rt, 
                                  depth=sum / rs,)
            
            #Smooth it:
            for f in bm.faces:
                f.smooth = True
            
            #Rotate the segments of rope:
            rot = mathutils.Matrix.Rotation(math.radians(90), 3, 'Y')
            bmesh.ops.rotate(bm,
                             verts=bm.verts,
                             cent=(0.0, 0.0, 0.0),
                             matrix=rot)
            
            if rn > 1:
                #Move the segment horizontally and vertically:
                bmesh.ops.translate(bm,
                                    verts=bm.verts,
                                    vec=((sum / (2.0 * rs)), -rw / 2.0, 0.0))
                
                curr_geom = bm.verts[:] + bm.edges[:] + bm.faces[:]
                
                for i in range(1, rn):
                    dupl_geom = bmesh.ops.duplicate(bm,
                                                    geom=curr_geom)
                    
                    new_verts = [v for v in dupl_geom["geom"]
                                 if isinstance(v, bmesh.types.BMVert)]
                    new_edges = [e for e in dupl_geom["geom"]
                                 if isinstance(e, bmesh.types.BMEdge)]
                    new_faces = [f for f in dupl_geom["geom"]
                                 if isinstance(f, bmesh.types.BMFace)]
                    
                    curr_geom = new_verts[:] + new_edges[:] + new_faces[:]
                    del dupl_geom

                    #Move it to the next position:
                    bmesh.ops.translate(bm,
                                        verts=new_verts[:],
                                        vec=(0.0, rw / (rn - 1), 0.0))
            
            #Make sure it's in the right place vertically:
            bmesh.ops.translate(bm,
                                verts=bm.verts,
                                vec=(0.0, 0.0, rz))
            
            #Finalize changes:
            bm.to_mesh(r_mesh)
            bm.free()
            r_mesh.update()
            
            #Apply the curve and array 
            #modifiers to the rope_obj
            bpy.ops.object.select_all(action='DESELECT')
            rope_obj.select = True
            bpy.context.scene.objects.active = rope_obj
            array_mod = rope_obj.modifiers.new(name='rope_array', type='ARRAY')
            array_mod.use_constant_offset = False
            array_mod.use_relative_offset = True
            array_mod.count = rs
            array_mod.relative_offset_displace = [1.0, 0.0, 0.0]
            
            #Apply curve modifier to the planks:
            curve_mod = rope_obj.modifiers.new(name='c_mod', type='CURVE')
            curve_mod.object = curve_obj
            bpy.ops.object.modifier_apply(modifier=array_mod.name)
            bpy.ops.object.modifier_apply(modifier=curve_mod.name)
            
        
        #Apply array modifier to the 
        #planks using the arc length
        bpy.ops.object.select_all(action='DESELECT')
        plank_obj.select = True
        bpy.context.scene.objects.active = plank_obj
        array_mod = plank_obj.modifiers.new(name='plank_array', type='ARRAY')
        array_mod.use_constant_offset = True
        array_mod.use_relative_offset = False
        array_mod.count = pn
        array_mod.constant_offset_displace = [(sum / (pn - 1)), 0.0, 0.0]
        
        #Apply curve modifier to the planks:
        curve_mod = plank_obj.modifiers.new(name='c_mod', type='CURVE')
        curve_mod.object = curve_obj
        bpy.ops.object.modifier_apply(modifier=array_mod.name)
        bpy.ops.object.modifier_apply(modifier=curve_mod.name)
        
        #Delete the curve:
        bpy.ops.object.select_all(action='DESELECT')
        curve_obj.select = True
        bpy.ops.object.delete()
        
        bpy.ops.object.select_all(action='DESELECT')
        plank_obj.select = True
        bpy.context.scene.objects.active = plank_obj
        #Join the meshes:
        if rn > 0:
            rope_obj.select = True
            bpy.ops.object.join()
        context.active_object.name = 'Plank_Bridge'
        
        #Move and rotate it:
        plank_obj.rotation_euler = rotate
        plank_obj.location = pos
        
        bpy.ops.object.transform_apply(location=True, 
                                       rotation=True, 
                                       scale=True)

        return {'FINISHED'}


def menu_func(self, context):
    self.layout.operator(AddPlankBridge.bl_idname, icon='MESH_CUBE')


def register():
    bpy.utils.register_class(AddPlankBridge)
    bpy.types.INFO_MT_mesh_add.append(menu_func)


def unregister():
    bpy.utils.unregister_class(AddPlankBridge)
    bpy.types.INFO_MT_mesh_add.remove(menu_func)

if __name__ == "__main__":
    register()