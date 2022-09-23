# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; version 2
#  of the License.
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


#######################################################

## KeepAChangeLog
##
## Nore Presets
##
## v0.1.5.1 - 2022-09-23
## Added
## - Opening preferences from Extras menu open addon expandded
## Fixed
## - Fix error report messages

## v0.1.5 - 2022-09-13
## Added
## - Prefix to list items so they are stored and can be customized
## - Shortcut for save action and return action
## - Error report when base files isnt setup properly for adding node groups

### Fixed
## - Saving wolrd note caused error due to wwrong node_tree check space_data
## - Reports when operator can not place node group due to error. Added better reports as well
## - Issue not using categories. 22-09-2022
## - Add prefix operator, now checks world or material
## - Checks if node tree is

## v0.1.4
## Fixed
## 22-05-09 - Issue with template in panel, suddenly wont show. np_preset_files keeps being 0 because its never called. Used to work fine
## 22-05-10 - Checking modifiers, active is not supported with bl.2.83
## 22-05-18 - Fixed add issue with not support node tree, #295

## v0.1.3
## Added
## 22-05-05 - When placing NodeGroup, remove prefix

## v0.1.2
## Changed
## 22-02-09 - Initial release updated addon

#######################################################

'''

TODO

22-09-2022
- Clean code of Persisten, reuse checks using single functions

21-09-2022
- Make columns for node preset when saved

14-09-2022
- Add check for hat type of node are saved to what files. Somehow need to check when shader nodes are saved to world or environment blend files

V Check how to make better filtered menus usign categories
  ^  def draw_node_categories_menu(self, context):
        for cats in _node_categories.values():
        cats[1](self, context)
- Add nodes lights as well
V Check if geometry node groups work
- Add function which switches to object which needs to get the nodegroup
^ This way can neatly store the nodegroups
V Make it work with automated grouping and using preset popup. That way user keeps its original node layout and doesnt need to ungroup if needed
V Expand preset files to only show those NodeGroups. This allows for large setups and better organizing methods
- Add preference file locator, also add prefix to those files for the category system
^ Look at Save_Cams addon to proper UIlist implementation

2022-02-11
- Fix reload mechanism, with categories a file needs to opene or close. Neeeds to be called from menu operator

2022-02-17
- make main Menu Operator 1 operator

'''


bl_info = {
    "name": "Node Presets",
    "description": "Useful and time-saving tools for node group workflow. Add node groups directly to the node editors",
    "author": "Campbell Barton, Rombout Versluijs",
    "version": (0, 1, 51),
    "blender": (2, 80, 0),
    "location": "Node Editors > Add > Template",
    "doc_url": "{BLENDER_MANUAL_URL}/addons/node/node_presets.html",
    "wiki_url": "https://github.com/schroef/node-presets/",
	"tracker_url": "https://github.com/schroef/node-presets/issues",
    "category": "Node",
}


import bpy
import subprocess, os
import rna_keymap_ui
from sys import platform
from bpy.app.handlers import persistent
from bpy.props import (
        BoolProperty,
        CollectionProperty,
        EnumProperty,
        IntProperty,
        PointerProperty,
        StringProperty,
        )
from bpy.types import (
        AddonPreferences, 
        Menu,
        Operator, 
        PropertyGroup, 
        UIList, 
        Panel, 
    )
import logging


# return addon preferences
def get_addon_prefs(context):
    return context.preferences.addons[__name__].preferences

def update_np_settings():
    if bpy:
        bpy.ops.wm.save_userpref()

def get_preset_files(templateFolder):
    addon_prefs = get_addon_prefs(bpy.context)
    addon_prefs.np_preset_files.clear()
    for file_path in os.listdir(templateFolder):
#        print(file_path.lower().endswith('.blend'))
        if file_path.lower().endswith('.blend'):
            try:
                item = addon_prefs.np_preset_files.add()
                item.name = str(file_path)[:-6]
                # print(item.name)
            except:
                print ("Couldn't open file")       


logger = logging.getLogger('save_node_presets')


class NP_OT_ErrorDialog(Operator):
    """Add a node template"""
    bl_idname = "node.error_dialog"
    bl_label = "Error Dialog Node Groups"
    bl_description = "Callable Error Dialog"

    # message : StringProperty()

    def execute(self, context):
        addon_prefs = get_addon_prefs(context)
        np_settings = addon_prefs.node_preset_settings
        self.report({'ERROR'}, np_settings["error_messages"])
        return {'FINISHED'}

    # def invoke(self, context, event):
    #     wm = context.window_manager
    #     return wm.invoke_props_dialog(self)


