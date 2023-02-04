# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

import bpy
from . import shared
from . import bl_enum


def register_props():
    bpy.types.Object.m3_ribbons = bpy.props.CollectionProperty(type=RibbonProperties)
    bpy.types.Object.m3_ribbons_index = bpy.props.IntProperty(options=set(), default=-1, update=update_collection_index)
    bpy.types.Object.m3_ribbons_version = bpy.props.EnumProperty(options=set(), items=ribbon_version, default='9')
    bpy.types.Object.m3_ribbonsplines = bpy.props.CollectionProperty(type=SplineProperties)
    bpy.types.Object.m3_ribbonsplines_index = bpy.props.IntProperty(options=set(), default=-1, update=update_spline_collection_index)


# TODO UI stuff
ribbon_version = (
    ('4', '4', 'Version 4'),
    ('5', '5', 'Version 5'),
    ('6', '6', 'Version 6'),
    ('7', '7', 'Version 7'),
    ('8', '8', 'Version 8'),
    ('9', '9', 'Version 9'),
)


def update_collection_index(self, context):
    if self.m3_ribbons_index in range(len(self.m3_ribbons)):
        bl = self.m3_ribbons[self.m3_ribbons_index]
        shared.select_bones_handles(context.object, [bl.bone])


def update_spline_collection_index(self, context):
    spline = self.m3_ribbonsplines[self.m3_ribbonsplines_index]
    if spline.points_index in range(len(spline.points)):
        bl = spline.points[spline.points_index]
        shared.select_bones_handles(context.object, [bl.bone])


def update_point_collection_index(self, context):
    if self.points_index in range(len(self.points)):
        bl = self.points[self.points_index]
        shared.select_bones_handles(context.object, [bl.bone])


def draw_point_props(point, layout):
    shared.draw_prop_pointer_search(layout, point.bone, point.id_data.data, 'bones', text='Bone', icon='BONE_DATA')
    col = layout.column()
    col.prop(point, 'emission_offset', text='Emission Offset')
    col.prop(point, 'emission_vector', text='Emission Vector')
    col = layout.column(align=True)
    shared.draw_prop_anim(col, point, 'length', text='Length')
    shared.draw_prop_anim(col, point, 'yaw', text='Yaw')
    shared.draw_prop_anim(col, point, 'pitch', text='Pitch')
    col = layout.column(align=True)
    col.prop(point, 'length_var_shape', text='Length Variation')
    sub = col.column(align=True)
    sub.active = point.length_var_shape != 'NONE'
    shared.draw_prop_anim(sub, point, 'length_var_frequency', text='Frequency')
    shared.draw_prop_anim(sub, point, 'length_var_amplitude', text='Amount')
    col = layout.column(align=True)
    col.prop(point, 'yaw_var_shape', text='Yaw Variation')
    sub = col.column(align=True)
    sub.active = point.yaw_var_shape != 'NONE'
    shared.draw_prop_anim(sub, point, 'yaw_var_frequency', text='Frequency')
    shared.draw_prop_anim(sub, point, 'yaw_var_amplitude', text='Amount')
    col = layout.column(align=True)
    col.prop(point, 'pitch_var_shape', text='Pitch Variation')
    sub = col.column(align=True)
    sub.active = point.pitch_var_shape != 'NONE'
    shared.draw_prop_anim(sub, point, 'pitch_var_frequency', text='Frequency')
    shared.draw_prop_anim(sub, point, 'pitch_var_amplitude', text='Amount')


def draw_spline_props(spline, layout):
    shared.draw_collection_list(layout.box(), spline.points, draw_point_props, menu_id=PointsMenu.bl_idname)


