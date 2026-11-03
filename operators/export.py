import re
import bpy
import bpy_extras

from ..core import utils

EXPORT_COLLECTION_NAME = 'export'
EXPORT_RIG_NAME = 'Bip001'


def get_export_collection(scene):
    # Blender adds .001, .002 etc. to duplicate collection names, so accept those suffixes too
    pattern = re.compile(re.escape(EXPORT_COLLECTION_NAME) + r'(\.\d{3,})?', re.IGNORECASE)
    for collection in scene.collection.children_recursive:
        if pattern.fullmatch(collection.name):
            return collection
    return None


class ExportRig(bpy.types.Operator, bpy_extras.io_utils.ExportHelper):
    bl_idname = "rsl.export_rig"
    bl_label = "Export Rig"
    bl_description = "Exports the rig in the Export collection as FBX, renamed to Bip001, for use in Unity"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    filename_ext = ".fbx"
    filter_glob: bpy.props.StringProperty(default='*.fbx;', options={'HIDDEN'})

    def execute(self, context):
        collection = get_export_collection(context.scene)
        if not collection:
            self.report({'ERROR'}, f'No collection named "{EXPORT_COLLECTION_NAME}" found!'
                                   '\nMove the rig into that collection first.')
            return {'CANCELLED'}

        objects = list(collection.all_objects)
        armatures = [obj for obj in objects if obj.type == 'ARMATURE']
        meshes = [obj for obj in objects if obj.type == 'MESH']

        if len(armatures) != 1:
            self.report({'ERROR'}, f'The "{EXPORT_COLLECTION_NAME}" collection must contain exactly one armature,'
                                   f' found {len(armatures)}.')
            return {'CANCELLED'}

        armature = armatures[0]

        export_types = set(context.scene.rsl_export_object_types)
        export_objects = ([armature] if 'ARMATURE' in export_types else []) + (meshes if 'MESH' in export_types else [])
        if not export_objects:
            self.report({'ERROR'}, 'Select at least one object type to export.')
            return {'CANCELLED'}

        if context.object and context.object.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')

        has_animation = bool(armature.animation_data and armature.animation_data.action)

        # Another object in the file may already use the export name. Rename it temporarily so the file stays unchanged
        original_name = armature.name
        conflicting = bpy.data.objects.get(EXPORT_RIG_NAME)
        if conflicting and conflicting != armature:
            conflicting.name = EXPORT_RIG_NAME + '_rsl_temp'
        else:
            conflicting = None

        armature.name = EXPORT_RIG_NAME
        try:
            bpy.ops.object.select_all(action='DESELECT')
            for obj in export_objects:
                obj.select_set(True)
            utils.set_active(export_objects[0])

            bpy.ops.export_scene.fbx(
                filepath=self.filepath,
                use_selection=True,
                object_types=export_types,
                apply_scale_options='FBX_SCALE_ALL',
                axis_forward='-Z',
                axis_up='Y',
                use_armature_deform_only=True,
                add_leaf_bones=False,
                primary_bone_axis='Y',
                secondary_bone_axis='X',
                armature_nodetype='NULL',
                mesh_smooth_type='OFF',
                use_mesh_modifiers=True,
                bake_anim=has_animation,
                bake_anim_use_all_bones=True,
                bake_anim_use_nla_strips=False,
                bake_anim_use_all_actions=False,
                path_mode='AUTO',
                embed_textures=False,
            )
        finally:
            armature.name = original_name
            if conflicting:
                conflicting.name = EXPORT_RIG_NAME

        self.report({'INFO'}, f'Exported rig as "{EXPORT_RIG_NAME}" to "{self.filepath}".')
        return {'FINISHED'}
