import bpy

from .main import ToolPanel
from ..operators.export import ExportRig, EXPORT_COLLECTION_NAME, EXPORT_RIG_NAME, get_export_collection


# Export panel
class ExportPanel(ToolPanel, bpy.types.Panel):
    bl_idname = 'VIEW3D_PT_rsl_export'
    bl_label = 'Export'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = False
        coll =  get_export_collection(context.scene)

        if not coll:
            row = layout.row(align=True)
            row.label(text=f'No "{EXPORT_COLLECTION_NAME}" collection found!', icon='ERROR')
            return

        row = layout.row(align=True)
        row.label(text=f'Rig in "{coll.name}" is exported as "{EXPORT_RIG_NAME}"', icon='INFO')

        row = layout.row(align=True)
        row.label(text='Export:')
        row.prop(context.scene, 'rsl_export_object_types', expand=True)

        row = layout.row(align=True)
        row.scale_y = 1.4
        row.operator(ExportRig.bl_idname, icon='EXPORT')
