bl_info = {
    "name": "Add Playground Structure",
    "description": "Generates a playground structure mesh.",
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

class AddPlaygroundStructure(bpy.types.Operator):
    """Add a simple playground structure"""
    bl_idname = "mesh.playground_structure_add"
    bl_label = "Add Playground Structure"
    bl_options = {'REGISTER', 'UNDO'}

    length = FloatProperty(
            name="Length",
            description="How long the structure is",
            min=0.01,
            default=1.0,
            )
    width = FloatProperty(
            name="Width",
            description="How wide the structure is",
            min=0.01,
            default=1.0,
            )
    roof_height = FloatProperty(
            name="Roof Height",
            description="How tall the roof is",
            min=0.01,
            default=0.5,
            )
    roof_thick = FloatProperty(
            name="Roof Thickness",
            description="Thickness of the roof",
            min=0.0,
            default=0.125,
            )
    roof_x = FloatProperty(
            name="Roof Scale X",
            description="Grows/Shrinks the top of the roof along the x-axis",
            min=0.0,
            default=0.5,
            )
    roof_y = FloatProperty(
            name="Roof Scale Y",
            description="Grows/Shrinks the top of the roof along the y-axis",
            min=0.0,
            default=0.5,
            )
    roof_str = FloatProperty(
            name="Roof Bevel Offset",
            description="How strong the roof bevel is",
            min=0.0,
            default=0.0125,
            )
    roof_seg = IntProperty(
            name="Roof Bevel Segments",
            description="How many segments make up the roof bevel",
            min=0,
            default=2,
            )
    platform_h = FloatProperty(
            name="Platform Height",
            description="How high off the ground the platform is",
            min=0.01,
            default=2.0,
            )
    platform_t = FloatProperty(
            name="Platform Thickness",
            description="How thick the platform is",
            min=0.01,
            default=0.05,
            )
    platform_str = FloatProperty(
            name="Platform Bevel Offset",
            description="How strong the platform bevel is",
            min=0.0,
            default=0.0125,
            )
    platform_seg = IntProperty(
            name="Roof Bevel Segments",
            description="How many segments make up the platform bevel",
            min=0,
            default=2,
            )
    supports_seg = IntProperty(
            name="Supports Segments",
            description="How many segments make up the cylinders for the supports",
            min=3,
            default=16,
            )
    supports_rad = FloatProperty(
            name="Supports Radius",
            description="How thick the supports are",
            min=0.001,
            default=0.0675,
            )
    supports_h = FloatProperty(
            name="Supports Height",
            description="How tall the supports are",
            min=0.01,
            default=4.0,
            )
    supports_shift = FloatProperty(
            name="Supports Shift",
            description="Moves the supports away from the edge",
            default=0.0125,
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
        col.label(text="General", icon="NOCURVE")
        col.prop(self, "length")
        col.prop(self, "width")
        col.prop(self, "location")
        col.prop(self, "rotation")
        
        box = layout.box()
        col = box.column()
        col.label(text="Roof", icon="LINCURVE")
        col.prop(self, "roof_height")
        col.prop(self, "roof_thick")
        col.prop(self, "roof_x")
        col.prop(self, "roof_y")
        col.prop(self, "roof_str")
        col.prop(self, "roof_seg")
        
        box = layout.box()
        col = box.column()
        col.label(text="Supports", icon="PAUSE")
        col.prop(self, "supports_rad")
        col.prop(self, "supports_h")
        col.prop(self, "supports_shift")
        col.prop(self, "supports_seg")
        
        box = layout.box()
        col = box.column()
        col.label(text="Platform", icon="ZOOMOUT")
        col.prop(self, "platform_t")
        col.prop(self, "platform_h")
        col.prop(self, "platform_str")
        col.prop(self, "platform_seg")

    def execute(self, context):
        #Rename the variables
        #to something simpler
        l = self.length
        w = self.width
        rh = self.roof_height
        rt = self.roof_thick
        rx = self.roof_x
        ry = self.roof_y
        rstr = self.roof_str
        rseg = self.roof_seg
        ph = self.platform_h
        pt = self.platform_t
        pstr = self.platform_str
        pseg = self.platform_seg
        sr = self.supports_rad
        sh = self.supports_h
        ss = self.supports_seg
        sshift = self.supports_shift
        pos = self.location
        rotate = self.rotation
        
        #Basic roof geometry:
        verts= [(-l * rx, -w * ry, rh + sh),
                (-l * rx, w * ry, rh + sh),
                (l * rx, -w * ry, rh + sh),
                (l * rx, w * ry, rh + sh),
                (-l, w, sh),
                (-l, -w , sh),
                (l, w, sh),
                (l, -w, sh),
                ]
        
        faces= [(5, 0, 1, 4),
                (4, 1, 3, 6),
                (6, 3, 2, 7),
                (7, 2, 0, 5),
                (3, 1, 0, 2),
                ]
        
        #Make the roof:
        r_mesh = bpy.data.meshes.new("roof")
        roof_obj = bpy.data.objects.new("Roof_Obj", r_mesh)

        scene = bpy.context.scene
        scene.objects.link(roof_obj)
        bm = bmesh.new()
        
        #Add verts, then faces:
        for v_co in verts:
            bm.verts.new(v_co)

        bm.verts.ensure_lookup_table()
        for f_idx in faces:
            bm.faces.new([bm.verts[i] for i in f_idx])
        
        #Smooth it:
        for f in bm.faces:
            f.smooth = True
        
        
        
        #Finalize changes:
        bm.to_mesh(r_mesh)
        bm.free()
        r_mesh.update()
        
        #Apply solidify modifier:
        bpy.context.scene.objects.active = roof_obj
        thick_mod = roof_obj.modifiers.new("thick_mod", type='SOLIDIFY')
        thick_mod.thickness = rt
        bpy.ops.object.modifier_apply(apply_as='DATA', modifier=thick_mod.name)
        
        
        bm = bmesh.new()
        bm.from_mesh(r_mesh)
        
        #Now fix the bottom verts:
        for v in bm.verts:
            if v.co.z < sh:
                v.co.z = sh
        
        if rseg > 0 and rstr > 0.0:
            #Now bevel it:
            bmesh.ops.bevel(bm, 
                            geom=bm.verts[:] + bm.edges[:], 
                            offset=rstr, 
                            offset_type=0, 
                            segments=rseg, 
                            profile=0.5, 
                            clamp_overlap=True,)
        
        #Finalize changes:
        bm.to_mesh(r_mesh)
        bm.free()
        r_mesh.update()
        
        #Make the platform:
        p_mesh = bpy.data.meshes.new("platform")
        platform_obj = bpy.data.objects.new("Platform_Obj", p_mesh)

        scene = bpy.context.scene
        scene.objects.link(platform_obj)
        bm = bmesh.new()
        
        #Make the box:
        bmesh.ops.create_cube(bm, size=2.0,)
        
        #And resize it:
        loc = mathutils.Matrix.Translation((0.0, 0.0, 0.0))
        scl = (l, w, pt)
        bmesh.ops.scale(bm, 
                        vec=scl, 
                        space=loc, 
                        verts=bm.verts)
        
        #Move it up to the proper height:
        bmesh.ops.translate(bm, 
                            vec=(0.0, 0.0, ph), 
                            verts=bm.verts)
        
        if pstr > 0.0 and pseg > 0:
            #And bevel it:
            new_geom = bmesh.ops.bevel(bm, 
                                       geom=bm.verts[:] + bm.edges[:], 
                                       offset=pstr, 
                                       offset_type=0, 
                                       segments=pseg, 
                                       profile=0.5, 
                                       clamp_overlap=True,)
            
            for f in new_geom["faces"]:
                f.smooth = True
        
        #Finalize changes:
        bm.to_mesh(p_mesh)
        bm.free()
        p_mesh.update()
        
        #Make the supports:
        s_mesh = bpy.data.meshes.new("supports")
        supports_obj = bpy.data.objects.new("Supports_Obj", s_mesh)

        scene = bpy.context.scene
        scene.objects.link(supports_obj)
        bm = bmesh.new()
        
        #Positions for the supports:
        loc = [(l - sr - sshift, w - sr - sshift, sh / 2.0),
               (-(l - sr - sshift), w - sr - sshift, sh / 2.0),
               (l - sr - sshift, -(w - sr - sshift), sh / 2.0),
               (-(l - sr - sshift), -(w - sr - sshift), sh / 2.0),]
        
        #Make 4 supports:
        #Add the cylinder:
        for i in range(0, 4):
            new_geom = bmesh.ops.create_cone(bm, 
                                             cap_ends=False,
                                             segments=ss, 
                                             diameter1=sr, 
                                             diameter2=sr, 
                                             depth=sh,)
            
            #Move it:
            bmesh.ops.translate(bm,
                                verts=new_geom["verts"],
                                vec=loc[i])
            
            del new_geom
        
        #Smooth it:
        for f in bm.faces:
            f.smooth = True
        
        #Finalize changes:
        bm.to_mesh(s_mesh)
        bm.free()
        s_mesh.update()
        
        #Combine the objects:
        bpy.ops.object.select_all(action='DESELECT')
        roof_obj.select = True
        bpy.context.scene.objects.active = roof_obj
        platform_obj.select = True
        supports_obj.select = True
        bpy.ops.object.join()
        context.active_object.name = 'Playground_Structure'
        
        #Move and rotate it:
        roof_obj.rotation_euler = rotate
        roof_obj.location = pos
        
        bpy.ops.object.transform_apply(location=True, 
                                       rotation=True, 
                                       scale=True)
        

        return {'FINISHED'}


def menu_func(self, context):
    self.layout.operator(AddPlaygroundStructure.bl_idname, icon='NOCURVE')


def register():
    bpy.utils.register_class(AddPlaygroundStructure)
    bpy.types.INFO_MT_mesh_add.append(menu_func)


def unregister():
    bpy.utils.unregister_class(AddPlaygroundStructure)
    bpy.types.INFO_MT_mesh_add.remove(menu_func)

if __name__ == "__main__":
    register()