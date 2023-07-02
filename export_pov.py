import os
import bpy
from bpy_extras.io_utils import ExportHelper
from bpy.props import (BoolProperty,
    FloatProperty,
    StringProperty,
    EnumProperty,
    )

bl_info = {
    "name": "POV-Ray Mesh Exporter",
    "author": "Jonathan S.",
    "version": (1, 0, 0),
    "blender": (3, 5, 0),
    "category": "Import-Export",
    "location": "File > Export",
    "description": "Mesh exporter for the POV-Ray renderer. Exports to a .inc file with automatic mesh declaration based on object name."
}


class ExportPOV(bpy.types.Operator, ExportHelper):
    """Export mesh to POV-Ray .inc file"""
    bl_idname = "export_mesh.pov"
    bl_label = "Export POV-Ray Mesh"

    filename_ext = ".inc"
    filter_glob: StringProperty(
        default="*.inc;*.pov",
        options={'HIDDEN'},
    )

    check_extension = True


    meshname: StringProperty(
        name="Mesh Name (leave blank to use object name)",
        description="What to name the mesh variable. Follow standard code formatting- don't use spaces. Leave blank to use object's name",
        default=""
    )

    color_r: FloatProperty(
        name="R",
        min=0.0, max=1.0,
        default=1.0,
    )
    color_g: FloatProperty(
        name="G",
        min=0.0, max=1.0,
        default=1.0,
    )
    color_b: FloatProperty(
        name="B",
        min=0.0, max=1.0,
        default=1.0,
    )

    f_diffuse: FloatProperty(
        name="Diffuse",
        min=0.0, max=1.0,
        default=0.7,
    )
    f_brilliance: FloatProperty(
        name="Brilliance",
        min=0.0, max=1.0,
        default=0.0,
    )
    f_phong: FloatProperty(
        name="Phong",
        min=0.0, max=1.0,
        default=1.0,
    )
    f_specular: FloatProperty(
        name="Specular",
        min=0.0, max=1.0,
        default=0.0,
    )
    f_reflection: FloatProperty(
        name="Reflection",
        min=0.0, max=1.0,
        default=0.0,
    )


    def execute(self, context):
        keywords = self.as_keywords(ignore=(
            'filter_glob',
            'check_existing',
        ))

        return save(self, context, **keywords)

    # disable drawing of properties by default, so it only happens in the POV_PT_export_* classes
    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        sfile = context.space_data
        operator = sfile.active_operator

        layout.prop(operator, 'meshname')


#####v PROPERTY GROUPING v#####

# color grouping
class POV_PT_export_color(bpy.types.Panel):
    bl_space_type = 'FILE_BROWSER'
    bl_region_type = 'TOOL_PROPS'
    bl_label = "Texture Color"
    bl_parent_id = "FILE_PT_operator"

    @classmethod
    def poll(cls, context):
        sfile = context.space_data
        operator = sfile.active_operator

        return operator.bl_idname == "EXPORT_MESH_OT_pov"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        sfile = context.space_data
        operator = sfile.active_operator

        layout.prop(operator, 'color_r')
        layout.prop(operator, 'color_g')
        layout.prop(operator, 'color_b')

# finish grouping
class POV_PT_export_finish(bpy.types.Panel):
    bl_space_type = 'FILE_BROWSER'
    bl_region_type = 'TOOL_PROPS'
    bl_label = "Finish Options"
    bl_parent_id = "FILE_PT_operator"
    #bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        sfile = context.space_data
        operator = sfile.active_operator

        return operator.bl_idname == "EXPORT_MESH_OT_pov"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        sfile = context.space_data
        operator = sfile.active_operator

        layout.prop(operator, 'f_diffuse')
        layout.prop(operator, 'f_brilliance')
        layout.prop(operator, 'f_phong')
        layout.prop(operator, 'f_specular')
        layout.prop(operator, 'f_reflection')

#####^ PROPERTY GROUPING ^#####


def menu_func_export(self, context):
    self.layout.operator(ExportPOV.bl_idname, text="POV-Ray Mesh (.inc)")


