from bpy.types import Scene, Object
from bpy.props import IntProperty, StringProperty, EnumProperty, BoolProperty, FloatProperty, CollectionProperty, PointerProperty

from .core import animation_lists, state_manager, recorder, retargeting
from .panels import retargeting as retargeting_ui


def register():
    # Receiver
    Scene.rsl_receiver_port = IntProperty(
        name='Streaming Port',
        description="The port defined in Rokoko Studio",
        default=14043,
        min=1,
        max=65535
    )
    Scene.rsl_receiver_fps = IntProperty(
        name='FPS',
        description="How often is the data received",
        default=60,
        min=1,
        max=100
    )
    Scene.rsl_scene_scaling = FloatProperty(
        name='Scene Scaling',
        description="This allows you to scale the position of props and trackers."
                    "\nUseful to align their positions with armatures",
        default=1,
        precision=3,
        step=1
    )
    Scene.rsl_reset_scene_on_stop = BoolProperty(
        name='Reset Scene on Stop',
        description='This will reset the location and position of animated objects to the state of before starting the receiver',
        default=True
    )
    Scene.rsl_hide_mesh_during_play = BoolProperty(
        name='Hide Meshes during Play',
        description='This will hide all meshes that are animated by armatures'
                    '\nto greatly reduce lag and increase performance.'
                    '\nThis will not hide animated faces',
        default=False,
        update=state_manager.update_hidden_meshes
    )
    Scene.rsl_recording = BoolProperty(
        name='Toggle Recording',
        description='Start and stop recording of the data from Rokoko Studio',
        default=False,
        update=recorder.toggle_recording
    )

    # Command API
    Scene.rsl_command_ip_address = StringProperty(
        name='IP Address',
        description='Input the IP address of Rokoko Studio',
        default='127.0.0.1',
        maxlen=15
    )
    Scene.rsl_command_ip_port = IntProperty(
        name='Command API Port',
        description="The port defined in Rokoko Studio",
        default=14053,
        min=1,
        max=65535
    )
    Scene.rsl_command_api_key = StringProperty(
        name='API Key',
        description='Input the API key displayed in Rokoko Studio',
        default='1234',
        maxlen=15
    )

    # Retargeting
    Scene.rsl_retargeting_armature_source = PointerProperty(
        name='Source',
        description='Select the armature with the animation that you want to retarget',
        type=Object,
        poll=retargeting.poll_source_armatures,
        update=retargeting.clear_bone_list
    )
    Scene.rsl_retargeting_armature_target = PointerProperty(
        name='Target',
        description='Select the armature that should receive the animation',
        type=Object,
        poll=retargeting.poll_target_armatures,
        update=retargeting.clear_bone_list
    )
    Scene.rsl_retargeting_auto_scaling = BoolProperty(
        name='Auto Scale',
        description='This will scale the source armature to fit the height of the target armature.'
                    '\nBoth armatures have to be in T-pose for this to work correctly',
        default=False
    )
    Scene.rsl_retargeting_copy_rest_pose = BoolProperty(
        name='Copy Rest Pose',
        description='Copy the rest pose (location, rotation and scale) from the source armature'
                    '\nto the target armature before retargeting the animation.'
                    '\nThis is applied to all mapped bones and then set as the target rest pose'
                    '\nAlways applied when the target armature has no animation',
        default=True
    )
    Scene.rsl_retargeting_clean_animation = BoolProperty(
        name='Clean Animation',
        description='Clean the retargeted animation: removes unused channels, reduces constant channels to their first keyframe'
                    '\nand removes redundant keyframes',
        default=True
    )
    Scene.rsl_retargeting_clean_tolerance = FloatProperty(
        name='Tolerance',
        description='How far a keyframe may deviate from the curve before it is kept. Higher values remove more keyframes',
        default=0.001,
        min=0.0,
        precision=4
    )
    Scene.rsl_retargeting_decimate_percent = FloatProperty(
        name='Decimate Allowed Change',
        description='Largest change allowed when removing keyframes, as a percentage of each channel\'s value range.'
                    '\nKeyframes are only removed if the curve stays within this change. 0 uses only the tolerance',
        default=0.6,
        min=0.0,
        max=100.0,
        precision=2
    )
    Scene.rsl_retargeting_smooth_iterations = IntProperty(
        name='Smooth Passes',
        description='Number of smoothing passes applied to each channel. 0 disables smoothing',
        default=0,
        min=0,
        max=20
    )
    Scene.rsl_retargeting_smooth_interpolation = BoolProperty(
        name='Smooth Interpolation',
        description='Use Bezier interpolation with auto-clamped handles instead of linear, for softer motion',
        default=True
    )
    Scene.rsl_retargeting_use_pose = EnumProperty(
        name="Use Pose",
        description='Select which pose of the source and target armature to use to retarget the animation.'
                    '\nBoth armatures should be in the same pose before retargeting',
        items=[
            ("REST", "Rest", "Select this to use the rest pose during retargeting."),
            ("CURRENT", "Current", "Select this to use the current pose during retargeting.")
        ],
        default="CURRENT"
    )
    Scene.rsl_retargeting_bone_list = CollectionProperty(
        type=retargeting_ui.BoneListItem
    )
    Scene.rsl_retargeting_bone_list_index = IntProperty(
        name="Index for the retargeting bone list",
        default=0
    )

    # Export
    Scene.rsl_export_object_types = EnumProperty(
        name='Export Types',
        description='Select which object types are included in the export',
        items=[
            ("ARMATURE", "Armature", "Export the rig"),
            ("MESH", "Mesh", "Export the meshes in the export collection")
        ],
        options={'ENUM_FLAG'},
        default={'ARMATURE'}
    )

    # Objects
    Object.rsl_animations_props_trackers = EnumProperty(
        name='Tracker or Prop',
        description='Select the prop or tracker that you want to attach this object to',
        items=animation_lists.get_props_trackers,
        update=state_manager.update_object
    )
    Object.rsl_animations_faces = EnumProperty(
        name='Face',
        description='Select the face that you want to attach this mesh to',
        items=animation_lists.get_faces,
        update=state_manager.update_face
    )
    Object.rsl_animations_actors = EnumProperty(
        name='Actor',
        description='Select the actor that you want to attach this armature to',
        items=animation_lists.get_actors,
        update=state_manager.update_actor
    )
    Object.rsl_use_custom_scale = BoolProperty(
        name='Use Custom Scale',
        description='Select this if the objects scene scaling should be overwritten',
        default=False,
    )
    Object.rsl_custom_scene_scale = FloatProperty(
        name='Custom Scene Scaling',
        description="This allows you to scale the position independently from the scene scale.",
        default=1,
        precision=3,
        step=1
    )

    # Face shapekeys
    for shape in animation_lists.face_shapes:
        setattr(Object, 'rsl_face_' + shape, StringProperty(
            name=shape,
            description='Select the shapekey that should be animated by this shape'
        ))

    # Actor bones
    for bone in animation_lists.get_bones().keys():
        setattr(Object, 'rsl_actor_' + bone, StringProperty(
            name=bone,
            description='Select the bone that corresponds to the actors bone'
        ))