@persistent
def open_nodepresets_check(context):
    if bpy:
        try:
            addon_prefs = bpy.context.preferences.addons[__name__].preferences
            # addon_prefs = get_addon_prefs(context)
            np_settings = addon_prefs.node_preset_settings
            np_settings["use_categories"]==""
            if addon_prefs.use_categories and (os.listdir(addon_prefs.search_path)):
                get_preset_files(addon_prefs.search_path)
                global np_cat_list
                global np_blend_categories
                get_blend_nodegroups(context,dirpath=addon_prefs.search_path)
                np_cat_list = gen_categories()
            else:
                get_preset_files(addon_prefs.search_path)
        except:
            pass
            # import traceback
            # print(traceback.print_exc())

        if np_settings["preset_file"] != "":
            if os.path.samefile(np_settings["preset_file"], bpy.data.filepath):
                # logger.info("Editing a node preset.")
                ob = bpy.context.object

                if not np_settings["edit_preset"]:
                    # source: https://blender.stackexchange.com/questions/147488/load-and-change-material-with-python-script
                    # with bpy.data.libraries.load(targetpath, link=False) as (data_from, data_to):
                    with bpy.data.libraries.load(np_settings["original_file"], link=False) as (data_from, data_to):
                        # data_to.materials = [np_settings["mat_name"]]
                        data_to.node_groups = [np_settings["node_group"]]
                        # data_to.materials = [node_preset_settings["node_group"]]
                    
                    # switch to the correct workspace
                    bpy.context.window.workspace = bpy.data.workspaces[np_settings["workspace"]]
                    
                    # space = context.space_data
                    # print(space.node_tree)
                    # node_tree = space.node_tree

                    # check shader_type
                    # https://blender.stackexchange.com/questions/137844/changing-the-shading-type-in-python
                    for area in bpy.context.screen.areas: 
                        # print(area.type)
                        if area.type == 'NODE_EDITOR':
                            for space in area.spaces: 
                                print(space.shader_type)
                                print(space.type)
                                shader_type = space.shader_type
                                if space.type == 'NODE_EDITOR':
                                    # space.shader_type = 'MATERIAL'
                                    print(space.shader_type)

                    # print("World %s" % np_settings["world_name"])
                    # print("world_name %s" % np_settings["world_name"])
                    # print("ob %s" % ob)
                    # print("use_categories %s" % np_settings["use_categories"])

                    #info add nodes
                    # https://docs.blender.org/api/current/bpy.types.NodeTree.html#bpy.types.NodeTree
                    # use_categories check
                    if addon_prefs.use_categories:
                        if np_settings["node_type"] == 'ShaderNodeTree':
                            if not ob and (addon_prefs.use_categories==True):
                                np_settings["error_messages"] = "No Object with Material to save Node Preset"
                                return
                            if ob and (np_settings["world_name"]==""):
                                if not bpy.context.active_object.active_material:
                                    np_settings["error_messages"] = "No node tree available"
                                    return
                                # Needs better checking for world or material shader
                                if ob.type != 'LIGHT':
                                    nt = bpy.context.active_object.active_material.node_tree.nodes
                                    node_1 = nt.new("ShaderNodeGroup")
                                if ob.type == 'LIGHT':
                                    nt = bpy.context.active_object.data.node_tree.nodes
                                    node_1 = nt.new("ShaderNodeGroup")
                        
                                if ob.modifiers:
                                    if ob.modifiers.active.type == 'NODES':
                                        # nt = bpy.context.active_object.modifiers.active.node_group.nodes.active.node_tree.name
                                        nt = bpy.context.active_object.modifiers.active.node_group.nodes
                                        node_1 = nt.new("GeometryNodeGroup")

                            else:
                                world = bpy.context.scene.world
                                if not world or not world.node_tree.nodes:
                                    np_settings["error_messages"] = "No Node Tree in world available"
                                    return
                                if np_settings["world_name"]:
                                    nt = world.node_tree.nodes #.active.node_tree
                                    node_1 = nt.new("ShaderNodeGroup")
                                    
                        if np_settings["node_type"] == 'CompositorNodeTree':
                            nt = bpy.context.scene.node_tree.nodes
                            node_1 = nt.new("CompositorNodeGroup")
                    
                    # No use_categories
                    if not addon_prefs.use_categories:
                        if shader_type == 'OBJECT':
                            if not ob:
                                np_settings["error_messages"] = "No Object with Material to save Node Preset"
                                return
                            if not bpy.context.active_object.active_material:
                                np_settings["error_messages"] = "No node tree available"
                                return
                            if np_settings["node_type"] == 'ShaderNodeTree':
                                if ob.type != 'LIGHT':
                                    nt = bpy.context.active_object.active_material.node_tree.nodes
                                    node_1 = nt.new("ShaderNodeGroup")
                                if ob.type == 'LIGHT':
                                    nt = bpy.context.active_object.data.node_tree.nodes
                                    node_1 = nt.new("ShaderNodeGroup")
                            if ob.modifiers:
                                if ob.modifiers.active.type == 'NODES':
                                    nt = bpy.context.active_object.modifiers.active.node_group.nodes
                                    node_1 = nt.new("GeometryNodeGroup")

                            if np_settings["node_type"] == 'CompositorNodeTree':
                                nt = bpy.context.scene.node_tree.nodes
                                node_1 = nt.new("CompositorNodeGroup")
                        if shader_type == 'WORLD':
                            world = bpy.context.scene.world
                            if not world or not world.node_tree.nodes:
                                np_settings["error_messages"] = "No Node Tree in world available"
                                return
                            
                            nt = world.node_tree.nodes #.active.node_tree
                            node_1 = nt.new("ShaderNodeGroup")

                    anode = nt.active
                    bpy.data.node_groups[np_settings["node_group"]].use_fake_user = True
                    node_1.node_tree = bpy.data.node_groups[np_settings["node_group"]]
                    if nt.active is not None:
                        node_1.location = ((anode.location.x + anode.width)+50,anode.location.y)
                    else:
                        node_1.location = (0,0)
                    if anode is not None:
                        anode.select = False
                    node_1.select = True
                    nt.active = node_1
                    
                    # This returns area since UI isnt ready yet, not sure why
                    # print("sleep")
                    # import time
                    # time.sleep(2)
                    # area = bpy.context.area
                    # # old_type = area.type
                    # area.type = 'NODE_EDITOR'
                    # # bpy.ops.node.view_selected()
                    # bpy.ops.node.view_all()
                    # # try:
                    # # except:
                    # #     pass

                    if addon_prefs.auto_close:
                        bpy.ops.nodes.return_to_original()

            else:
                # logger.info("Reset paths and filenames")
                
                # For some reason, the linked editing session ended
                # (failed to find a file or opened a different file
                # before returning to the originating .blend)
                np_settings["original_file"] = ""
                np_settings["preset_file"] = ""
                np_settings["node_type"] = ""
                np_settings["node_group"] = ""
                np_settings["mat_name"] = ""
                np_settings["world_name"] = ""
                np_settings["workspace"] = ""
                np_settings["edit_preset"] = False
                np_settings["error_messages"] = ""



# -----------------------------------------------------------------------------
# Node Adding Operator

def node_center(context):
    from mathutils import Vector
    loc = Vector((0.0, 0.0))
    node_selected = context.selected_nodes
    if node_selected:
        for node in node_selected:
            loc += node.location
        loc /= len(node_selected)
    return loc


