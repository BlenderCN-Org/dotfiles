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

# NEWS

# This Version is compatible with blender trunk, but not with 2.66a or earlier releases
# There's also an edit composition button in the compositor, now (intended for working
# with blender's gui splitted into more than on window).
#
# now the operator checks for existing image or movie datablocks 
# before to create new ones, no more duplicated garbage in the blend file...
#
# dropdown selectors for node groups and screens (updated dinamically
# everytime an scene property change)
# 
# all options are now persitent in the blend file

# when creating a new comp, main scene resolution is
# changed acording to source video resolution: bpy.ops.sequencer.rendersize()
# and the render settings are copied to the new scene

# new scenes are renamed
# Comp_stripsource.name

# render options removed. The new comp output filepath is set to
# //Comp/Comp_filename

# i.e: a strip refering a video called video will generate
# a comp called Comp_video or Comp_video.00x (if other already exist)
# with output render set to: //Comp/Comp_video/

# if you choose automatic proxy settings
# the new scene strip will have proxy set to custom directory
# in this way:   //.proxy/Comp_video

# with preserve duration you will obtain a soft cutted scene strip
# without preserve duration you will obtain a hard cutted scene strip
# both options fully synched with original strip no matter if it has
# soft and hard cuts

# added scale node options 
# (auto set to strech, to work with multiple resolutions)

# "add node group" option now is only visible if some nodegroup exist

bl_info = {
    "name": "Edit Strip With Compositor REMAKE f",
    "description": "Send one or more Sequencer strips to the Compositor, gently",
    "author": "Carlos Padial, TMW, Björn Sonnenschein",
    "version": (0, 14),
    "blender": (2, 68, 0),
    "location": "Sequencer > UI panel, Node Editor > UI panel",
    "warning": "Experimental",
    "wiki_url": "None Yet"
                "None Yet",
    "tracker_url": "None"
                   "func=detail&aid=<number>",
    "category": "Sequencer"}

import bpy, os

from bpy.props import (IntProperty,
                        FloatProperty,
                        EnumProperty,
                        BoolProperty,
                        StringProperty,
                        CollectionProperty,
                        PointerProperty,
                        )

# jump to cut functions
def triminout(strip, sin, sout):
    start = strip.frame_start + strip.frame_offset_start
    end = start + strip.frame_final_duration
    if end > sin:
        if start < sin:
            strip.select_right_handle = False
            strip.select_left_handle = True
            bpy.ops.sequencer.snap(frame=sin)
            strip.select_left_handle = False
    if start < sout:
        if end > sout:
            strip.select_left_handle = False
            strip.select_right_handle = True
            bpy.ops.sequencer.snap(frame=sout)
            strip.select_right_handle = False
    return {'FINISHED'}
    

# ----------------------------------------------------------------------------
# Persistent Scene Data Types for Edit Strip With Compositor addon (eswc_info)