def draw_ribbon_props(ribbon, layout):
    shared.draw_prop_pointer_search(layout, ribbon.bone, ribbon.id_data.data, 'bones', text='Bone', icon='BONE_DATA')
    shared.draw_prop_pointer_search(layout, ribbon.material, ribbon.id_data, 'm3_materialrefs', text='Material', icon='MATERIAL')
    shared.draw_prop_pointer_search(layout, ribbon.spline, ribbon.id_data, 'm3_ribbonsplines', text='Ribbon Spline', icon='LINKED')

    col = layout.column(align=True)
    col.prop(ribbon, 'ribbon_type', text='Ribbon Type')

    if ribbon.ribbon_type == 'CYLINDER':
        col.prop(ribbon, 'sides', text='Edges')

    if ribbon.ribbon_type == 'STAR':
        col.prop(ribbon, 'sides', text='Edges')
        col.prop(ribbon, 'star_ratio', text='Cylinder/Planar Ratio')

    col = layout.column(align=True)
    col.prop(ribbon, 'lod_reduce', text='LOD Reduction')
    col.prop(ribbon, 'lod_cut', text='Cutoff')
    col = layout.column(align=True)
    col.prop(ribbon, 'divisions', text='Emission Rate')
    shared.draw_prop_anim(col, ribbon, 'length', text='Velocity')
    shared.draw_prop_anim(col, ribbon, 'yaw', text='Yaw')
    shared.draw_prop_anim(col, ribbon, 'pitch', text='Pitch')
    col.separator()
    col = layout.column(align=True)
    col.prop(ribbon, 'gravity', text='Gravity')
    col = layout.column(align=True)
    col.prop(ribbon, 'cull_method', text='Division Cull Type')

    if ribbon.cull_method == 'TIME':
        col.prop(ribbon, 'lifespan', text=' ')

    elif ribbon.cull_method == 'LENGTH':
        shared.draw_prop_anim(col, ribbon, 'length', text='Length')
        row = col.row(align=True, heading='Lifespan')
        row.prop(ribbon, 'length_time', text='')
        sub = row.column(align=True)
        sub.active = ribbon.length_time
        sub.prop(ribbon, 'lifespan', text='')

    col = layout.column(align=True)
    shared.draw_prop_anim(col, ribbon, 'twist', index=0, text='Twist Base')
    shared.draw_prop_anim(col, ribbon, 'twist', index=1, text='Center')
    shared.draw_prop_anim(col, ribbon, 'twist', index=2, text='Tip')
    col.prop(ribbon, 'twist_anim_mid', text='Animation Center')
    col.prop(ribbon, 'twist_anim_mid_time', text='Animation Center Time')
    col = layout.column(align=True)
    shared.draw_prop_anim(col, ribbon, 'scale', index=0, text='Scale Base')
    shared.draw_prop_anim(col, ribbon, 'scale', index=1, text='Center')
    shared.draw_prop_anim(col, ribbon, 'scale', index=2, text='Tip')
    col.prop(ribbon, 'scale_anim_mid', text='Animation Center')
    col.prop(ribbon, 'scale_anim_mid_time', text='Animation Center Time')
    col = layout.column(align=True)
    shared.draw_prop_anim(col, ribbon, 'color_base', text='Color Base')
    shared.draw_prop_anim(col, ribbon, 'color_mid', text='Center')
    shared.draw_prop_anim(col, ribbon, 'color_tip', text='Tip')
    col.prop(ribbon, 'color_anim_mid', text='Color Animation Center')
    col.prop(ribbon, 'color_anim_mid_time', text='Color Animation Center Time')
    col.prop(ribbon, 'alpha_anim_mid', text='Alpha Animation Center')
    col.prop(ribbon, 'alpha_anim_mid_time', text='Alpha Animation Center Time')
    col = layout.column(align=True)
    col.prop(ribbon, 'stretch_limit', text='Stretch Limit')
    col.prop(ribbon, 'stretch_amount', text='Amount')
    col = layout.column(align=True)
    col.prop(ribbon, 'noise_amplitude', text='Noise Amplitude')
    col.prop(ribbon, 'noise_waves', text='Waves')
    col.prop(ribbon, 'noise_frequency', text='Frequency')
    col.prop(ribbon, 'noise_scale', text='Scale')
    col = layout.column(align=True)
    col.prop(ribbon, 'amplitude_var_shape', text='Amplitude Variation')
    sub = col.column(align=True)
    sub.active = ribbon.amplitude_var_shape != 'NONE'
    shared.draw_prop_anim(sub, ribbon, 'amplitude_var_frequency', text='Frequency')
    shared.draw_prop_anim(sub, ribbon, 'amplitude_var_amplitude', text='Amount')
    col = layout.column(align=True)
    col.prop(ribbon, 'direction_var_shape', text='Direction Variation')
    sub = col.column(align=True)
    sub.active = ribbon.direction_var_shape != 'NONE'
    shared.draw_prop_anim(sub, ribbon, 'direction_var_frequency', text='Frequency')
    shared.draw_prop_anim(sub, ribbon, 'direction_var_amplitude', text='Amount')
    col = layout.column(align=True)
    col.prop(ribbon, 'length_var_shape', text='Length Variation')
    sub = col.column(align=True)
    sub.active = ribbon.length_var_shape != 'NONE'
    shared.draw_prop_anim(sub, ribbon, 'length_var_frequency', text='Frequency')
    shared.draw_prop_anim(sub, ribbon, 'length_var_amplitude', text='Amount')
    col = layout.column(align=True)
    col.prop(ribbon, 'scale_var_shape', text='Scale Variation')
    sub = col.column(align=True)
    sub.active = ribbon.scale_var_shape != 'NONE'
    shared.draw_prop_anim(sub, ribbon, 'scale_var_frequency', text='Frequency')
    shared.draw_prop_anim(sub, ribbon, 'scale_var_amplitude', text='Amount')
    col = layout.column(align=True)
    col.prop(ribbon, 'alpha_var_shape', text='Alpha Variation')
    sub = col.column(align=True)
    sub.active = ribbon.alpha_var_shape != 'NONE'
    shared.draw_prop_anim(sub, ribbon, 'alpha_var_frequency', text='Frequency')
    shared.draw_prop_anim(sub, ribbon, 'alpha_var_amplitude', text='Amount')
    col = layout.column_flow(align=True, columns=2)
    col.use_property_split = False
    col.prop(ribbon, 'collide_terrain', text='Collide Terrain')
    col.prop(ribbon, 'collide_objects', text='Collide Objects')
    col.prop(ribbon, 'edge_falloff', text='Edge Falloff')
    col.prop(ribbon, 'force_cpu_sim', text='Force CPU Simulation')
    col.prop(ribbon, 'inherit_parent_velocity', text='Inherit Parent Velocity')
    col.prop(ribbon, 'scale_time_parent', text='Scale Time By Parent')
    col.prop(ribbon, 'local_time', text='Local Time')
    col.prop(ribbon, 'simulate_init', text='Simulate On Init')
    col.prop(ribbon, 'scale_smooth', text='Smooth Size')
    col.prop(ribbon, 'scale_smooth_bezier', text='Smooth Size Bezier')
    col.prop(ribbon, 'vertex_alpha', text='Vertex Alpha')


