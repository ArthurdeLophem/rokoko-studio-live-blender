
import bpy
import copy

from ..core import animation_cleanup
from ..core.retargeting import get_target_armature

RETARGET_ID = '_RSL_RETARGET'


class CleanAnimation(bpy.types.Operator):
    bl_idname = "rsl.clean_animation"
    bl_label = "Clean Animation"
    bl_description = "Cleans the animation of the target armature using the Clean Animation settings"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    def execute(self, context):
        armature_target = get_target_armature()

        if not armature_target or not armature_target.animation_data or not armature_target.animation_data.action:
            self.report({'ERROR'}, 'No animation on the target armature found!'
                                   '\nRetarget an animation first or select a target with an animation.')
            return {'CANCELLED'}

        target_bones = {item.bone_name_target for item in context.scene.rsl_retargeting_bone_list if item.bone_name_target} or None
        animation_cleanup.clean_action(context.scene, armature_target.animation_data.action, target_bones)

        self.report({'INFO'}, 'Cleaned the animation.')
        return {'FINISHED'}