class ESWC_Info(bpy.types.PropertyGroup):

    
    comp_name = StringProperty(
        name = "Comp Name", 
        default = "",
        description = "Name of the composite") 
    
    show_options_bool = BoolProperty( 
        name = "Show options", 
        description = "Show options", 
        default = False)  
    
    addscale_bool = BoolProperty(
        name = "Add Scale node", 
        description = "Add Scale node", 
        default = False)
    
    preserveduration_bool = BoolProperty( 
        name = "Preserve strip duration", 
        description = "For single clips the new scene will have the duration \
         of the active movie strip's input file and gets trimmed \
         to match it's length", 
        default = False )    
    
    addviewer_bool = BoolProperty(
        name = "Add Viewer", 
        description = "You can add a viewer node to the new compositions \
        automatically", 
        default = False )   
    
    addgroup_bool = BoolProperty(
        name="Add Nodegroup", 
        description = "You can add a custom node group to the new compositions \
        automatically", 
        default = False )    
    
    autoproxy_bool = BoolProperty(
        name = "Automatic proxy settings", 
        description = "The new scene will automatically create and use a proxy \
        custom directory in the project directory, 100% proxy will be \
        generated by default. ", 
        default = False )  
    
    selections = [  ( "All", "All", "Copy all settings" ), 
           #( "Select", "Select", "Copy selected settings" ),
           ( "None", "None", "Copy none of the settings" )]
    settings = EnumProperty(
        name = "Settings Type", 
        items = selections, 
        default="All",
        description = "Choose which settings to copy" ) 
    
    proxy_qualities = [  ( "1", "25%", "" ), ( "2", "50%", "" ),
                    ( "3", "75%", "" ), ( "4", "100%", "" )]
    pq = EnumProperty(
        name = "Proxy Quality", items = proxy_qualities,
        default = "1", 
        description = "Quality setting for auto proxies" )
        
    channelincrease = IntProperty(
        name = "Channel increase",
        description = "Define how many tracks above the source strips the new \
        Strips are placed for the single strip option. For the multiple clips \
        option this is the channel number the new strip will be placed in", 
        default = 1, min = 1, max = 30, step = 1)
    
    master_scene = StringProperty(
        name = "Master Scene", 
        description = "This is the name of the Scene's Master Scene", 
        default = "Scene")
    
    scene_init_comp = BoolProperty( name="", 
        description = "", 
        default = False ) 
        
    #col_node_groups = CollectionProperty(type=StringColl)
    
    def avail_nodegroups(self, context):
        items = []
        for i, elem in enumerate(bpy.data.node_groups):
            items.append((str(i), elem.name, elem.name))
        return items
    
    
    enum_node_groups = EnumProperty(items=avail_nodegroups, 
                                    name="Node Group")
                                    
    def avail_screens(self, context):
        items = []
        for i, elem in enumerate(bpy.data.screens):
            items.append((str(i), elem.name, elem.name))
        return items
    
    
    enum_edit_screen = EnumProperty(items=avail_screens, 
                                    name="Editing Screen")
                                    
    enum_comp_screen = EnumProperty(items=avail_screens, 
                                    name="Compositing Screen")
    
    

# Initialization                
def initprops(context, scn):

    eswc_info = scn.eswc_info
    
    try:
        if eswc_info.scene_init_comp == True:
            return False
    except AttributeError:
        pass
    #Define some new properties we will use
    eswc_info.comp_name = ""   # what is this for?   
    eswc_info.show_options_bool = False
    eswc_info.addscale_bool = False   
    eswc_info.preserveduration_bool = True
    eswc_info.addviewer_bool = False
    eswc_info.addgroup_bool = False
    eswc_info.autoproxy_bool = False
    eswc_info.settings = "All"
    eswc_info.pq = "1"
    eswc_info.channelincrease = 1 
    eswc_info.scene_init_comp = True
    
class SetMasterSceneOperator(bpy.types.Operator): 
     
    bl_idname = "eswc.set_master_scene"
    bl_label = "Set master scene"
            
    def invoke(self, context, event ):
        
        bpy.ops.sequencer.rendersize()
        initprops(context, context.scene)
            
        return {'FINISHED'} 
        
        