class RibbonPointerProp(bpy.types.PropertyGroup):
    value: bpy.props.StringProperty(options=set(), get=shared.pointer_get_args('m3_ribbons'), set=shared.pointer_set_args('m3_ribbons', False))
    handle: bpy.props.StringProperty(options=set())


class PointProperties(shared.M3PropertyGroup):
    bone: bpy.props.PointerProperty(type=shared.M3BonePointerProp)
    emission_offset: bpy.props.FloatVectorProperty(options=set(), size=3, subtype='XYZ')
    emission_vector: bpy.props.FloatVectorProperty(options=set(), size=3, subtype='XYZ')
    yaw: bpy.props.FloatProperty(name='Spline Yaw')
    yaw_header: bpy.props.PointerProperty(type=shared.M3AnimHeaderProp)
    yaw_var_shape: bpy.props.EnumProperty(options=set(), items=bl_enum.ribbon_variation_shape)
    yaw_var_amplitude: bpy.props.FloatProperty(name='Spline Yaw Variation Amount')
    yaw_var_amplitude_header: bpy.props.PointerProperty(type=shared.M3AnimHeaderProp)
    yaw_var_frequency: bpy.props.FloatProperty(name='Spline Yaw Variation Frequency')
    yaw_var_frequency_header: bpy.props.PointerProperty(type=shared.M3AnimHeaderProp)
    pitch: bpy.props.FloatProperty(name='Spline Pitch')
    pitch_header: bpy.props.PointerProperty(type=shared.M3AnimHeaderProp)
    pitch_var_shape: bpy.props.EnumProperty(options=set(), items=bl_enum.ribbon_variation_shape)
    pitch_var_amplitude: bpy.props.FloatProperty(name='Spline Pitch Variation Amount')
    pitch_var_amplitude_header: bpy.props.PointerProperty(type=shared.M3AnimHeaderProp)
    pitch_var_frequency: bpy.props.FloatProperty(name='Spline Pitch Variation Frequency')
    pitch_var_frequency_header: bpy.props.PointerProperty(type=shared.M3AnimHeaderProp)
    length: bpy.props.FloatProperty(name='Spline Length')
    length_header: bpy.props.PointerProperty(type=shared.M3AnimHeaderProp)
    length_var_shape: bpy.props.EnumProperty(options=set(), items=bl_enum.ribbon_variation_shape)
    length_var_amplitude: bpy.props.FloatProperty(name='Spline Length Variation Amount')
    length_var_amplitude_header: bpy.props.PointerProperty(type=shared.M3AnimHeaderProp)
    length_var_frequency: bpy.props.FloatProperty(name='Spline Length Variation Frequency')
    length_var_frequency_header: bpy.props.PointerProperty(type=shared.M3AnimHeaderProp)