def node_template_add(context, filepath, node_group, ungroup, report, space):
    """ Main function"""
    
    space = context.space_data
    node_tree = space.node_tree
    node_active = context.active_node
    node_selected = context.selected_nodes

    if node_tree is None:
        report({'ERROR'}, "No node tree available")
        return

    with bpy.data.libraries.load(filepath, link=False) as (data_from, data_to):
        assert(node_group in data_from.node_groups)
        data_to.node_groups = [node_group]
    node_group = data_to.node_groups[0]

    # add node!
    # center = node_center(context)
    # new method
    # space.cursor_location = store_mouse_cursor(event, context)

    for node in node_tree.nodes:
        node.select = False

    node_type_string = {
        "ShaderNodeTree": "ShaderNodeGroup",
        "GeometryNodeTree": "GeometryNodeGroup",
        "CompositorNodeTree": "CompositorNodeGroup",
        "TextureNodeTree": "TextureNodeGroup",
    }[type(node_tree).__name__]

    node = node_tree.nodes.new(type=node_type_string)
    node.node_tree = node_group

    is_fail = (node.node_tree is None)
    if is_fail:
        report({'WARNING'}, "Incompatible node type")

    node.select = True
    node_tree.nodes.active = node
    # node.location = center
    # mew method
    # addon_prefs = context.preferences.addons['node_presets_v004'].preferences
    # if addon_prefs.auto_ungroup:
    #     node.location = space.cursor_location#(space.cursor_location.x + 200, space.cursor_location.y)
    # else:
    node.location = space.cursor_location

    if is_fail:
        node_tree.nodes.remove(node)
    else:
        if ungroup:
            bpy.ops.node.group_ungroup()

        nt = node.node_tree
        
        # Remove prefix
        if nt.type == 'SHADER':
            if nt.name[0:3] == 'SH_':
                nt.name = nt.name[3:] 

        if nt.type == 'COMPOSITING':
            if nt.name[0:3] == 'CP_':
                nt.name = nt.name[3:] 

        if nt.type == 'GEOMETRY':
            if nt.name[0:3] == 'SH_':
                nt.name = nt.name[3:] 
    # node_group.user_clear()
    # bpy.data.node_groups.remove(node_group)


# -----------------------------------------------------------------------------
# Node Template Add

class NODE_OT_template_add(Operator):
    """Add a node template"""
    bl_idname = "node.template_add"
    bl_label = "Add node group template"
    bl_description = "Add node group template"
    bl_options = {'REGISTER', 'UNDO'}

    use_transform: BoolProperty(
        name="Use Transform",
        description="Start transform operator after inserting the node",
        default=False,
    )
    
    filepath: StringProperty(
        subtype='FILE_PATH',
    )
    group_name: StringProperty()

    # from node.py
    @staticmethod
    def store_mouse_cursor(context, event):
    # def store_mouse_cursor(event, context):
        space = context.space_data
        tree = space.edit_tree

        # convert mouse position to the View2D for later node placement
        if context.region.type == 'WINDOW':
            # convert mouse position to the View2D for later node placement
            space.cursor_location_from_region(event.mouse_region_x, event.mouse_region_y)
        else:
            space.cursor_location = tree.view_center


    def execute(self, context):
        space = context.space_data
        node_tree = space.node_tree
        node_active = context.active_node
        node_selected = context.selected_nodes

        if node_tree is None:
            self.report({'ERROR'}, "No node tree available")
            return {'CANCELLED'}
        else:
            node_template_add(context, self.filepath, self.group_name, True, self.report, space)

            return {'FINISHED'}

    def invoke(self, context, event):
        addon_prefs = get_addon_prefs(context)
        space = context.space_data
        node_tree = space.node_tree
        node_active = context.active_node
        node_selected = context.selected_nodes

        if node_tree is None:
            self.report({'ERROR'}, "No node tree available")
            return {'CANCELLED'}
        else:
            self.store_mouse_cursor(context, event)
            node_template_add(context, self.filepath, self.group_name, addon_prefs.auto_ungroup, self.report, space)


        # Perhaps handy, this ungroups the store group, could be nice!
        # result = self.execute(context)
        
        # if self.use_transform and ('FINISHED' in result):
        if addon_prefs.use_transform:
            # removes the node again if transform is cancelled
            bpy.ops.node.translate_attach_remove_on_cancel('INVOKE_DEFAULT')

        return {'FINISHED'}


# -----------------------------------------------------------------------------
# Node menu list

def node_template_cache(context, *, reload=False):
    dirpath = node_search_path(context)

    # Force reload, we dont want cache. if we remove files we dont see until blender restarts
    # if node_template_cache._node_cache_path != dirpath:
    reload = True

    node_cache = node_template_cache._node_cache
    if reload:
        node_cache = []
    if node_cache:
        return node_cache

    for fn in os.listdir(dirpath):
        if fn.endswith(".blend"):
            filepath = os.path.join(dirpath, fn)
            with bpy.data.libraries.load(filepath) as (data_from, data_to):
                for group_name in data_from.node_groups:
                    if not group_name.startswith("_"):
                        node_cache.append((filepath, group_name))

    node_template_cache._node_cache = node_cache
    node_template_cache._node_cache_path = dirpath

    return node_cache


node_template_cache._node_cache = []
node_template_cache._node_cache_path = ""


class NODE_MT_template_add(Menu):
    bl_label = "Node Template"

    def draw(self, context):
        layout = self.layout

        dirpath = node_search_path(context)
        # print("dirpath %s" % dirpath)
        try:
            os.listdir(dirpath)
            pass
        except:
            layout.label(text="Can't find template folder", icon='ERROR')
            return
        if check_search_path(context):
            layout.label(text="Template folder is empty", icon='INFO')
            return
        if dirpath == "":
            layout.label(text="Set search dir in the addon-prefs", icon='INFO')
            return
        try:
            node_items = node_template_cache(context)
        except Exception as ex:
            node_items = ()
            layout.label(text=repr(ex), icon='ERROR')

        for filepath, group_name in node_items:
            # print(group_name[2:3])
            if group_name[2:3] == '_':
                if group_name[0:3] == 'SH_':
                    iconType = 'NODE_MATERIAL'
                if group_name[0:3] == 'CP_':
                    iconType = 'NODE_COMPOSITING'
                if group_name[0:3] == 'GN_':
                    iconType = 'NODETREE'
                if group_name[0:3] == 'TX_':
                    iconType = 'NODE_TEXTURING'
    #            ng.name = 'SH_' + ng.name 
                groupName = group_name[3:]
            else:
                groupName = group_name
                iconType = 'NONE'

            props = layout.operator(
                NODE_OT_template_add.bl_idname,
                text=groupName, icon = iconType
            )
            props.filepath = filepath
            props.group_name = group_name


def add_node_button(self, context):
    self.layout.menu(
        NODE_MT_template_add.__name__,
        text="Node Presets",
        icon='PLUGIN',
    )

# -----------------------------------------------------------------------------
# Node add to template operators & functions