#______________________PANEL_______________________________________     

 
class CompPanel(bpy.types.Panel):
    bl_label = "Edit strip with Compositor"
    bl_space_type = "SEQUENCE_EDITOR"
    bl_region_type = "UI"
    
    @staticmethod
    def has_sequencer(context):
        return (context.space_data.view_type in {'SEQUENCER'})

    @classmethod
    def poll(self, context):
        try:
            if context.scene.sequence_editor.active_strip:
                if context.scene.sequence_editor.active_strip.type \
                in {'MOVIE', "IMAGE", "SCENE"}:
                    return context.scene.sequence_editor
                else:
                    return False
            else:
                return False
        except AttributeError:
             return False
    def draw(self, context):
        scn = context.scene
        layout = self.layout
        try:
            activestrip = scn.sequence_editor.active_strip
            eswc_info = scn.eswc_info
            if eswc_info.scene_init_comp:
                if activestrip.type == "SCENE":
                    layout.operator("eswc.switch_to_composite")
                if activestrip.type in {"MOVIE", "IMAGE"}:
                    layout.operator("eswc.single_comp")
                    layout.prop(eswc_info,"show_options_bool")
                    if eswc_info.show_options_bool == True:
                        box = layout.box()
                        
                        col = box.column(align=True)
                        
                        col.prop(eswc_info,"channelincrease")
                        col.prop(eswc_info,"settings")
                        col.prop(eswc_info,"addviewer_bool")
                        col.prop(eswc_info,"addscale_bool")
                        col.prop(eswc_info,"preserveduration_bool")
                        col.prop(eswc_info,"autoproxy_bool")
                        if eswc_info.autoproxy_bool:
                            col.prop(eswc_info,"pq")
                        
                        if len(bpy.data.node_groups) != 0:
                            col.prop(eswc_info,"addgroup_bool")
                            if eswc_info.addgroup_bool:
                                # node group selector
                                col.prop(eswc_info,"enum_node_groups")
                        
                        box = layout.box()
                        col = box.column(align=True)
                        
                        # comp screen selector
                        col.prop(eswc_info, "enum_comp_screen")
                        
                        # editing screen selector
                        col.prop(eswc_info, "enum_edit_screen")
            
            else:     
                layout.operator("eswc.set_master_scene")               
        except AttributeError as Err:  
            layout.operator("eswc.set_master_scene")   
            

class NodePanel(bpy.types.Panel):
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"
    bl_label = "Edit strip with Compositor"
 
    def draw(self, context):
        scn = context.scene
        try:
            eswc_info = scn.eswc_info
            
            layout = self.layout
            row = layout.row()
            col = row.column()
            try:
                col.prop(eswc_info, "comp_name" )
                col.operator("eswc.switch_back_to_timeline" )
                col.operator("eswc.switch_to_composite_nodepanel")
                row = layout.row()
                col = row.column()
                col.operator("eswc.fix_operator")
            except KeyError:
                pass
        except AttributeError:
            pass
            
class Switch_to_Composite_Operator(bpy.types.Operator):
    
    bl_idname = "eswc.switch_to_composite"
    bl_label = "Edit Composition"
               
    def invoke(self, context, event ):
        if (context.scene.sequence_editor.active_strip.type == 'SCENE'):
            stripscene = context.scene.sequence_editor.active_strip.scene
            scn = context.scene 
            eswc_info = scn.eswc_info
            
            for i, elem in enumerate(bpy.data.screens):
                if i == int(eswc_info.enum_comp_screen):
                    screen_name = elem.name
                    break      
        
            for i in bpy.data.screens:
                bpy.ops.screen.screen_set(delta=1)
                if (context.screen.name == screen_name):
                    break
        
            context.screen.scene = stripscene
            
            try:
                viewer = context.scene.node_tree.nodes['Viewer']
                context.scene.node_tree.nodes.active = viewer
            except KeyError:
                pass
            context.scene.frame_current = context.scene.frame_start
                      
        return {'FINISHED'} 
    
class Switch_to_Composite_Nodepanel_Operator(bpy.types.Operator):
    
    bl_idname = "eswc.switch_to_composite_nodepanel"
    bl_label = "Edit Composition"
               
    def invoke(self, context, event ):
        
        activestrip = bpy.data.scenes[context.scene.eswc_info.master_scene].sequence_editor.active_strip
        scn = bpy.data.scenes[context.scene.eswc_info.master_scene]
        
        if (scn.sequence_editor.active_strip.type == 'SCENE'):
            stripscene = scn.sequence_editor.active_strip.scene
            eswc_info = scn.eswc_info
            
            for i, elem in enumerate(bpy.data.screens):
                if i == int(eswc_info.enum_comp_screen):
                    screen_name = elem.name
                    break      
        
            for i in bpy.data.screens:
                bpy.ops.screen.screen_set(delta=1)
                if (context.screen.name == screen_name):
                    break
        
            context.screen.scene = stripscene
            
            try:
                viewer = context.scene.node_tree.nodes['Viewer']
                context.scene.node_tree.nodes.active = viewer
            except KeyError:
                pass
            context.scene.frame_current = context.scene.frame_start
                      
        return {'FINISHED'} 
    
    