class SplineProperties(shared.M3PropertyGroup):
    points: bpy.props.CollectionProperty(type=PointProperties)
    points_index: bpy.props.IntProperty(options=set(), default=-1, update=update_point_collection_index)


class RibbonProperties(shared.M3PropertyGroup):
    bone: bpy.props.PointerProperty(type=shared.M3BonePointerProp)
    material: bpy.props.PointerProperty(type=shared.M3MatRefPointerProp)
    spline: bpy.props.PointerProperty(type=RibbonPointerProp)
    ribbon_type: bpy.props.EnumProperty(options=set(), items=bl_enum.ribbon_type)
    cull_method: bpy.props.EnumProperty(options=set(), items=bl_enum.ribbon_cull)
    lod_cut: bpy.props.EnumProperty(options=set(), items=bl_enum.lod)
    lod_reduce: bpy.props.EnumProperty(options=set(), items=bl_enum.lod)
    active: bpy.props.BoolProperty(name='Active', default=True)  # TODO draw
    active_header: bpy.props.PointerProperty(type=shared.M3AnimHeaderProp)
    lifespan: bpy.props.FloatProperty(name='Lifespan', min=0, default=5)
    lifespan_header: bpy.props.PointerProperty(type=shared.M3AnimHeaderProp)
    divisions: bpy.props.FloatProperty(options=set(), min=0, default=20)
    sides: bpy.props.IntProperty(options=set(), min=3, default=5)
    star_ratio: bpy.props.FloatProperty(options=set(), subtype='FACTOR', min=0, max=1, default=0.5)
    length: bpy.props.FloatProperty(name='Length', min=0)
    length_header: bpy.props.PointerProperty(type=shared.M3AnimHeaderProp)
    yaw: bpy.props.FloatProperty(name='Yaw')
    yaw_header: bpy.props.PointerProperty(type=shared.M3AnimHeaderProp)
    pitch: bpy.props.FloatProperty(name='Pitch')
    pitch_header: bpy.props.PointerProperty(type=shared.M3AnimHeaderProp)
    twist: bpy.props.FloatVectorProperty(name='Twist', subtype='XYZ', size=3)
    twist_header: bpy.props.PointerProperty(type=shared.M3AnimHeaderProp)
    scale: bpy.props.FloatVectorProperty(name='Scale', subtype='XYZ', size=3, default=(1, 1, 1))
    scale_header: bpy.props.PointerProperty(type=shared.M3AnimHeaderProp)
    color_base: bpy.props.FloatVectorProperty(name='Base Color', subtype='COLOR', size=4, min=0, max=1, default=(1, 1, 1, 1))
    color_base_header: bpy.props.PointerProperty(type=shared.M3AnimHeaderProp)
    color_mid: bpy.props.FloatVectorProperty(name='Center Color', subtype='COLOR', size=4, min=0, max=1, default=(1, 1, 1, 1))
    color_mid_header: bpy.props.PointerProperty(type=shared.M3AnimHeaderProp)
    color_tip: bpy.props.FloatVectorProperty(name='Tip Color', subtype='COLOR', size=4, min=0, max=1, default=(1, 1, 1, 0))
    color_tip_header: bpy.props.PointerProperty(type=shared.M3AnimHeaderProp)
    twist_anim_mid: bpy.props.FloatProperty(options=set(), subtype='FACTOR', min=0, max=1, default=1)
    scale_anim_mid: bpy.props.FloatProperty(options=set(), subtype='FACTOR', min=0, max=1, default=1)
    color_anim_mid: bpy.props.FloatProperty(options=set(), subtype='FACTOR', min=0, max=1, default=1)
    alpha_anim_mid: bpy.props.FloatProperty(options=set(), subtype='FACTOR', min=0, max=1, default=1)
    twist_anim_mid_time: bpy.props.FloatProperty(options=set(), min=0)
    scale_anim_mid_time: bpy.props.FloatProperty(options=set(), min=0)
    color_anim_mid_time: bpy.props.FloatProperty(options=set(), min=0)
    alpha_anim_mid_time: bpy.props.FloatProperty(options=set(), min=0)
    scale_smoothing: bpy.props.EnumProperty(items=bl_enum.anim_smoothing)  # TODO
    color_smoothing: bpy.props.EnumProperty(items=bl_enum.anim_smoothing)  # TODO
    gravity: bpy.props.FloatProperty(options=set())
    stretch_amount: bpy.props.FloatProperty(options=set(), default=1)
    stretch_limit: bpy.props.FloatProperty(options=set(), default=1)
    noise_amplitude: bpy.props.FloatProperty(options=set())
    noise_waves: bpy.props.FloatProperty(options=set())
    noise_frequency: bpy.props.FloatProperty(options=set())
    noise_scale: bpy.props.FloatProperty(options=set())
    bounce: bpy.props.FloatProperty(options=set(), subtype='FACTOR', min=0, max=1)  # TODO
    friction: bpy.props.FloatProperty(options=set(), min=0, max=1)  # TODO
    drag: bpy.props.FloatProperty(options=set())  # TODO
    mass: bpy.props.FloatProperty(options=set())  # TODO
    mass2: bpy.props.FloatProperty(options=set())  # TODO
    local_forces: bpy.props.BoolVectorProperty(options=set(), subtype='LAYER', size=16)  # TODO
    world_forces: bpy.props.BoolVectorProperty(options=set(), subtype='LAYER', size=16)  # TODO
    world_space: bpy.props.BoolProperty(options=set())
    amplitude_var_shape: bpy.props.EnumProperty(options=set(), items=bl_enum.ribbon_variation_shape)
    amplitude_var_amplitude: bpy.props.FloatProperty(name='Amplitude Variation Amount')
    amplitude_var_amplitude_header: bpy.props.PointerProperty(type=shared.M3AnimHeaderProp)
    amplitude_var_frequency: bpy.props.FloatProperty(name='Amplitude Variation Frequency')
    amplitude_var_frequency_header: bpy.props.PointerProperty(type=shared.M3AnimHeaderProp)
    direction_var_shape: bpy.props.EnumProperty(options=set(), items=bl_enum.ribbon_variation_shape)
    direction_var_amplitude: bpy.props.FloatProperty(name='Directional Variation Amount')
    direction_var_amplitude_header: bpy.props.PointerProperty(type=shared.M3AnimHeaderProp)
    direction_var_frequency: bpy.props.FloatProperty(name='Directional Variation Frequency')
    direction_var_frequency_header: bpy.props.PointerProperty(type=shared.M3AnimHeaderProp)
    length_var_shape: bpy.props.EnumProperty(options=set(), items=bl_enum.ribbon_variation_shape)
    length_var_amplitude: bpy.props.FloatProperty(name='Length Variation Amount')
    length_var_amplitude_header: bpy.props.PointerProperty(type=shared.M3AnimHeaderProp)
    length_var_frequency: bpy.props.FloatProperty(name='Length Variation Frequency')
    length_var_frequency_header: bpy.props.PointerProperty(type=shared.M3AnimHeaderProp)
    scale_var_shape: bpy.props.EnumProperty(options=set(), items=bl_enum.ribbon_variation_shape)
    scale_var_amplitude: bpy.props.FloatProperty(name='Scale Variation Amount')
    scale_var_amplitude_header: bpy.props.PointerProperty(type=shared.M3AnimHeaderProp)
    scale_var_frequency: bpy.props.FloatProperty(name='Scale Variation Frequency')
    scale_var_frequency_header: bpy.props.PointerProperty(type=shared.M3AnimHeaderProp)
    alpha_var_shape: bpy.props.EnumProperty(options=set(), items=bl_enum.ribbon_variation_shape)
    alpha_var_amplitude: bpy.props.FloatProperty(name='Alpha Variation Amount')
    alpha_var_amplitude_header: bpy.props.PointerProperty(type=shared.M3AnimHeaderProp)
    alpha_var_frequency: bpy.props.FloatProperty(name='Alpha Variation Frequency')
    alpha_var_frequency_header: bpy.props.PointerProperty(type=shared.M3AnimHeaderProp)
    parent_velocity: bpy.props.FloatProperty(name='Parent Velocity')  # TODO
    parent_velocity_header: bpy.props.PointerProperty(type=shared.M3AnimHeaderProp)
    phase_shift: bpy.props.FloatProperty(name='Phase Shift')  # TODO
    phase_shift_header: bpy.props.PointerProperty(type=shared.M3AnimHeaderProp)
    collide_terrain: bpy.props.BoolProperty(options=set())
    collide_objects: bpy.props.BoolProperty(options=set())
    edge_falloff: bpy.props.BoolProperty(options=set())
    inherit_parent_velocity: bpy.props.BoolProperty(options=set())
    scale_smooth: bpy.props.BoolProperty(options=set())
    scale_smooth_bezier: bpy.props.BoolProperty(options=set())
    vertex_alpha: bpy.props.BoolProperty(options=set())
    scale_time_parent: bpy.props.BoolProperty(options=set())
    force_cpu_sim: bpy.props.BoolProperty(options=set())
    local_time: bpy.props.BoolProperty(options=set())
    simulate_init: bpy.props.BoolProperty(options=set())
    length_time: bpy.props.BoolProperty(options=set())
    accurate_gpu_tangents: bpy.props.BoolProperty(options=set())  # TODO add to draw method


