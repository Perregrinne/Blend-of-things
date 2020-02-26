import bpy
import bmesh
import math

#ADDON WILL CURRENTLY RUN!
#TODO: https://blender.stackexchange.com/questions/643/is-it-possible-to-create-image-data-and-save-to-a-file-from-a-script
#Sync bmesh selection with UV selection, then select all base faces
#Import your selection methods from other scripts to get the selection methods, if you need them
#Create the image based off of the texture sizes (texture_w, texture_h)
#Fill the entire image with the basic orange color (color1)
#make another method that determines the highest x, smallest x, highest y, and lowest y (of the selected UV coordinates) and
#then make a square of color3 that completely covers all selected UV coordinates
#Deselect all
#Try to select each exterior face of the cone, one at a time
#Put all stripes (if any) 3/4 of the way up the face.
#MAKE SURE YOU MAKE AN ALBEDO MAP, ROUGHNESS MAP, AND METAL MAP

#bpy.context.scene.render.engine = 'CYCLES'

def get_dist(a, b):
    
    #Break a and b into
    #6 simple variables
    x1 = a[0]
    y1 = a[1]
    z1 = a[2]
    
    x2 = b[0]
    y2 = a[1]
    z2 = a[2]
    
    #Do the distance formula
    #and return the results:
    return math.sqrt((((x2 - x1)**2) + ((y2 - y1)**2) + ((z2 - z1)**2)))
    

from bpy.props import (
        BoolProperty,
        BoolVectorProperty,
        FloatProperty,
        FloatVectorProperty,
        IntProperty,
        EnumProperty,
        )


