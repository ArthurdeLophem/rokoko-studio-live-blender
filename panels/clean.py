import bpy

from .main import ToolPanel
from ..operators import retargeting


# Clean animation panel
class CleanPanel(ToolPanel, bpy.types.Panel):
    bl_idname = 'VIEW3D_PT_rsl_clean_animation'
    bl_label = 'Animating'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = False

        if self.bl_idname == 'VIEW3D_PT_rsl_retargeting_v2':
            row = layout.row(align=True)
            row.prop(context.scene, 'rsl_retargeting_clean_animation')

        col = layout.column(align=True)
        col.prop(context.scene, 'rsl_retargeting_clean_tolerance')
        col.prop(context.scene, 'rsl_retargeting_decimate_percent')
        col.prop(context.scene, 'rsl_retargeting_smooth_iterations')
        col.prop(context.scene, 'rsl_retargeting_smooth_interpolation')

        row = layout.row(align=True)
        row.scale_y = 1.4
        row.operator(retargeting.CleanAnimation.bl_idname, icon='MOD_DECIM')