class NP_OT_EditNodeGroup(Operator):
    """Edit Node Group"""
    bl_idname = "nodes.edit_node_group"
    bl_label = "Edit a Node Group"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        snode = context.space_data
        addon_prefs = get_addon_prefs(context)
        np_settings = addon_prefs.node_preset_settings
        
        targetpath = get_addon_prefs(context)['search_path']
        if targetpath:
            # logger.debug(target.name + " is linked to " + targetpath)

            np_settings["original_file"] = bpy.data.filepath
            addon_prefs.np_list_index = 0 if len(addon_prefs.np_preset_files) <= 1 else addon_prefs.np_list_index
            preset_file_blend = addon_prefs.np_preset_files[addon_prefs.np_list_index]['name']
            np_settings["preset_file"] = bpy.path.abspath(targetpath+str(preset_file_blend)+".blend")
            
            np_settings["edit_preset"] = True
            bpy.ops.wm.save_mainfile()
            # Opens file inside open blender
            bpy.ops.wm.open_mainfile(filepath=np_settings["preset_file"])
            

            # logger.info("Opening preset file")
            self.report({'INFO'}, "Opening preset file")
        else:
            self.report({'WARNING'}, "File  does not excist")
            # logger.warning(target.name + " is not linked")

        return {'FINISHED'}


class NP_OT_SaveNodeGroup(Operator):
    """Save NodeGroup to the selected template blend file. Template will be opened and NoeGroup will be saved to that Blend. Use the setting "Auto Close" sto aumate the process completely."""
    bl_idname = "nodes.save_node_group"
    bl_label = "Save NodeGroup"
    bl_options = {'REGISTER', 'UNDO'}

    name: bpy.props.StringProperty()
    # use_instance: bpy.props.BoolProperty(
    #         name="New Blender Instance",
    #         description="Open in a new Blender instance",
    #         default=False)

    # @classmethod
    # def poll(cls, context):
    #     return bpy.data.filepath != '':
    #     return node_preset_settings["original_file"] == "" and context.active_object is not None and (
    #             (context.active_object.instance_collection and
    #             context.active_object.instance_collection.library is not None) or
    #             (context.active_object.proxy and
    #             context.active_object.proxy.library is not None) or
    #             context.active_object.library is not None)

    def execute(self, context):
        scene = context.scene
        ob = context.object
        snode = context.space_data
        addon_prefs = get_addon_prefs(context)
        np_settings = addon_prefs.node_preset_settings
        # if snode.tree_type == 'ShaderNodeTree':
        #     if snode.shader_type == 'WORLD':
        #         target = context.scene.world
        #         nodeName = context.scene.world.node_tree.nodes.active.node_tree.name
        #     if snode.shader_type == 'OBJECT':
        #         target = context.active_object
        #         nodeName = target.active_material.node_tree.nodes.active.node_tree.name
        # if snode.tree_type == 'CompositorNodeTree':
        #     target = context.scene.node_tree.nodes.active
        #     nodeName = target.node_tree.name
        
        # Easier method of getting active node
        target = context.active_node
        # print("target %s" % target)
        nodeName = target.node_tree.name
        # print("nodeName %s" % nodeName)


        targetpath = get_addon_prefs(context)['search_path']
        if targetpath:
            # logger.debug(target.name + " is linked to " + targetpath)

            np_settings["original_file"] = bpy.data.filepath
            # print("NP file idnex %s" % addon_prefs.np_list_index)
            addon_prefs.np_list_index = 0 if len(addon_prefs.np_preset_files) <= 1 else addon_prefs.np_list_index
            preset_file_blend = addon_prefs.np_preset_files[addon_prefs.np_list_index]['name']
            np_settings["preset_file"] = bpy.path.abspath(targetpath+str(preset_file_blend)+".blend")
            
            # print("target %s" % target)
            np_settings["node_group"] = nodeName # takes node group name
            np_settings["node_type"] = snode.tree_type # Todo check if its material or comp node
            np_settings["workspace"] = bpy.context.window.workspace.name
            np_settings["edit_preset"] = False
            if snode.tree_type == 'ShaderNodeTree':
                if snode.shader_type == 'WORLD':
                    np_settings["world_name"] = target.name
                if snode.shader_type == 'OBJECT' and ob.type != 'LIGHT':    
                    np_settings["mat_name"] = context.active_object.active_material.name
                if snode.shader_type == 'OBJECT' and ob.modifiers:
                    # bpy.context.active_object.modifiers.active.node_group.nodes.active.node_tree.name
                    # We need to loop over modifiers
                    for mod in ob.modifiers:    
                        if mod.type == 'NODES':
                            np_settings["geon_name"] = context.active_object.modifiers.active.node_group.nodes.active.node_tree.name
            # print(targetpath)

            if addon_prefs.use_instance:
                bpy.ops.wm.save_mainfile()
                # Opens new blender instance
                import subprocess
                subprocess.Popen([bpy.app.binary_path, np_settings["preset_file"]])
            #     import subprocess
            #     try:
            #         subprocess.Popen([bpy.app.binary_path, node_preset_settings["preset_file"]])
            #     except:
            #         logger.error("Error on the new Blender instance")
            #         import traceback
            #         logger.error(traceback.print_exc())
            else:
                # print("bpy.data.filepath %s" % (bpy.data.filepath == ''))
                # Check if file is saved already if not present filebrowser dialog to save
                # if bpy.data.filepath != '':
                if bpy.data.filepath == '':
                    self.report({'WARNING'}, " Please save file first, run Save NodeGroup again whenn done.")
                    # bpy.ops.wm.save_mainfile('INVOKE_AREA')
                    # print("saving")
                    return {'CANCELLED'}
                    # return {'CANC'}
                else:
                    # Opens file inside open blender
                    bpy.ops.wm.save_mainfile()

                bpy.ops.wm.open_mainfile(filepath=np_settings["preset_file"])
            

            print("np_settings %s" % np_settings)
            print("np_settings error_messages %s" % np_settings["error_messages"])
            if np_settings["error_messages"] != "":
                self.report({'ERROR'}, np_settings["error_messages"])    
                return {'CANCELLED'}
            # logger.info("Opening preset file")
            self.report({'INFO'}, "Opening preset file")
        else:
            # logger.warning(target.name + " is not linked")
            self.report({'WARNING'}, target.name + " is not linked")

        return {'FINISHED'}

    # def invoke(self, context, event):
    #     print(bpy.data.filepath == '')
    #     if bpy.data.filepath == '':
    #         print("save as")
    #         bpy.ops.wm.save_as_mainfile('INVOKE_AREA')
    #     return self.execute(context)