class PointsMenu(bpy.types.Menu):
    bl_idname = 'OBJECT_MT_m3_ribbonsplinepoints'
    bl_label = 'Menu'

    def draw(self, context):
        spline = context.object.m3_ribbonsplines[context.object.m3_ribbonsplines_index]
        shared.draw_menu_duplicate(self.layout, spline.points, dup_keyframes_opt=True)


class SplineMenu(bpy.types.Menu):
    bl_idname = 'OBJECT_MT_m3_ribbonsplines'
    bl_label = 'Menu'

    def draw(self, context):
        shared.draw_menu_duplicate(self.layout, context.object.m3_ribbonsplines, dup_keyframes_opt=True)


class RibbonMenu(bpy.types.Menu):
    bl_idname = 'OBJECT_MT_m3_ribbons'
    bl_label = 'Menu'

    def draw(self, context):
        shared.draw_menu_duplicate(self.layout, context.object.m3_ribbons, dup_keyframes_opt=True)


class RibbonPanel(shared.ArmatureObjectPanel, bpy.types.Panel):
    bl_idname = 'OBJECT_PT_M3_RIBBONS'
    bl_label = 'M3 Ribbons'

    def draw(self, context):
        shared.draw_collection_list(self.layout, context.object.m3_ribbons, draw_ribbon_props, menu_id=RibbonMenu.bl_idname)


class SplinePanel(shared.ArmatureObjectPanel, bpy.types.Panel):
    bl_idname = 'OBJECT_PT_M3_RIBBONSPLINES'
    bl_label = 'M3 Ribbon Splines'

    def draw(self, context):
        shared.draw_collection_list(self.layout, context.object.m3_ribbonsplines, draw_spline_props, menu_id=SplineMenu.bl_idname)


classes = (
    RibbonPointerProp,
    PointProperties,
    SplineProperties,
    RibbonProperties,
    PointsMenu,
    SplineMenu,
    RibbonMenu,
    RibbonPanel,
    SplinePanel,
)
