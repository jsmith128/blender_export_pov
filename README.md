# blender_export_pov
Simple Blender addon for exporting objects into a POV-Ray `mesh{}`.

<br>

To use, simply install the addon, select a mesh in blender, then go to `File > Export > POV-Ray Mesh (.inc)` and then export. It will only export the selected object.  

Once you have your .inc file, you can use the `#include` statement in POV-Ray to include the file. Check what the object is called in the .inc file, and then write `object{~name~}` to use it in your scene.

<br>

The addon will automatically `#declare` the mesh with a variable name determined by the name of the object in blender, or one you specify. The script will not format the name properly at the moment, so if there's spaces it won't work without manual effort.

<br>

Supports simple RGB coloring, and *very* simple finishes. It's best for short-term use right now. 

No support for `smooth_triangle{}`s (yet?).  
No support for textures or multiple objects at a time.  