class NP_OT_ReturnToOriginal(Operator):
    """Load the original file"""
    bl_idname = "nodes.return_to_original"
    bl_label = "Return to Original File"
    bl_options = {'REGISTER', 'UNDO'}

    name: bpy.props.StringProperty()

    @classmethod
    def poll(cls, context):
        addon_prefs = get_addon_prefs(context)
        return (addon_prefs.node_preset_settings["original_file"] != "")

    def execute(self, context: bpy.context):
        # addon_prefs = context.preferences.addons[__name__].preferences
        addon_prefs = get_addon_prefs(context)
        np_settings = addon_prefs.node_preset_settings
        # addon_prefs = context.preferences.addons['node_presets_v002'].preferences
        # if self.use_autosave:
        bpy.ops.wm.save_mainfile()

        bpy.ops.wm.open_mainfile(filepath=np_settings["original_file"])

        np_settings["original_file"] = ""
        # settings["linked_objects"] = []
        # logger.info("Back to the original!")
        return {'FINISHED'}


# -----------------------------------------------------------------------------
# Rename Operator

        
class NP_OT_AutoRenameShaders(Operator):
    """Add dn Remove Prefix to NodeGroups so icons show in the Add Menu. This helps distinguish the different NodeGroups more easily. It also helps organising them, they are catergoeizes by Composite NodeGroups, Shader NodeGroups and Geometry NodeGroups."""
    bl_idname = "node.np_auto_rename"
    bl_label = "Auto Rename"
    bl_options = {'REGISTER', 'UNDO'}

    remove_prefix: BoolProperty(
        default=False
    #        options={'HIDDEN', 'SKIP_SAVE'},
    )
    add_prefix: BoolProperty(
        default=False
    #        options={'HIDDEN', 'SKIP_SAVE'},
    )

    @classmethod
    def poll(cls, context):
        addon_prefs = get_addon_prefs(context)
        np_settings = addon_prefs.node_preset_settings
        # print(addon_prefs.preset_file)
    #    return context.active_object is not None 
        return np_settings["preset_file"] != ""

    def execute(self, context):
        ob = bpy.context.active_object
        snode = bpy.context.space_data
        # if ob.type != 'LIGHT':
        #     mat = ob.active_material
        #     anode = mat.node_tree.nodes.active
        # else:
        #     anode= ob.data.node_tree.nodes.active
        #print(anode.node_tree.type)
        # print(snode.tree_type)
        # print(snode.shader_type)   
        # if snode.tree_type == 'ShaderNodeTree':
        #     if snode.shader_type == 'WORLD':
        #         print(snode.shader_type)     
        #     if snode.shader_type == 'OBJECT':
        #         print(snode.shader_type)
        #     if snode.tree_type == 'CompositorNodeTree':
        #         print(snode.shader_type)
        #         print("compostir")
                
        for ng in bpy.data.libraries.data.node_groups:
            print(ng.type)
            print(ng.type)
            # if snode.shader_type == 'WORLD':
            if ng.type == 'SHADER':
                if snode.shader_type == 'MATERIAL':
                    if self.add_prefix:
                        if ng.name[0:3] != 'SH_':
                            ng.name = 'SH_' + ng.name 
                    if self.remove_prefix:
                        if ng.name[0:3] == 'SH_':
                            ng.name = ng.name[3:] 

                if snode.shader_type == 'WORLD':
                    if self.add_prefix:
                        if ng.name[0:3] != 'CP_':
                            ng.name = 'CP_' + ng.name 
                    if self.remove_prefix:
                        if ng.name[0:3] == 'CP_':
                            ng.name = ng.name[3:] 

            if ng.type == 'COMPOSITING':
                if self.add_prefix:
                    if ng.name[0:3] != 'CP_':
                        ng.name = 'CP_' + ng.name 
                if self.remove_prefix:
                    if ng.name[0:3] == 'CP_':
                        ng.name = ng.name[3:] 
            
            if ng.type == 'GEOMETRY':
                if self.add_prefix:
                    if ng.name[0:3] != 'GN_':
                        ng.name = 'GN_' + ng.name 
                if self.remove_prefix:
                    if ng.name[0:3] == 'SH_':
                        ng.name = ng.name[3:] 
        
        return {'FINISHED'}


# -----------------------------------------------------------------------------
# UIlist Preset blend selector

class NP_PG_Preset_Items(PropertyGroup):
    """Group of properties representing an item in the list."""

    name: StringProperty(
           name="Name",
           description="A name for this item",
           default="Untitled"
           )

    random_prop: StringProperty(
           name="Any other property you want",
           description="",
           default=""
           )
    
    prefix: StringProperty(
           name="Prefix node group type",
           description="",
           default=""
           )


class NP_UL_List(UIList):
    """Example UIList."""

    def draw_item(self, context, layout, data, item, icon, active_data,
                  active_propname, index):
        # self.use_filter_show = True
        # We could write some code to decide which icon to use here...
        custom_icon = 'FILE_BLEND'

        # Make sure your code supports all 3 layout types
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.label(text=item.name, icon = custom_icon)

        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="", icon = custom_icon)


class NP_OT_MoveItem(Operator):
    """Move an item in the list."""

    bl_idname = "nodes.np_move_item"
    bl_label = "Move an item in the list"

    direction: bpy.props.EnumProperty(items=(('UP', 'Up', ""),
                                              ('DOWN', 'Down', ""),))

    @classmethod
    def poll(cls, context):
        # return context.scene.np_preset_files
        addon_prefs = get_addon_prefs(context)
        return addon_prefs.np_preset_files

    def move_index(self, context):
        """ Move index of an item render queue while clamping it. """

        addon_prefs = get_addon_prefs(context)
        index = addon_prefs.np_list_index
        
        list_length = len(addon_prefs.np_preset_files) - 1  # (index starts at 0)
        new_index = index + (-1 if self.direction == 'UP' else 1)

        addon_prefs.np_list_index = max(0, min(new_index, list_length))

    def execute(self, context):
        addon_prefs = get_addon_prefs(context)
        np_preset_files = addon_prefs.np_preset_files
        index = addon_prefs.np_list_index

        neighbor = index + (-1 if self.direction == 'UP' else 1)
        np_preset_files.move(neighbor, index)
        self.move_index(context)

        return{'FINISHED'}



# -----------------------------------------------------------------------------
# Add keymap

addon_keymaps = []

