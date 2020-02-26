bl_info = {
    "name": "Building Generator",
    "description": "Generate Buildings at the push of a button",
    "author": "Austin Jacob",
    "version": (0, 4, 0),
    "blender": (2, 79, 0),
    "location": "View3D > Add > Mesh",
    "warning": "", # used for warning icon and text in addons panel
    "wiki_url": "",
    "tracker_url": "",
    "category": "Add Mesh"}

import bpy
import random
from datetime import datetime
from . import door_add, window_add, operator_structure_add

from bpy.props import (
        BoolProperty,
        BoolVectorProperty,
        FloatProperty,
        FloatVectorProperty,
        EnumProperty,
        IntProperty,
        )


class AddBuilding(bpy.types.Operator):
    """Add a building"""
    bl_idname = "mesh.building_add"
    bl_label = "Add Building"
    bl_options = {'REGISTER', 'UNDO'}

    length = FloatProperty(
            name="Length",
            description="Maximum length of the building",
            min=4.0,
            default=10.0,
            )
    width = FloatProperty(
            name="Width",
            description="Maximum width of the building",
            min=4.0,
            default=10.0,
            )
    floor_ceil_dist = FloatProperty(
            name="Floor height",
            description="Height of each floor",
            min=4.0,
            default=10.0,
            )
    floors = IntProperty(
            name="Floors",
            description="Number of floors",
            min=1,
            default=1,
            )
    structures = IntProperty(
            name="Number of Structures",
            description="The number of structures that make up the building",
            min=1,
            default=4,
            )
    rseed = IntProperty(
            name="Random Seed",
            description="Provide your own int as the random seed",
            default = 0,
            )
    time_seed = BoolProperty(
            name="Use Time For Seed",
            description="Use time instead of an int for the random seed",
            default=True
            )
    randomize_values = BoolProperty(
            name="Randomize All",
            description="Randomize all above parameters",
            default=False
            )
    location = FloatVectorProperty(
            name="Location",
            subtype='TRANSLATION',
            )
    rotation = FloatVectorProperty(
            name="Rotation",
            subtype='EULER',
            )
    #EnumProperty for building presets, like apartment/hotel, gas station, store, warehouse, etc.
    
    def draw(self, context):
        
        #Randomize values if they need
        #to be randomized, before they
        #are all displayed in the menu
        if self.time_seed:
            random.seed(datetime.now())
        else:
            random.seed(self.rseed)
        
        if self.randomize_values == True:
            self.length = ((round(((random.random() * 50) + 4)), 2))
            self.width = ((round(((random.random() * 50) + 4)), 2))
            self.floor_ceil_dist = ((round(((random.random() * 1) + 2.5)), 2))
            self.structures = random.randint(1, 6)
            #Many buildings are only 1 floor so this'll
            #need a bias for buildings that are smaller
            floor_bias = random.choice([1, 2, 3,]) #3 is anything larger than 1 or 2 floors
            if floor_bias == 1:
                self.floors = 1
            elif floor_bias == 2:
                self.floors = 2
            else:
                self.floors = random.randint(1, 15)
        
        layout = self.layout
        
        box = layout.box()
        col = box.column()
        col.label(text="Dimensions", icon="MOD_BUILD")
        col.prop(self, "length")
        col.prop(self, "width")
        col.prop(self, "floors")
        col.prop(self, "floor_ceil_dist")
        col.prop(self, "structures")
        
        box = layout.box()
        col = box.column()
        col.label(text="Placement", icon="NDOF_TURN")
        col.prop(self, "location")
        col.prop(self, "rotation")
        
        box = layout.box()
        col = box.column()
        col.label(text="Randomization", icon="QUESTION")
        col.prop(self, "randomize_values")
        col.prop(self, "time_seed")
        col.prop(self, "rseed")
        
        
    def execute(self, context):
        
        #rename variables to something easier:
        l = self.length
        w = self.width
        f = self.floors
        fcd = self.floor_ceil_dist
        s = structures
        loc = self.location
        rot = self.rotation
        
        #Determine the locations and bounds of each structure:
        
        return {'FINISHED'}


def menu_func(self, context):
    self.layout.operator(AddBuilding.bl_idname, icon='MOD_BUILD')

def register():
    bpy.utils.register_module(__name__)

def unregister():
    bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
    register()