classes = (
    ExportPOV,
    POV_PT_export_color,
    POV_PT_export_finish,
)


def register():
    for c in classes:
        bpy.utils.register_class(c)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)
def unregister():
    for c in reversed(classes):
        bpy.utils.unregister_class(c)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)



def save(operator, context, filepath, 
         meshname= "",
         color_r= 1.0,
         color_g= 1.0,
         color_b= 1.0,
         f_diffuse= 0.7,
         f_brilliance= 0.0, 
         f_phong= 1.0, 
         f_specular= 0.0, 
         f_reflection= 0.0,
        ):

    obj = context.object # bpy.context.object

    filepath = os.fsencode(filepath)
    fp = open(filepath, 'w')

    if (meshname == ""):
        meshname = obj.name


    # make dictionary where key is index and value is vertex
    index2vert = {}
    for vert in obj.data.vertices:
        index2vert[vert.index] = vert


    fp.write("#declare " + meshname + " = mesh {\n") # BEGIN MESH

    # loop through triangles in mesh and write each tri definition to file
    for tri in obj.data.loop_triangles: 
        fp.write(process_tri(tri, index2vert))

    # set default material:
    fp.write("\n")
    fp.write("\ttexture{{ pigment{{ color rgb< {r}, {g}, {b}> }}\n".format(r= round(color_r, 2), g= round(color_g, 2), b= round(color_b, 2)))
    
    #fp.write("\t\tfinish { phong 1 }\n")
    fp.write(process_finishes(f_diffuse, f_brilliance, f_phong, f_specular, f_reflection))

    fp.write("\t}\n")
    
    fp.write("\n")
    # rotate because blender and pov ray use different coordinate spaces
    # this is a bit of a hack because i think there are more formal ways to do this?
    # https://imgur.com/a/EpgyiSX
    fp.write("\trotate <{rotx}, {roty}, {rotz}>\n".format(rotx= 0, roty= 180, rotz= 180)) 
    fp.write("};\n") # END MESH


    fp.close()
    return {'FINISHED'}

# take in a triangle object and return its vertex coordinates as a POV trangle{} string
def process_tri(tri: bpy.types.MeshLoopTriangle, index2vert: dict):
    # temp string to hold finished triangle definition
    tri_definition = "" 

    tri_definition+= "\ttriangle { " # BEGIN TRIANGLE
        
    # list of this triangle's vertex coordinates in format <x, y, z>
    tri_verts_coords = []
    
    for index in tri.vertices:
        # get this vertex's coordinates
        vert_co = index2vert[index].co

        # format this vertex's coordinates to a list of floats with .0000 accuracy
        coords = [str("{:.4f}".format(coord)) for coord in vert_co]
        # format the list of floats to <x, y, z> a format string. add to list
        tri_verts_coords.append("<" + ", ".join( coords ) + ">")

        
    tri_definition+= ", ".join(tri_verts_coords)  # write the tri coords separated by commas
    tri_definition+= " }\n" # END TRIANGLE

    return tri_definition

# take in finish properties and return them as a POV-Ray SDL string
def process_finishes(f_diffuse= 0.7, 
                     f_brilliance= 0.0, 
                     f_phong= 1.0, 
                     f_specular= 0.0, 
                     f_reflection= 0.0,
                    ):
    finish_def = "\t\tfinish {\n"

    if (f_diffuse > 0.0):
        finish_def+=("\t\t\tdiffuse "+ str(round(f_diffuse, 2)) + "\n")

    if (f_brilliance > 0.0):
        finish_def+=("\t\t\tbrilliance "+ str(round(f_brilliance, 2)) + "\n")

    if (f_phong > 0.0):
        finish_def+=("\t\t\tphong "+ str(round(f_phong, 2)) + "\n")

    if (f_specular > 0.0):
        finish_def+=("\t\t\tspecular "+ str(round(f_specular, 2)) + "\n")

    if (f_reflection > 0.0):
        finish_def+=("\t\t\treflection "+ str(round(f_reflection, 2)) + "\n")

    finish_def+=("\t\t}\n")
    return finish_def


if __name__ == "__main__":
    register()