def add_hotkey():
    # preferences = bpy.context.preferences
    # addon_prefs = preferences.addons[__name__].preferences

    # print("HOTKEY added")
    # Use alt or cmd for windows and osx
    cmdK = False if platform == "win32" else True
    altK = True if platform == "win32" else False

    # print("QS hotkeys added")
    wm = bpy.context.window_manager

    kc = wm.keyconfigs.addon    # for hotkeys within an addon
    km = kc.keymaps.new(name="Node Editor", space_type="NODE_EDITOR")

    #Add save nodegrous
    kmi = km.keymap_items.new("nodes.save_node_group",  value='PRESS', type='BACK_SLASH', ctrl=False, alt=altK, shift=False, oskey=cmdK)
    kmi.properties.name = "NP_OT_SaveNodeGroup"
    kmi.active = True
    addon_keymaps.append((km, kmi))
    
    #Return to original file
    kmi = km.keymap_items.new("nodes.return_to_original",  value='PRESS', type='BACK_SLASH', ctrl=False, alt=altK, shift=False, oskey=cmdK)
    kmi.properties.name = "NP_OT_ReturnToOriginal"
    kmi.active = True
    addon_keymaps.append((km, kmi))



# -----------------------------------------------------------------------------
# Node Template Prefs

def get_hotkey_entry_item(km, kmi_name, kmi_value, properties):
    '''
    returns hotkey of specific type, with specific properties.name (keymap is not a dict, so referencing by keys is not enough
    if there are multiple hotkeys!)
    '''

    for i, km_item in enumerate(km.keymap_items):
        if km.keymap_items.keys()[i] == kmi_name:
            if properties == 'name':
                if km.keymap_items[i].properties.name == kmi_value:
                    return km_item
            try:
                if km.keymap_items[i].properties.name == kmi_value:
                    # print(properties)
                    # print(km.keymap_items[i].properties.layoutName)
                    # print(km.keymap_items[i].properties.wslayoutMenu)
                    # print("\n\n")
                    # print("%s - %s" % (km.keymap_items[i].properties.layoutName, kmi_value))
                    return km_item
            except:
                pass
    return None # not needed, since no return means None, but keeping for readability


class NP_OT_OpenPrefs(Operator):
    """Edit Node Group"""
    bl_idname = "nodes.open_prefs"
    bl_label = "Open Preferences"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        bpy.ops.screen.userpref_show('INVOKE_DEFAULT')
        # Go to Quickswitch addon
        bpy.context.preferences.active_section = 'ADDONS'
        bpy.context.window_manager.addon_search = 'node presets'

        # https://blender.stackexchange.com/questions/230698/question-about-managing-the-preferences-window-python
        # Show expanded
        import addon_utils
        module_name = "node_presets"
        bpy.ops.preferences.addon_expand(module=module_name)# get_addon_name() it is a small function that returns the name of the addon (For my convenience)
        bpy.ops.preferences.addon_show(module=module_name) # Show my addon pref

        # force panel redraw
        context.area.tag_redraw()

        return {'FINISHED'}

def check_search_path(context):
    # preferences = context.preferences
    # addon_prefs = preferences.addons[__name__].preferences
    dirpath = node_search_path(context)
    files = []
    if dirpath:
        for fn in os.listdir(dirpath):
            if fn.endswith(".blend"):
                filepath = os.path.join(dirpath, fn)
                # Strip *.blend
                fn = fn[:-6]
                files.append(fn)
        return len(files) == 0

def update_use_categories(self, context):
    # preferences = context.preferences
    # addon_prefs = preferences.addons[__name__].preferences
    addon_prefs = get_addon_prefs(context)
    np_settings = addon_prefs.node_preset_settings
    # print(self.use_categories)
    if self.use_categories or not self.use_categories and (np_settings["use_categories"]=="False"):
        np_settings["use_categories"] = "True"
        addon_prefs.info_messages = "Restart needed in order to update menus."
    
    if not self.use_categories:
        addon_prefs.node_preset_settings["use_categories"] = "False"
        addon_prefs.info_messages = "Restart needed in order to update menus."
    # print(check_search_path(context))
    if check_search_path(context):
        np_settings["use_categories"] = "True"
        addon_prefs.info_messages = "Template folder is empty."
    # is_sortable = len(addon_prefs.np_preset_files) > 1
    # return is_sortable


def node_search_path(context):
    # preferences = context.preferences
    # addon_prefs = preferences.addons[__name__].preferences
    addon_prefs = get_addon_prefs(context)
    dirpath = addon_prefs.search_path
    return dirpath


class NP_NodeTemplatePrefs(AddonPreferences):
    bl_idname = __name__

    search_path: StringProperty(
        name="Folder",
        description="Directory of blend files with node-groups.",
        subtype='DIR_PATH',
        update=update_use_categories,
        # update=update_np_settings()
    )
    use_instance: bpy.props.BoolProperty(
        name="New Blender Instance",
        description="Open in a new Blender instance.",
        default=False
    )
    edit_preset: bpy.props.BoolProperty(
        name="Edit Preset",
        description="Edit Preset file",
        default=False
    )

    node_preset_settings = {
        "preset_file": "",
        "node_group": "",
        "mat_name": "",
        "geon_name": "",
        "world_name": "",
        "original_file": "",
        "targetpath":"",
        "use_categories":"",
        "error_messages":"",
        }

    use_transform: BoolProperty(
        name="Use Transform",
        description="Start transform Operator after inserting the node.",
        default=False,
        # update=update_np_settings()
    )

    auto_ungroup: BoolProperty(
        name="Auto Ungroup",
        description="When placing ungroup NodeGroup automatically.",
        default=False,
        # update=update_np_settings()
    )

    auto_close: BoolProperty(
        name="Auto Close",
        description="Template file will be saved and closed automatically. Original file will be openend then automatically.",
        default=False,
        # update=update_np_settings()
    )
    
    use_categories: BoolProperty(
        name="Use Categories",
        description="Divide blend template files into categ0ries in add menu. Main purpose is for better organising. ie use one blend for materials, one for compositing and one for geometry nodes. This approach is usefull when user has lots of nodegroup presets. Dividing helps keeping the add menu more readable and small. This workflow needs mutple blend files in order to work.",
        default=False,
        update=update_use_categories
    )
    
    info_messages: StringProperty(
        name="Info Messages",
        description="Show information about errors & messages."
    )

    np_list_index : IntProperty(
        name = "Node group will be saved to this blend file",
        default = 0
    )

    np_preset_files : CollectionProperty(
        type = NP_PG_Preset_Items
    )

    error_messages: StringProperty(
        name="Error Messages",
        description="Show information errors messages."
    )
    def draw(self, context):
        layout = self.layout
        ws = context.workspace

        box=layout.box()
        row = box.row()
        row = row.split(factor=0.3)
        row.label(text="Folder")
        row.prop(self, "search_path", text="")

        # sub.enabled = update_extras(context)
        row = box.row()
        row = row.split(factor=0.3)
        sub = row
        sub.enabled = self.search_path !=''
        sub.prop(self, "use_categories")
        
        if (self.node_preset_settings["use_categories"]=="True") and self.use_categories or check_search_path(context) or (self.node_preset_settings["use_categories"]=="False"):
            row.prop(self,"info_messages",text="", icon='INFO', emboss=False)

        # sub = row
        # sub.activated = False
        
        box=layout.box()
        col = box.column()
        col.label(text="Settings:")
        col.prop(self, "auto_close")
        col.prop(self, "auto_ungroup")
        col.prop(self, "use_transform")

        # Keymap
        wm = bpy.context.window_manager
        kc = wm.keyconfigs.user
        km = kc.keymaps['Node Editor']

        box=layout.box()
        split = box.split()
        col = split.column()
        col.label(text='Hotkey:')
        kmi = get_hotkey_entry_item(km, 'nodes.save_node_group', 'NP_OT_SaveNodeGroup', 'name')
        if kmi:
            # col.label(text='Save Node Group')
            col.context_pointer_set("keymap", km)
            rna_keymap_ui.draw_kmi([], kc, km, kmi, col, 0)
        else:
            col.label(text="restore hotkeys from interface tab")
        
        kmi = get_hotkey_entry_item(km, 'nodes.return_to_original', 'NP_OT_ReturnToOriginal', 'name')
        if kmi:
            # col.label(text='Return to Original')
            col.context_pointer_set("keymap", km)
            rna_keymap_ui.draw_kmi([], kc, km, kmi, col, 0)
        else:
            col.label(text="restore hotkeys from interface tab")