class Switch_back_to_Timeline_Operator(bpy.types.Operator): 
     
    bl_idname = "eswc.switch_back_to_timeline"
    bl_label = "Get Back"
            
    def invoke(self, context, event ):
        
        scn = bpy.data.scenes[context.scene.eswc_info.master_scene]
        
        # this is to avoid errors when changing percentage for preview render...
        context.scene.render.resolution_percentage = 100  
                   
        eswc_info = scn.eswc_info    
        
        for i, elem in enumerate(bpy.data.screens):
            if i == int(eswc_info.enum_edit_screen):
                screen_name = elem.name
                break      
        
        for i in bpy.data.screens:
            bpy.ops.screen.screen_set(delta=1)
            if (context.screen.name == screen_name):
                break
        
        context.screen.scene = scn
            
        return {'FINISHED'} 
        
          

 
#---------------------------------------------------------------------

import bpy

class UglyFixOperator(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "eswc.fix_operator"
    bl_label = "eswc fix Operator"

    """@classmethod
    def poll(cls, context):
        space = context.space_data
        return space.type == 'NODE_EDITOR'"""

    def execute(self, context):
        sce=context.scene
        sce.use_nodes = True
        sce.render.use_compositing = True
        tree =sce.node_tree
        
        for i in sce.node_tree.nodes:
            i.select=False 
            context.scene.update()     
            if i.type=="REROUTE":
                re=i
            if i.type=="COMPOSITE":
                for j in sce.node_tree.nodes:
                    j.select=False
                i.select=True   
                tree.nodes.active=i 
                context.scene.update()       
                bpy.ops.node.delete() 
                
        
        comp = tree.nodes.new('CompositorNodeComposite') 
        comp.location = 300,200
        try:
            links = tree.links
            links = links.new(re.outputs[0],comp.inputs[0])
        except:
            pass
        
        return {'FINISHED'}



#-------------------------------------------------------------------------
 
 
 
class S_CompOperator(bpy.types.Operator):
 
    bl_idname = "eswc.single_comp"
    bl_label = "Create Comp from strip"
        
    def invoke(self, context, event ):
        scn=context.scene
        
        def copyrendersettings(scena, scenb):
            '''
            Copy render settings for scene A to match original scene B
            ''' 
            scena.render.resolution_x = scenb.render.resolution_x
            scena.render.resolution_y = scenb.render.resolution_y
            scena.render.resolution_percentage = \
                                        scenb.render.resolution_percentage
            scena.render.fps  = scenb.render.fps
            path = bpy.path.abspath(\
                        os.path.join("//Comp", scena.name+"/"+scena.name))
            scena.render.filepath = bpy.path.relpath(path)
         
        def copycomprendersettings(scena, scenb):   
            # copy compositor render settings
            scena.node_tree.use_opencl = scenb.node_tree.use_opencl
            scena.node_tree.two_pass = scenb.node_tree.two_pass
            scena.node_tree.render_quality = scenb.node_tree.render_quality
            scena.node_tree.edit_quality = scenb.node_tree.edit_quality
            scena.node_tree.chunk_size = scenb.node_tree.chunk_size
            pass
    
        def copyallsettings(scena, scenb):
            '''
            Copy all listed settings for scene strip A scena.node_tree.use_opencl
            to match original scene strip B
            ''' 
            #scena.use_translation =  scenb.use_translation
            scena.use_reverse_frames =  scenb.use_reverse_frames
            scena.use_float =  scenb.use_float
            scena.use_flip_y =  scenb.use_flip_y
            scena.use_deinterlace =  scenb.use_deinterlace
            scena.use_default_fade =  scenb.use_default_fade
            scena.strobe =  scenb.strobe
            scena.speed_factor =  scenb.speed_factor
            scena.mute =  scenb.mute
            scena.lock =  scenb.lock
            scena.effect_fader =  scenb.effect_fader
            scena.color_saturation =  scenb.color_saturation
            scena.color_multiply =  scenb.color_multiply
            scena.blend_type =  scenb.blend_type
            scena.blend_alpha =  scenb.blend_alpha
            scena.use_flip_x =  scenb.use_flip_x
            
        def setupproxy(a, context):
            a.use_proxy = True
            if (eswc_info.pq == "1"):
                a.proxy.build_25 = True
            else:
                a.proxy.build_25 = False
            if (eswc_info.pq == "2"):
                a.proxy.build_50 = True
            else:
                a.proxy.build_50 = False
            if (eswc_info.pq == "3"):
                a.proxy.build_75 = True
            else:
                a.proxy.build_75 = False
            if (eswc_info.pq == "4"):
                a.proxy.build_100 = True
            else:
                a.proxy.build_100 = False
            a.use_proxy_custom_directory = True
            #blender file path
            file = bpy.data.filepath 
            name = new_name
            proxy_folder = bpy.path.abspath("//.proxy")
            new_folder = os.path.join(proxy_folder, name)
            rel_folder = bpy.path.relpath(new_folder)
            a.proxy.directory = rel_folder
            a.proxy.quality = 90 
        
        # Get selected strips, current scene, and
        # current camera, used for linking with other scenes 
        sel_strips = context.selected_sequences
        scene_name = context.scene.name
        cur_scene = bpy.data.scenes[context.scene.name]
        cur_camera = cur_scene.camera
        
        # Loop selected strips                         
        for strip in sel_strips:
        
            # Check if strip is a movie
            if strip.type == 'MOVIE' or 'IMAGE':
                # Creates new scene but doesn't set it as active.
                new_name = '{}{}'.format('Comp_', strip.name)
                new_scene = bpy.data.scenes.new(new_name)
                new_name = new_scene.name
                new_scene = bpy.data.scenes[new_scene.name]
                
                scn=context.scene
                eswc_info = scn.eswc_info
                
                #set comp_name
                new_scene.eswc_info.comp_name = strip.name
    
                # Change render settings for new scene to match original scene
                copyrendersettings(new_scene, cur_scene)
                
                
                
                # Setup new scene EndFrame to match strip length
                if eswc_info.preserveduration_bool == False:
                    new_scene.frame_start = 1
                    new_scene.frame_end = strip.frame_final_duration
                else:
                    
                    new_scene.frame_end = strip.frame_final_duration + \
                    strip.frame_offset_start + strip.frame_offset_end 
                
                #
                    
                # Setup nodes
                new_scene.use_nodes = True
                #copycomprendersettings(new_scene, cur_scene)
                tree = new_scene.node_tree
                
                # Clear default nodes
                for n in tree.nodes:
                    tree.nodes.remove(n)
                    
                # Create input node
                rl = tree.nodes.new('CompositorNodeImage')      
                rl.location = 0,0 
                
                if strip.type == 'IMAGE':
                    #Find extension
                    full_name = \
                            context.selected_sequences[0].elements[0].filename
                    full_name = strip.elements[0].filename
                    file_parts = os.path.splitext(full_name)
                    extension = file_parts[1]

                    #Get source of strip and add strip path
                    clean_path = bpy.path.abspath(strip.directory)
                    files = []
                    for i in os.listdir(clean_path):
                        if i.endswith(extension):
                            files.append(i)
                    path = os.path.join(clean_path, full_name)
                    #Check for existing image datablocks for this item
                    createnew=True
                    D=bpy.data
                    for i in D.images:
                        if i.name==full_name:
                            StripSource = bpy.data.images[full_name]
                            createnew=False
                    #or create a new one
                    if createnew:        
                        StripPath = bpy.path.resolve_ncase(path)
                        StripSource = D.images.load(StripPath)
                        StripSource.source = 'SEQUENCE'
                    rl.image = StripSource
                    
                    if len(strip.elements) == 1:
                        rl.image.source = 'IMAGE'
                    else:
                        rl.image.source = 'SEQUENCE'
                        rl.frame_duration = len(files) 
                        
                elif strip.type == 'MOVIE':
                    #Get source of strip and add strip path
                    StripPath = strip.filepath
                    filename = os.path.basename(StripPath)
                    
                    #Check for existing image datablocks for this item
                    createnew=True
                    D=bpy.data
                    #print(StripPath)
                    for i in D.images:
                        if i.filepath==StripPath:
                            StripSource = bpy.data.images[i.name]
                            createnew=False
                    #or create a new one
                    if createnew:
                        StripSource = bpy.data.images.load(StripPath)
                        StripSource.source = 'MOVIE'
                    rl.image = StripSource

                # Other input settings
                if eswc_info.preserveduration_bool == False:
                    rl.frame_duration = strip.frame_final_duration
                    rl.frame_offset = strip.frame_offset_start + \
                    strip.animation_offset_start
                else:
                    rl.frame_duration = strip.frame_final_duration + \
                    strip.frame_offset_start + strip.frame_offset_end + \
                    strip.animation_offset_end
                    rl.frame_offset = strip.animation_offset_start

                rl.use_cyclic = False
                rl.use_auto_refresh = True
                                
                # Update scene 
                new_scene.update()
                #StripSource.update()
                new_scene.frame_current = 2                
                
                # create scale node    
                if eswc_info.addscale_bool == True:
                    scale = tree.nodes.new('CompositorNodeScale')
                    scale.space = "RENDER_SIZE"
                    scale.location = 180,0
                    
                # create group node
                if eswc_info.addgroup_bool == True:
                    groupexists = False
                    nodegroup = ""
                    
                    for i, elem in enumerate(bpy.data.node_groups):
                        if i == int(eswc_info.enum_node_groups):
                            groupexists = True
                            nodegroup = elem
                            break
                    
                    if groupexists == True:
                        group = tree.nodes.new('CompositorNodeGroup')
                        group.node_tree = bpy.data.node_groups[nodegroup.name]
                        group.location = 350,0
                
                #
                #
                # create comp and viewer output node
                comp = tree.nodes.new('CompositorNodeComposite')   
                if eswc_info.addgroup_bool == True and groupexists == True:  
                    comp.location = 600,0
                else:
                    comp.location = 400,0
                if eswc_info.addviewer_bool == True:
                    viewer = tree.nodes.new('CompositorNodeViewer')
                    reroute = tree.nodes.new('NodeReroute')
                    if eswc_info.addgroup_bool == True and groupexists == True:  
                        reroute.location = 550,-150
                        viewer.location = 600,-200
                    else:
                        reroute.location = 350,-150
                        viewer.location = 400,-200

                # Link nodes
                links = tree.links
                if eswc_info.addviewer_bool == False:
                    if eswc_info.addgroup_bool and groupexists:  
                        if eswc_info.addscale_bool:
                            link = links.new(rl.outputs[0],scale.inputs[0]) 
                            link = links.new(scale.outputs[0],group.inputs[0]) 
                            link = links.new(group.outputs[0],comp.inputs[0])
                        else:    
                            link = links.new(rl.outputs[0],group.inputs[0]) 
                            link = links.new(group.outputs[0],comp.inputs[0]) 
                    else:
                        if eswc_info.addscale_bool:
                            link = links.new(rl.outputs[0],scale.inputs[0])
                            link = links.new(scale.outputs[0],comp.inputs[0])
                        else:
                            link = links.new(rl.outputs[0],comp.inputs[0])
                else:
                    link = links.new(reroute.outputs[0],viewer.inputs[0])   
                    link = links.new(reroute.outputs[0],comp.inputs[0]) 
                    if eswc_info.addgroup_bool == True and groupexists == True:  
                        if eswc_info.addscale_bool:
                            link = links.new(rl.outputs[0],scale.inputs[0]) 
                            link = links.new(scale.outputs[0], group.inputs[0])
                            link = links.new(group.outputs[0],reroute.inputs[0])   
                            
                        else:                    
                            link = links.new(rl.outputs[0],group.inputs[0])
                            link = links.new(group.outputs[0],reroute.inputs[0])      
                    else:
                        if eswc_info.addscale_bool:
                            link = links.new(rl.outputs[0],scale.inputs[0]) 
                            link = links.new(scale.outputs[0],reroute.inputs[0]) 
                        else:
                            link = links.new(rl.outputs[0],reroute.inputs[0]) 
       
                # Update scene 
                context.scene.update()

                # Create Marker
                if (eswc_info.preserveduration_bool == True):                  
                    bpy.ops.marker.add()
                    playhead = context.scene.frame_current
                    marker_offset = strip.frame_offset_start - playhead 
                    bpy.ops.marker.move(frames=marker_offset)
                    bpy.ops.marker.make_links_scene(scene=new_scene.name)
                    bpy.ops.marker.delete()

                
                # Change current scene to original                                    
                data_context = {"blend_data": context.blend_data, \
                                                scene_name: new_scene}
                context.screen.scene.update()
                
                channelincrease = eswc_info.channelincrease           
                
                # Add newly created scene       
                if eswc_info.preserveduration_bool == False:            
                    bpy.ops.sequencer.scene_strip_add(
                    frame_start=strip.frame_start, 
                    channel=strip.channel + channelincrease, 
                    replace_sel=False, scene=new_scene.name)           
                else:
                    bpy.ops.sequencer.scene_strip_add(
                    frame_start=strip.frame_start, 
                    channel=strip.channel + channelincrease, 
                    replace_sel=False, scene=new_scene.name)
                               
                #Copy Settings
                settings = eswc_info.settings
                
                # make new strip active
                context.scene.sequence_editor.active_strip = \
                    bpy.data.scenes[scene_name].sequence_editor.\
                    sequences_all[new_scene.name]
                newstrip = context.scene.sequence_editor.active_strip
                
                # deselect all other strips
                for i in context.selected_editable_sequences:
                    if i.name != newstrip.name:
                        i.select=False
                
                # Update scene 
                context.scene.update()
                
                #Camera override
                newstrip.scene_camera = cur_camera
                
                #Match the original clip's length 
                if eswc_info.preserveduration_bool == False:
                    newstrip.frame_start = strip.frame_start + \
                                            strip.frame_offset_start
                    newstrip.frame_final_duration = strip.frame_final_duration 
                    newstrip.animation_offset_start = 0
                    newstrip.animation_offset_end = 0
                else:
                    triminout(newstrip, 
                        strip.frame_start + strip.frame_offset_start, 
                        strip.frame_start + strip.frame_offset_start + \
                        strip.frame_final_duration)
                    pass
                 
                context.scene.update() 
                 
                #Save the strip's master scene
                bpy.data.scenes[new_name].eswc_info.master_scene = scene_name
                                                               
                if (settings == "All"):
                    a = bpy.data.scenes[scene_name].\
                                sequence_editor.sequences[new_name]
                    b = bpy.data.scenes[scene_name].\
                                sequence_editor.sequences_all[strip.name]
                    copyallsettings(a, b)
                
                
                if (eswc_info.autoproxy_bool == True):                    
                    a = bpy.data.scenes[scene_name].\
                                sequence_editor.sequences[new_name]
                    setupproxy(a, context)
                
            else:
                print("Active Strip is not a movie or an image sequence.")

        return {'FINISHED'}


 
 
 
def register():

    bpy.utils.register_module(__name__)
    
    # eswc_info
    bpy.types.Scene.eswc_info = PointerProperty(type=ESWC_Info)
    

    
 
def unregister():

    bpy.utils.unregister_module(__name__)
    
    # eswc_info
    del bpy.types.Scene.eswc_info

 
if __name__ == "__main__":
    register()
    
    
 