class AddTrafficCone(bpy.types.Operator):
    bl_idname = "mesh.primitive_traffic_cone_add"
    bl_label = "Add Traffic Cone"
    bl_options = {'REGISTER', 'UNDO'}

    radius1 = FloatProperty(
            name="Upper Cone Radius",
            description="Radius of the top of the cone",
            min=0.01,
            default=0.175,
            )
    radius2 = FloatProperty(
            name="Lower Cone Radius",
            description="Radius of the bottom of the cone",
            min=0.01,
            default=0.75,
            )
    coneh = FloatProperty(
            name="Cone Height",
            description="How tall the cone is",
            min=0.01,
            default=2.0,
            )
    cones = IntProperty(
            name="Cone Segments",
            description="How many segments make up the cone",
            min=3,
            default=32,
            )
    basew = FloatProperty(
            name="Base Width",
            description="Width of the base of the cone",
            min=0.01,
            default=2.0,
            )
    thick = FloatProperty(
            name="Thickness",
            description="Thickness of the cone",
            min=0.01,
            default=0.05,
            )
    color1 = FloatVectorProperty(
            name="Cone Color",
            description="What color to make the cone",
            default=(0.75, 0.125, 0.0),
            subtype='COLOR',
            )
    color2 = FloatVectorProperty(
            name="Stripe Color",
            description="What color to make the reflective stripes on the cone",
            default=(0.8, 0.8, 0.8),
            subtype='COLOR',
            )
    color3 = FloatVectorProperty(
            name="Base Color",
            description="What color to make the base of the cone",
            default=(0.05, 0.05, 0.05),
            subtype='COLOR',
            )
    stripes = IntProperty(
            name="Cone Stripes",
            description="How many reflective stripes on the cone",
            min=0,
            default=2,
            max=2,
            )
    texture_w = IntProperty(
            name="X:",
            description="Width of the texture",
            min=1,
            default=2048,
            )
    texture_h = IntProperty(
            name="Y:",
            description="Height of the texture",
            min=1,
            default=2048,
            )
    col_mesh = EnumProperty(
            name="Collision Mesh",
            description="Collision mesh to generate for the object",
            items=(('BOX', 'Box', 'A simple box'),
                ('TIGHT', 'Tight Box', 'A box that better matches the mesh'),
                ('SIMPLE', 'Simple', 'A simple mesh that tightly matches the bounds'),
                ('NONE', 'None', 'Do not generate collision for this object')),
            default='SIMPLE',
            )
    engine_type = EnumProperty(
            name="Game Engine",
            description="Which engine this will be exported to (Unity if unsure)",
            items=(('UNITY', 'Unity', 'For the Unity Game Engine or any other engines'),
                ('UNREAL', 'Unreal', 'For Unreal Engine 4')),
            default='UNITY',
            )
    vis = BoolProperty(
            name="Hide Collision",
            description="Toggles the visibility of the collision mesh",
            default=True,
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
        col.label(text="Cone", icon="MESH_CONE")
        col.prop(self, "coneh")
        col.prop(self, "cones")
        col.prop(self, "radius1")
        col.prop(self, "radius2")
        
        box = layout.box()
        col = box.column()
        col.label(text="Base", icon="MESH_CUBE")
        col.prop(self, "basew")
        col.prop(self, "thick")
        
        box = layout.box()
        col = box.column()
        col.label(text="Color", icon="COLOR")
        col.prop(self, "color1")
        col.prop(self, "color3")
        col.prop(self, "color2")
        col.prop(self, "stripes")
        col.label(text="Resolution:")
        col.prop(self, "texture_w")
        col.prop(self, "texture_h")
        
        box = layout.box()
        col = box.column()
        col.label(text="Collision", icon="MOD_PHYSICS")
        col.prop(self, "col_mesh")
        col.prop(self, "engine_type")
        col.prop(self, "vis")
    
    def execute(self, context):
        
        coneh = self.coneh
        cones = self.cones
        radius1 = self.radius1
        radius2 = self.radius2
        basew = (self.basew / 2.0)
        thick = self.thick
        color1 = self.color1
        color2 = self.color2
        stripes = self.stripes
        col = self.col_mesh
        eng = self.engine_type
        vis = self.vis
        texture_w = self.texture_w
        texture_h = self.texture_h
        
        verts = [(+basew, +basew, 0.0),
                 (+basew, -basew, 0.0),
                 (-basew, -basew, 0.0),
                 (-basew, +basew, 0.0),
                 (+basew, +basew, thick),
                 (+basew, -basew, thick),
                 (-basew, -basew, thick),
                 (-basew, +basew, thick),
                ]

        faces = [(0, 1, 2, 3),
                 (4, 7, 6, 5),
                 (0, 4, 5, 1),
                 (1, 5, 6, 2),
                 (2, 6, 7, 3),
                 (4, 0, 3, 7),
                ]
        
        mesh1 = bpy.data.meshes.new("cone_base")
        cone_base_obj = bpy.data.objects.new("Cone_Base_Obj", mesh1)

        scene = bpy.context.scene
        scene.objects.link(cone_base_obj)
        
        bm = bmesh.new()
        for v in verts:
            bm.verts.new(v)
        
        bm.verts.ensure_lookup_table()
        for f_idx in faces:
            bm.faces.new([bm.verts[i] for i in f_idx])
        bm.to_mesh(mesh1)
        mesh1.update()
        
        mesh2 = bpy.data.meshes.new("cone_cone")
        cone_cone_obj = bpy.data.objects.new("Cone_Cone_Obj", mesh2)

        scene = bpy.context.scene
        scene.objects.link(cone_cone_obj)
        
        #Make the cone bmesh:
        bm = bmesh.new()
        bmesh.ops.create_cone(bm, cap_ends=False, cap_tris=False, segments=cones, diameter1=radius2, diameter2=radius1, depth=coneh, calc_uvs=True)
        
        #Move verts up by (coneh / 2.0) + thick
        bmesh.ops.translate(bm, vec=(0.0, 0.0, ((coneh / 2.0) + thick)), verts=bm.verts)
        
        #Smooth all faces:
        for face in bm.faces:
            face.smooth = True
        
        bm.to_mesh(mesh2)
        mesh2.update()
        
        #Solidify the empty cone
        bpy.context.scene.objects.active = cone_cone_obj
        cone_cone_obj.data = cone_cone_obj.data.copy()
        solid = cone_cone_obj.modifiers.new("solid", type='SOLIDIFY')
        solid.edge_crease_rim = 1.0
        solid.thickness = thick
        bpy.ops.object.modifier_apply(apply_as='DATA', modifier=solid.name)
        bpy.ops.object.select_all(action='DESELECT')
        
        #Make the object that gets cut out of cone_base:
        mesh3 = bpy.data.meshes.new("cone_cutout")
        cone_cutout_obj = bpy.data.objects.new("Cone_Cutout_Obj", mesh3)

        scene = bpy.context.scene
        scene.objects.link(cone_cutout_obj)
        
        bm = bmesh.new()
        bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=cones, diameter1=(radius2 - thick), diameter2=(radius2 - thick), depth=(thick + 0.25), calc_uvs=True)
        #Move cutout up by thick / 2.0 (cutout is slightly larger than the base to ensure a proper boolean)
        bmesh.ops.translate(bm, vec=(0.0, 0.0, (thick / 2.0)), verts=bm.verts)
        
        #Smooth all faces:
        for face in bm.faces:
            face.smooth = True
        
        bm.to_mesh(mesh3)
        mesh3.update()
        
        cone_cutout_obj.data = cone_cutout_obj.data.copy()
        
        #Cut cone_cutout out of cone_base:
        bpy.context.scene.objects.active = cone_base_obj
        cone_base_obj.data = cone_base_obj.data.copy()
        cut = cone_base_obj.modifiers.new("cut_hole", type='BOOLEAN')
        cut.operation = 'DIFFERENCE'
        cut.object = cone_cutout_obj
        bpy.ops.object.modifier_apply(apply_as='DATA', modifier=cut.name)
        bpy.ops.object.select_all(action='DESELECT')
        cone_cutout_obj.select = True
        bpy.ops.object.delete()
        
        #Join cone_base and cone_cone and rename it Traffic_Cone
        cone_base_obj.select = True
        cone_cone_obj.select = True
        bpy.context.scene.objects.active = cone_base_obj
        bpy.ops.object.join()
        context.active_object.name = 'Traffic_Cone'
        
        #Generate UVs
        bpy.ops.object.mode_set(mode='EDIT')
        bmCone = bmesh.from_edit_mesh(context.object.data)
        
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.uv.smart_project(angle_limit=66.0, island_margin=0.125, user_area_weight=0.0, use_aspect=True, stretch_to_bounds=False)

        bmesh.update_edit_mesh(context.active_object.data)
        bpy.ops.object.mode_set(mode='OBJECT')
        
        #Cone material
        material = bpy.data.materials.get("Material")
        if material is None:
            # create material
            material = bpy.data.materials.new(name="Cone_Mat")

        # Assign it to object
        if bpy.context.active_object.data.materials:
            # assign to 1st material slot
            bpy.context.active_object.data.materials[0] = material
        else:
            # no slots
            bpy.context.active_object.data.materials.append(material)
        
        material1 = bpy.context.active_object.data.materials[0]
        material1.diffuse_color = color1
        
        #EXPERIMENTAL----------------------
        #
        #
        #
        #Make the albedo, metallic, and roughness maps:
        albedo_image = bpy.data.images.new("Traffic_Cone_Albedo", width=texture_w, height=texture_h)
        metallic_image = bpy.data.images.new("Traffic_Cone_Metallic", width=texture_w, height=texture_h)
        roughness_image = bpy.data.images.new("Traffic_Cone_Roughness", width=texture_w, height=texture_h)
        
        #albedo colors (color1)
        r_alb = color1[0]
        g_alb = color1[1]
        b_alb = color1[2]
        a_alb = 1.0
        #Metallic colors (All black for now)
        #Only the stripes would be metallic.
        r_met = 0.0
        g_met = 0.0
        b_met = 0.0
        a_met = 1.0
        #Roughness colors (Completely rough)
        r_rough = 1.0
        g_rough = 1.0
        b_rough = 1.0
        a_rough = 1.0
        
        albedo_map = [None] * texture_w * texture_h
        metallic_map = [None] * texture_w * texture_h
        roughness_map = [None] * texture_w * texture_h
        
        for x in range(texture_w):
            for y in range(texture_h):
                #Fill the albedo map with color1
                albedo_map[(y * texture_w) + x] = [r_alb, g_alb, b_alb, a_alb]
                #Fill the metallic map:
                metallic_map[(y * texture_w) + x] = [r_met, g_met, b_met, a_met]
                #Fill the roughness map:
                roughness_map[(y * texture_w) + x] = [r_rough, g_rough, b_rough, a_rough]
        
        #Figure out the locations for the
        #stripe (if any) on the textures:
        if stripes > 0:
            #Sync mesh selection to UV selection
            bpy.data.scenes["Scene"].tool_settings.use_uv_select_sync = True
            
            #List of selected UV coordinates:
            uv_x_list = []
            uv_y_list = []
            
            bpy.ops.object.mode_set(mode='EDIT')
            bm = bmesh.from_edit_mesh(context.active_object.data)
            
            uv_layer = bm.loops.layers.uv.verify()
            bm.faces.layers.tex.verify()  #Currently, Blender needs both layers.
            
            #Deselect everything so that no
            #UV verts or faces are selected
            bpy.ops.mesh.select_all(action='DESELECT')
            
            #keep track of all stripe vertices
            #on the outside faces of the cone:
            for f in bm.faces:
                #Every one of the cone faces
                #has only exactly 4 vertices
                #so ignore faces that don't:
                if len(f.verts) == 4:
                    #If the vert's distance from
                    #the cone's center = radius1 
                    #or radius2, and all 4 verts
                    #are equal to either radius,
                    #then give the face a stripe
                    
                    #The cone faces needed
                    #all have a top-right,
                    #top-left, bottom-left
                    #and bottom-right vert
                    top = []
                    bottom = []
                    
                    matches = 0
                    for v in f.verts:
                        #The floats somehow lost 
                        #accuracy so round them:
                        #x = round(v.co.x, 3)
                        #y = round(v.co.y, 3)
                        #z = round(v.co.z, 3)
                        #t = round(thick, 3)
                        #c = round(coneh, 3)
                        #b = round(basew, 3)
                        dist1 = get_dist((v.co.x, v.co.y, v.co.z), (0.0, 0.0, thick + coneh))
                        #print(dist1)
                        dist2 = get_dist((v.co.x, v.co.y, v.co.z), (0.0, 0.0, thick))
                        #print(dist2)
                        if dist1 <= radius1 + 0.0125 and dist1 >= radius1 - 0.0125:
                            top += [v]
                            v.select = True
                            matches += 1
                            #print("Upper")
                        elif dist2 <= radius2 + 0.0125 and dist2 >= radius2 - 0.0125:
                            bottom += [v]
                            v.select = True
                            matches += 1
                            #print("Lower")
                        #Needs 4 matches, 2 up top, 2 down below:
                        if matches == 4 and len(bottom) == 2 and len(top) == 2:
                            print("Found one.")
                            #And move on with getting their coords...
                            
                    #Now deselect any selected verts:
                    for v in f.verts:
                        v.select = False
                        
                            
            """for v in bm.verts:
                #The floats somehow lost 
                #accuracy so round them:
                x = round(v.co.x, 3)
                y = round(v.co.y, 3)
                z = round(v.co.z, 3)
                t = round(thick, 3)
                c = round(coneh, 3)
                b = round(basew, 3)
                
                #If z is as tall as the bottom
                #of the cone or as tall as the
                #base plus cone's height then:
                if z == t or z == (c + t):
                    #Just a quick note, the inner
                    #thickness of the cone is not
                    #level with the outside, so z
                    #cannot be equal to t or t+c.
                    
                    #If v.co.x is not a vert
                    #found in the base then:
                    if x < b and x > -b and y < b and y > -b:
                        v.select = True
                        print("Hi")
                        
                        
                        
                        
                        #"Go through vertices, then go through faces, and during that, go through loops?"
                        #None of this makes sense, so rewrite it.
                        for f in bm.faces:
                            for l in f.loops:
                                luv = l[uv_layer]
                                if luv.select:
                                    # get the uv location
                                    uv_x_list += luv.uv.x
                                    uv_y_list += luv.uv.y
                                    print("sdf")"""
                        
        bmesh.update_edit_mesh(context.active_object.data)
        bpy.ops.object.mode_set(mode='OBJECT')
        
        #Finalize the images and save them as PNG files:--------------------------------------------------------
        
        #Flatten Each image
        albedo_map = [channels for pixel in albedo_map for channels in pixel]
        metallic_map = [channels for pixel in metallic_map for channels in pixel]
        roughness_map = [channels for pixel in roughness_map for channels in pixel]
        
        #Dump each map's pixels into their respective image
        albedo_image.pixels = albedo_map
        metallic_image.pixels = metallic_map
        roughness_image.pixels = roughness_map
        
        #Save the albedo map as a PNG:
        albedo_image.filepath_raw = "C:/Users/Austin/Desktop/traffic_cone_albedo.png"
        albedo_image.file_format = 'PNG'
        albedo_image.save()
        
        #Save the metallic map as a PNG:
        metallic_image.filepath_raw = "C:/Users/Austin/Desktop/traffic_cone_metallic.png"
        metallic_image.file_format = 'PNG'
        metallic_image.save()
        
        #Save the roughness map as a PNG:
        roughness_image.filepath_raw = "C:/Users/Austin/Desktop/traffic_cone_roughness.png"
        roughness_image.file_format = 'PNG'
        roughness_image.save()
        #
        #
        #---------------------------------------------------------------------------
        
        #Create the cone albedo texture:
        #albedo = bpy.data.images.new(name='Traffic_Cone_Albedo', width=texture_w, height=texture_h)
        
        #albedo = bpy.data.textures.new("Cone_Albedo", 'IMAGE')
        #slot = material1.texture_slots.add()
        #slot.texture = albedo
        
        #Generate collision mesh:
        #Name the collision mesh based off of what engine will be used
        if col != 'NONE':
            if eng == 'UNITY':
                col_name = context.active_object.name + "_collision_00"
            elif eng == 'UNREAL':
                col_name = "UCX_" + context.active_object.name + "_00"
            
            col_verts = []
            col_faces = []
        
            #Set up the list of verts and faces that make up the collision mesh        
            if col == 'BOX':
            
                col_verts = [(+basew, +basew, 0.0),
                             (+basew, -basew, 0.0),
                             (-basew, -basew, 0.0),
                             (-basew, +basew, 0.0),
                             (+basew, +basew, thick + coneh),
                             (+basew, -basew, thick + coneh),
                             (-basew, -basew, thick + coneh),
                             (-basew, +basew, thick + coneh),
                            ]

                col_faces = [(0, 1, 2, 3),
                             (4, 7, 6, 5),
                             (0, 4, 5, 1),
                             (1, 5, 6, 2),
                             (2, 6, 7, 3),
                             (4, 0, 3, 7),
                            ]
                        
            elif col == 'TIGHT':
                col_verts = [(+basew, +basew, 0.0),
                             (+basew, -basew, 0.0),
                             (-basew, -basew, 0.0),
                             (-basew, +basew, 0.0),
                             (+radius1, +radius1, thick + coneh),
                             (+radius1, -radius1, thick + coneh),
                             (-radius1, -radius1, thick + coneh),
                             (-radius1, +radius1, thick + coneh),
                            ]

                col_faces = [(0, 1, 2, 3),
                             (4, 7, 6, 5),
                             (0, 4, 5, 1),
                             (1, 5, 6, 2),
                             (2, 6, 7, 3),
                             (4, 0, 3, 7),
                            ]
                            
            elif col == 'SIMPLE':
                col_verts = [(+basew, +basew, 0.0),
                             (+basew, -basew, 0.0),
                             (-basew, -basew, 0.0),
                             (-basew, +basew, 0.0),
                             (+basew, +basew, thick),
                             (+basew, -basew, thick),
                             (-basew, -basew, thick),
                             (-basew, +basew, thick),
                             (+radius2, +radius2, thick),
                             (+radius2, -radius2, thick),
                             (-radius2, -radius2, thick),
                             (-radius2, +radius2, thick),
                             (+radius1, +radius1, thick + coneh),
                             (+radius1, -radius1, thick + coneh),
                             (-radius1, -radius1, thick + coneh),
                             (-radius1, +radius1, thick + coneh),
                            ]

                col_faces = [(0, 1, 2, 3),
                             (0, 4, 5, 1),
                             (1, 5, 6, 2),
                             (2, 6, 7, 3),
                             (4, 0, 3, 7),
                             (4, 8, 11, 7),
                             (5, 9, 8, 4),
                             (6, 10, 9, 5),
                             (7, 11, 10, 6),
                             (9, 13, 12, 8),
                             (10, 9, 13, 14),
                             (11, 10, 14, 15),
                             (8, 12, 15, 11),
                             (12, 13, 14, 15),
                            ]
                        
            #Dump those verts and faces into the new collision mesh
            col_mesh = bpy.data.meshes.new("col_mesh")
            cone_col_obj = bpy.data.objects.new(col_name, col_mesh)

            scene = bpy.context.scene
            scene.objects.link(cone_col_obj)
            
            bm_col = bmesh.new()
            
            for v_co in col_verts:
                bm_col.verts.new(v_co)
            
            bm_col.verts.ensure_lookup_table()
            for f_idx in col_faces:
                bm_col.faces.new([bm_col.verts[i] for i in f_idx])
            
            bm_col.to_mesh(col_mesh)
            col_mesh.update()
        
            #Hide collision mesh:
            bpy.data.objects[cone_col_obj.name].hide = vis

        return {'FINISHED'}


def menu_func(self, context):
    self.layout.operator(AddTrafficCone.bl_idname, icon='MESH_CONE')


def register():
    bpy.utils.register_class(AddTrafficCone)
    bpy.types.INFO_MT_mesh_add.append(menu_func)


def unregister():
    bpy.utils.unregister_class(AddTrafficCone)
    bpy.types.INFO_MT_mesh_add.remove(menu_func)

if __name__ == "__main__":
    register()

    # test call
    #bpy.ops.mesh.primitive_traffic_cone_add()