def check_node_type(context):
    space = context.space_data
    node_tree = space.node_tree
    node_type_string = {
        "ShaderNodeTree": "ShaderNodeGroup",
        "CompositorNodeTree": "CompositorNodeGroup",
        "TextureNodeTree": "TextureNodeGroup",
    }[type(node_tree).__name__]
    return node_type_string

def check_node_group(context):
    scene = context.scene
    snode = context.space_data
    aob = context.active_object

    # Works on overy node, handy but we really need nodegroup
    # print(context.active_node.type)
    anode = context.active_node
    # print(anode.type)
    if anode is not None:
        return anode.type =='GROUP'
    # print(context.area)
    # if context.area.type == 'NODE_EDITOR':
    # if scene.use_nodes:
    #     # print(snode.tree_type)
    #     # print(snode)
    #     # print("anode %s" % anode.node_tree)
    #     # print("anode %s" % anode.node_tree.name)
    #     if snode.tree_type == 'CompositorNodeTree':
    #         aNode = snode.node_tree.nodes.active
    #         if aNode is not None:
    #             return (aNode.type == 'GROUP')
    # if aob is not None and aob.type == 'MESH':
    #     if snode.tree_type == 'ShaderNodeTree':
    #         # print(snode.shader_type)
    #         if snode.shader_type == 'WORLD':
    #             aNode = context.scene.world.node_tree.nodes.active
    #             # if aNode is not None:
    #             #     return (aNode.type == 'GROUP')
    #         # if context.area.type == 'NODE_EDITOR':
    #         if snode.shader_type == 'OBJECT':
    #             # aNode = context.scene.node_tree.nodes.active
    #             aNode = aob.active_material.node_tree.nodes.active
    #             # if aNode is not None:
    #         if aNode is not None:
    #             return (aNode.type == 'GROUP')


class NP_PT_ListExample(Panel):
    """Panel for UI list."""

    bl_space_type  = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = 'Tool'
    bl_label = "Node Presets"

    def draw(self, context):
        layout = self.layout
        addon_prefs = get_addon_prefs(context)
        np_settings = addon_prefs.node_preset_settings

        layout.use_property_split = True
        layout.use_property_decorate = False

        is_sortable = len(addon_prefs.np_preset_files) > 1 or len(np_blend_categories) > 1
        
        row = layout.row()
        if np_settings["original_file"] != "":
            row.operator('nodes.return_to_original', text='Return to file', icon='LOOP_BACK')
            row.menu("NP_MT_settings_menu", text = '', icon = 'PREFERENCES')
        else:    
            if not check_node_group(context):
                row.label(text="No NodeGroup Selected", icon='INFO')
                row.menu("NP_MT_settings_menu", text = '', icon = 'PREFERENCES')
            else:
                rows = 1
                # print(is_sortable)
                # print((is_sortable))
                # print(len(addon_prefs.np_preset_files))
                # print(len(np_blend_categories))
                if (is_sortable):
                    rows = 4

                    # row = layout.row()

                    # if addon_prefs.node_preset_settings["original_file"] == "":
                    # row.template_list("NP_UL_List", "The_List", addon_prefs,"np_preset_files", addon_prefs, "np_list_index", rows=rows)
                    row.template_list("NP_UL_List", "", addon_prefs,"np_preset_files", addon_prefs, "np_list_index", rows=rows)
                    
                    # col = row.column(align=True)
                    # if is_sortable:
                    #     col.separator()
                    #     col.operator("nodes.np_move_item", icon='TRIA_UP', text="").direction = 'UP'
                    #     col.operator("nodes.np_move_item", icon='TRIA_DOWN', text="").direction = 'DOWN'
                    #     col.menu("NP_MT_settings_menu", text = '', icon = 'PREFERENCES')
                    # layout.operator('nodes.save_node_group', text='Save NodeGroup', icon='FILE_TICK')
                    
                # if not (is_sortable):
                    # col = layout.column() #align=True)
                    if bpy.data.filepath == '':
                        saveTooltip = "Please save file"
                        saveIcon = 'INFO'
                    else:
                        saveTooltip = "Save NodeGroup"
                        saveIcon = 'FILE_TICK'
                    # sub = row    
                    sub = layout.row()
                    sub.enabled = bpy.data.filepath != ''
                    sub.operator('nodes.save_node_group', text=saveTooltip, icon=saveIcon)
                    sub.menu("NP_MT_settings_menu", text = '', icon = 'PREFERENCES') #OPTIONS PREFERENCES


#################################################################################################
# Categorize blend files into submenu items

from collections import defaultdict
np_blend_categories = defaultdict(list)

