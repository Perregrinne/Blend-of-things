bl_info = {
    "name": "Add Blade",
    "description": "Generate straight or curved blades.",
    "author": "Austin Jacob",
    "version": (3, 0, 0),
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

from bpy.props import (
        BoolProperty,
        BoolVectorProperty,
        FloatProperty,
        FloatVectorProperty,
        IntProperty,
        EnumProperty,
        )

#bm is the bmesh; x, y, and z
#are the center of the bounds
#while l, w, h are the length
#height, width of the bounds,
#respectively. This finds all
#edges in bounds, and returns
#them to execute() in a list.
def get_e_in_bounds(edges, x, y, z, l, w, h):
    #Holds all edges within bounds:
    within_bounds = []
    
    x0 = x + (l / 2.0)
    x1 = x + (-l / 2.0)
    y0 = y + (w / 2.0)
    y1 = y + (-w / 2.0)
    z0 = z + (h / 2.0)
    z1 = z + (-h / 2.0)
    
    #If both verts of an edge are inside
    #bounds on the x, y, and z axis, add
    #that edge to the list of edges, and
    #finally, return the completed list:
    for e in edges:
        if e.verts[0].co.x <= x0 and e.verts[0].co.x >= x1:
            if e.verts[1].co.x <= x0 and e.verts[1].co.x >= x1:
                if e.verts[0].co.y <= y0 and e.verts[0].co.y >= y1:
                    if e.verts[1].co.y <= y0 and e.verts[1].co.y >= y1:
                        if e.verts[0].co.z <= z0 and e.verts[0].co.z >= z1:
                            if e.verts[1].co.z <= z0 and e.verts[1].co.z >= z1:
                                within_bounds += [e]
    return within_bounds

#Make the grip or the hilt or whatever:
def beveled_box(bm, l, w, h, mov, seg, str, p, is_g):
    #is_g is "is_grip?" If is_g is true,
    #then the front shouldn't be beveled
    
    bmesh.ops.create_cube(bm, size=1.0)
    #Scale it:
    bmesh.ops.scale(bm, vec=(l, w, h), verts=bm.verts)
    #Move it:
    bmesh.ops.translate(bm, vec=mov, verts=bm.verts)
    
    #Bevel it:
    if seg > 0 and str > 0.0:
        v_geom = []
        e_geom = []
        if is_g:
            #Find the x-val of the front-most face:
            max_x = -l
            for e in bm.edges:
                v0 = e.verts[0].co.x
                v1 = e.verts[1].co.x
                if v0 > max_x:
                    max_x = v0
                if v1 > max_x:
                    max_x = v1
            #Find the geom at the front-most face:
            for e in bm.edges:
                v0 = e.verts[0]
                v1 = e.verts[1]
                if v0.co.x < max_x or v1.co.x < max_x:
                    #Check for duplicates:
                    #v0:
                    not_found = True
                    for v in v_geom:
                        if v0 == v:
                            not_found = False
                    if not_found:
                        v_geom += [v0]
                    #v1:
                    not_found = True
                    for v in v_geom:
                        if v1 == v:
                            not_found = False
                    if not_found:
                        v_geom += [v1]
                    #e:
                    not_found = True
                    for e1 in e_geom:
                        if e1 == e:
                            not_found = False
                    if not_found:
                        e_geom += [e]
        else:
            v_geom = bm.verts[:]
            e_geom = bm.edges[:]
        new_geom = bmesh.ops.bevel(bm, 
                                   geom=v_geom[:] + e_geom[:], 
                                   offset=str, 
                                   offset_type=0, 
                                   segments=seg,
                                   profile=p,
                                   clamp_overlap=True)
        
        for f in new_geom["faces"]:
            f.smooth = True
        
    return bm

class AddBlade(bpy.types.Operator):
    bl_idname = "mesh.blade_add"
    bl_label = "Add Blade"
    bl_options = {'REGISTER', 'UNDO'}

    length = FloatProperty(
            name="Segment Length",
            description="Length of one section of the blade (excluding the point)",
            min=0.001,
            default=0.2,
            )
    width = FloatProperty(
            name="Width",
            description="Width of the  middle of the blade",
            min=0.001,
            default=0.025,
            )
    shift_l = FloatProperty(
            name="Shift Left",
            description="Shifts the left edge of the blade",
            default=0.0125,
            )
    shift_r = FloatProperty(
            name="Shift Right",
            description="Shifts the right edge of the blade",
            default=0.0125,
            )
    height = FloatProperty(
            name="Height",
            description="How tall the blade is.",
            min=0.01,
            default=0.0125,
            )
    point = FloatProperty(
            name="Point Length",
            description="How far the tip of the blade extends from the last segment",
            min=0.0,
            default=0.2,
            )
    segments = IntProperty(
            name="Segments",
            description="How many subdivisions make up the blade",
            min=1,
            default=5,
            )
    grip_l = FloatProperty(
            name="Grip Length",
            description="How long the grip is",
            min=0.01,
            default=0.2,
            )
    grip_w = FloatProperty(
            name="Grip Width",
            description="How wide the grip is",
            min=0.01,
            default=0.05,
            )
    grip_h = FloatProperty(
            name="Grip Height",
            description="How tall the grip is",
            min=0.01,
            default=0.025,
            )
    grip_seg = IntProperty(
            name="Grip Bevel Segments",
            description="How many bevel segments make up the grip",
            min=0,
            default=3,
            )
    grip_str = FloatProperty(
            name="Grip Bevel Strength",
            description="The strength of the bevel applied to the grip",
            min=0.0,
            default=0.00875,
            )
    grip_prof = FloatProperty(
            name="Grip Bevel Profile",
            description="Controls the bevel's direction",
            min=0.0, 
            max=1.0,
            default=0.5,
            )
    has_hilt = BoolProperty(
            name="Make Hilt",
            description="Whether or not the blade has a hilt",
            default=True,
            )
    hilt_l = FloatProperty(
            name="Hilt Length",
            description="How long the hilt is",
            min=0.01,
            default=0.0125,
            )
    hilt_w = FloatProperty(
            name="Hilt Width",
            description="How wide the hilt is",
            min=0.01,
            default=0.0875,
            )
    hilt_h = FloatProperty(
            name="Hilt Height",
            description="How tall the hilt is",
            min=0.01,
            default=0.05,
            )
    hilt_seg = IntProperty(
            name="Hilt Bevel Segments",
            description="How many bevel segments make up the hilt's length",
            min=0,
            default=3,
            )
    hilt_str = FloatProperty(
            name="Hilt Bevel Strength",
            description="The strength of the bevel applied to the hilt's length",
            min=0.0,
            default=0.005,
            )
    hilt_prof = FloatProperty(
            name="Hilt Bevel Profile",
            description="Controls the bevel's direction",
            min=0.0, 
            max=1.0,
            default=0.5,
            )
    use_curve = BoolProperty(
            name="Apply Selected Curve",
            description="If a curve is the active object, apply the curve to the blade",
            default=True,
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
        col.label(text="Blade", icon="IPO_LINEAR")
        col.prop(self, "length")
        col.prop(self, "width")
        col.prop(self, "shift_l")
        col.prop(self, "shift_r")
        col.prop(self, "height")
        col.prop(self, "point")
        col.prop(self, "segments")
        col.prop(self, "use_curve")
        
        box = layout.box()
        col = box.column()
        col.label(text="Grip", icon="MAN_SCALE")
        col.prop(self, "grip_l")
        col.prop(self, "grip_w")
        col.prop(self, "grip_h")
        col.prop(self, "grip_seg")
        col.prop(self, "grip_str")
        col.prop(self, "grip_prof")
        
        box = layout.box()
        col = box.column()
        col.label(text="Hilt", icon="ZOOMOUT")
        col.prop(self, "has_hilt")
        if self.has_hilt:
            col.prop(self, "hilt_l")
            col.prop(self, "hilt_w")
            col.prop(self, "hilt_h")
            col.prop(self, "hilt_seg")
            col.prop(self, "hilt_str")
            col.prop(self, "hilt_prof")
        
        """
        box = layout.box()
        col = box.column()
        col.label(text="Position", icon="NDOF_TURN")
        col.prop(self, "location")
        col.prop(self, "rotation")"""
    
    def execute(self, context):
        
        #Simplify variable names:
        l = self.length
        w = self.width
        height = self.height
        shift_l = self.shift_l
        shift_r = self.shift_r
        point = self.point
        segments = self.segments
        gripl = self.grip_l
        gripw = self.grip_w
        griph = self.grip_h
        gripseg = self.grip_seg
        gripstr = self.grip_str
        gp = self.grip_prof
        hiltl = self.hilt_l
        hiltw = self.hilt_w
        hilth = self.hilt_h
        hiltseg = self.hilt_seg
        hiltstr = self.hilt_str
        hp = self.hilt_prof
        has_hilt = self.has_hilt
        use_curve = self.use_curve
        
        #Check to see if a curve was selected.
        #If so, store it because it will later
        #be used to modify the blade curvature
        active = bpy.context.scene.objects.active
        curve_sel = False
        if active:
            c_obj = bpy.data.objects[active.name]
            if getattr(c_obj, 'type', '') == 'CURVE':
                if c_obj.select:
                    curve_sel = True
        
        #Define the verts and faces used in
        #the blade part of the sword/knife:
        verts = [(l, +((w / 2.0) + shift_l), +0.0),
                 (l, +(w / 2.0), +(height / 2.0)),
                 (l, -(w / 2.0), +(height / 2.0)),
                 (l, -((w / 2.0) + shift_r), +0.0),
                 (l, -(w / 2.0), -(height / 2.0)),
                 (l, +(w / 2.0), -(height / 2.0)),
                 (0.0, +((w / 2.0) + shift_l), +0.0),
                 (0.0, +(w / 2.0), +(height / 2.0)),
                 (0.0, -(w / 2.0), +(height / 2.0)),
                 (0.0, -((w / 2.0) + shift_r), +0.0),
                 (0.0, -(w / 2.0), -(height / 2.0)),
                 (0.0, +(w / 2.0), -(height / 2.0)),
                 ]

        faces = [(0, 6, 7, 1),
                 (1, 7, 8, 2),
                 (2, 8, 9, 3),
                 (3, 9, 10, 4),
                 (4, 10, 11, 5),
                 (6, 0, 5, 11),
                ]
        
        #Make the blade object stuff:
        mesh = bpy.data.meshes.new("blade")
        blade_obj = bpy.data.objects.new("Blade_Obj", mesh)

        scene = bpy.context.scene
        scene.objects.link(blade_obj)
        bm = bmesh.new()
        
        #Add verts, then faces:
        for v_co in verts:
            bm.verts.new(v_co)

        bm.verts.ensure_lookup_table()
        for f_idx in faces:
            bm.faces.new([bm.verts[i] for i in f_idx])
            
        #Extrude each additional 
        #seg and make the point:
        if segments > 1:
            s = segments
            e_geom = get_e_in_bounds(bm.edges, l, 0.0, 0.0, 0.0001, (w + shift_l + shift_r), height)
            
            for i in range(0, segments):
                ret_geom = bmesh.ops.extrude_edge_only(bm, edges=e_geom)
                e_geom = [e for e in ret_geom["geom"] 
                          if isinstance(e, bmesh.types.BMEdge)]
                v_geom = [v for v in ret_geom["geom"] 
                          if isinstance(v, bmesh.types.BMVert)]
                del ret_geom
                s -= 1
                
                bmesh.ops.translate(bm, verts=v_geom, vec=(l, 0.0, 0.0))
                if s == 0:
                    m_co = ((point + (l * segments)), 0.0, 0.0)
                    #Merge them in the center:
                    bmesh.ops.pointmerge(bm, verts=v_geom, merge_co=m_co)
        else:
            #Otherwise make the point:
            
            #Extrude and merge verts into center:
            e_geom = get_e_in_bounds(bm.edges, (l * segments), 0.0, 0.0, 0.0001, (w + shift_l + shift_r), height)
            ret_geom = bmesh.ops.extrude_edge_only(bm, edges=e_geom)
            v_geom = [v for v in ret_geom["geom"] 
                              if isinstance(v, bmesh.types.BMVert)]
            del ret_geom
            
            m_co = ((point + (l * segments)), 0.0, 0.0)
            #Merge them in the center:
            bmesh.ops.pointmerge(bm, verts=v_geom, merge_co=m_co)
        
        bm.to_mesh(mesh)
        bm.free()
        mesh.update()
        
        #Curve the blade by applying curve mod:
        if curve_sel and use_curve:
            bpy.ops.object.select_all(action='DESELECT')
            blade_obj.select = True
            bpy.context.scene.objects.active = blade_obj
            curve_mod = blade_obj.modifiers.new(name='c_mod', type='CURVE')
            curve_mod.object = c_obj
            bpy.ops.object.modifier_apply(modifier=curve_mod.name)
        
        #Make the grip object stuff:
        mesh1 = bpy.data.meshes.new("grip")
        grip_obj = bpy.data.objects.new("Grip_Obj", mesh1)

        scene = bpy.context.scene
        scene.objects.link(grip_obj)
        
        #Make the grip:
        bm1 = bmesh.new()
        
        #Return a beveled grip:
        if has_hilt:
            gripmov = (((-gripl / 2.0) - hiltl), 0.0, 0.0)
        else:
            gripmov = ((-gripl / 2.0), 0.0, 0.0)
        beveled_box(bm1, gripl, gripw, griph, gripmov, gripseg, gripstr, gp, True)
        
        bm1.to_mesh(mesh1)
        bm1.free()
        mesh1.update()
        
        if has_hilt:
            #Make the hilt object stuff:
            mesh2 = bpy.data.meshes.new("hilt")
            hilt_obj = bpy.data.objects.new("Hilt_Obj", mesh2)

            scene = bpy.context.scene
            scene.objects.link(hilt_obj)
            
            #Make the hilt:
            bm2 = bmesh.new()
            
            #Return a beveled hilt:
            hiltmov = ((-hiltl / 2.0), 0.0, 0.0)
            beveled_box(bm2, hiltl, hiltw, hilth, hiltmov, hiltseg, hiltstr, hp, False)
            
            bm2.to_mesh(mesh2)
            bm2.free()
            mesh2.update()
        
        #Join the grip (, hilt,) and blade:
        bpy.ops.object.select_all(action='DESELECT')
        blade_obj.select = True
        grip_obj.select = True
        if has_hilt:
            hilt_obj.select = True
        bpy.context.scene.objects.active = blade_obj
        bpy.ops.object.join()   
        blade_obj.name = "Blade"

        return {'FINISHED'}

def menu_func(self, context):
    self.layout.operator(AddBlade.bl_idname, icon='IPO_LINEAR')


def register():
    bpy.utils.register_class(AddBlade)
    bpy.types.INFO_MT_mesh_add.append(menu_func)


def unregister():
    bpy.utils.unregister_class(AddBlade)
    bpy.types.INFO_MT_mesh_add.remove(menu_func)

if __name__ == "__main__":
    register()