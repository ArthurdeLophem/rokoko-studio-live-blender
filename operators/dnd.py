import os
import shutil
import bpy


# Legacy FBX importer settings panel for dropped files, without the file browser
class IMPORT_OT_fbx_legacy(bpy.types.IMPORT_SCENE_OT_fbx):
    bl_idname = "import_scene.fbx_legacy_drop"
    bl_label = "Import FBX (Legacy)"
    bl_description = "Import FBX with the legacy importer, including orientation and armature options"
    bl_options = {'UNDO', 'PRESET'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)


# Drag-and-drop of .fbx files into the 3D viewport offers the legacy importer
class IO_FH_fbx_legacy(bpy.types.FileHandler):
    bl_idname = "IO_FH_fbx_legacy"
    bl_label = "FBX (Legacy)"
    bl_import_operator = IMPORT_OT_fbx_legacy.bl_idname
    bl_file_extensions = ".fbx"

    @classmethod
    def poll_drop(cls, context):
        return context.area and context.area.type == "VIEW_3D"


classes = (IMPORT_OT_fbx_legacy, IO_FH_fbx_legacy)


# Templates are stored per operator, so copy the legacy importer's templates to the drop importer once
def sync_legacy_presets():
    source = bpy.utils.user_resource('SCRIPTS', path=os.path.join('presets', 'operator', 'import_scene.fbx'))
    target = bpy.utils.user_resource('SCRIPTS', path=os.path.join('presets', 'operator', IMPORT_OT_fbx_legacy.bl_idname), create=True)
    if not os.path.isdir(source):
        return

    for name in os.listdir(source):
        if name.endswith('.py') and not os.path.exists(os.path.join(target, name)):
            shutil.copy2(os.path.join(source, name), os.path.join(target, name))