# def get_blend_nodegroups(context, *, reload=False, dirpath):    
def get_blend_nodegroups(context, dirpath):    
    # NodeGroupItems = []
    
    # Force reload, we dont want cache. if we remove files we dont see until blender restarts
    # if node_template_cache._node_cache_path != dirpath:
    # reload = True

#    node_cache = node_template_cache._node_cache
#    if reload:
#        node_cache = []
#    if node_cache:
#        return node_cache
    
    np_blend_categories.clear()
    
    for fn in os.listdir(dirpath):
        if fn.endswith(".blend"):
            filepath = os.path.join(dirpath, fn)
            # Strip *.blend
            fn = fn[:-6]
            np_blend_categories[fn]
            with bpy.data.libraries.load(filepath) as (data_from, data_to):
                for group_name in data_from.node_groups:
                    if not group_name.startswith("_"):
                        np_blend_categories[fn].append((group_name,filepath))
    # print("Len blend groups %s" % len(np_blend_categories))
#    node_template_cache._node_cache = node_cache
#    node_template_cache._node_cache_path = dirpath
#    return node_cache

#node_template_cache._node_cache = []
#node_template_cache._node_cache_path = ""

def np_nodepresets_menu(self, context):
    layout = self.layout
    dirpath = node_search_path(context)
    # print("dirpath %s" % dirpath)
    
    try:
        os.listdir(dirpath)
        pass
    except:
        layout.label(text="Can't find template folder", icon='ERROR')
        return
    if check_search_path(context):
        layout.label(text="Template folder is empty", icon='INFO')    
        return
    if dirpath == "":
        layout.label(text="Set search dir in the addon-prefs")
        return
    try:
        layout.menu('NP_MT_nodepresets_menu', text="Node Presets", icon="PLUGIN")
    except Exception as ex:
        layout.label(text=repr(ex), icon='ERROR')


np_cat_list = []

# function to generate menu classes
def gen_categories():
    np_cat_list = []
    # filepath :StringProperty()
    for item in np_blend_categories:
        def custom_draw(self,context):
            layout = self.layout
            for group_name,filepath in np_blend_categories[self.bl_label]:
                # icon =pcoll[group_name]
    #                print(group_name)
    #                print(group_name.NodeGroupName)
                if group_name[2:3] == '_':
                    if group_name[0:3] == 'SH_':
                        iconType = 'NODE_MATERIAL'
                    if group_name[0:3] == 'CP_':
                        iconType = 'NODE_COMPOSITING'
                    if group_name[0:3] == 'GN_':
                        iconType = 'NODETREE'
                    if group_name[0:3] == 'TX_':
                        iconType = 'NODE_TEXTURING'
        #            ng.name = 'SH_' + ng.name 
                    groupName = group_name[3:]
                    # print("groupName %s" % groupName)
                if not group_name[2:3] == '_':
                    groupName = group_name
                    iconType = 'NONE'
                
                props = layout.operator(
                    NODE_OT_template_add.bl_idname,
                    text=groupName, icon = iconType
                )       
                props.filepath = filepath
                props.group_name = group_name
        
        menu_type = type("NP_MT_category_" + item, (bpy.types.Menu,), {
            "bl_idname": "NP_MT_category_" + item.replace(" ", "_"),   # replace whitespace with uderscore to avoid alpha-numeric suffix warning 
            "bl_space_type": 'NODE_EDITOR',
            "bl_label": item,
            "draw": custom_draw,
        })
        np_cat_list.append(menu_type)
        bpy.utils.register_class(menu_type)
    return np_cat_list


class NP_MT_nodepresets_menu(Menu):
    bl_label = "Realtime Materials"
    bl_idname = 'NP_MT_nodepresets_menu'

    def draw(self, context):
        layout = self.layout
        for cat in np_cat_list:
            layout.menu(cat.bl_idname)

#################################################################################################
# Settings Menu
class NP_MT_settings_menu(Menu):
    bl_idname = "NP_MT_settings_menu"
    bl_label = "Settings"
    bl_description = "Settings"

    def draw(self, context):
        addon_prefs = get_addon_prefs(context) 
        layout = self.layout
        layout.label(text = 'Saving NodeGroups:')    
        layout.prop(addon_prefs, "auto_close") #, icon = 'auto_close')
        layout.separator()
        layout.label(text = 'Placing Template:')
        layout.prop(addon_prefs, 'auto_ungroup')
        layout.prop(addon_prefs, 'use_transform')
        layout.separator()
        layout.label(text = 'Edit Template:')
        layout.operator('nodes.edit_node_group', icon='FILEBROWSER') #GREASEPENCIL PROPERTIES
        layout.operator('node.np_auto_rename',text='Add Prefix', icon='ADD').add_prefix = True
        layout.operator('node.np_auto_rename',text = 'Remove Prefix', icon='REMOVE').remove_prefix = True
        layout.separator()
        layout.operator('nodes.open_prefs', icon='PREFERENCES')


addon_keymaps = []
classes = (
    NP_OT_ErrorDialog,
    NP_MT_nodepresets_menu,

    NODE_OT_template_add,
    NODE_MT_template_add,

    NP_OT_EditNodeGroup,
    NP_OT_SaveNodeGroup,
    NP_OT_ReturnToOriginal,
    NP_UL_List,
    NP_PG_Preset_Items,
    NP_OT_AutoRenameShaders,
    NP_OT_OpenPrefs,
    NP_NodeTemplatePrefs,
    NP_OT_MoveItem,
    NP_PT_ListExample,
    NP_MT_settings_menu,
    )


def register():
    for c in classes:
        bpy.utils.register_class(c)

    addon_prefs = get_addon_prefs(bpy.context)
    if addon_prefs.use_categories:
        # global np_cat_list
        # global np_blend_categories        
        bpy.types.NODE_MT_add.append(np_nodepresets_menu)
    else:
        bpy.types.NODE_MT_add.append(add_node_button)
    bpy.app.handlers.load_post.append(open_nodepresets_check) 

    # hotkey setup
    add_hotkey()


def unregister():
    addon_prefs = get_addon_prefs(bpy.context)
    if addon_prefs.use_categories:
        bpy.types.NODE_MT_add.remove(np_nodepresets_menu)
    else:
        bpy.types.NODE_MT_add.remove(add_node_button)
    bpy.app.handlers.load_post.remove(open_nodepresets_check) 
    bpy.types.NODE_MT_add.remove(add_node_button)

    # handle the keymap
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()

    for c in reversed(classes):
        bpy.utils.unregister_class(c)


if __name__ == "__main__":
    register()


