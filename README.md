# Node Preset

!['Look UI'](https://raw.githubusercontent.com/wiki/schroef/quickswitch/images/node-presets-v015.png?v22092022)
> XXXX


> [Source: Blender manual](https://docs.blender.org/manual/en/2.83/addons/node/node_presets.html)

This add-on allows you to set a file path to a directory with blend-file(s) containing node groups. All the node groups will then be available from a new menu in the node editors ‣ Add ‣ Template menu.

<b>Activation</b>

1. Open Blender and go to Preferences then the Add-ons tab.
2. Click Node then Node Presets to enable the script.

<b>Usage<bb>
In the add-on’s preferences you can set the path to your directory. The directory or folder can have multiple blend-files and all node groups they contain will be available. All node editors are supported, you can add compositing, material, enivronment and geometry nodes node groups. In the node editor select a node group which needs to be saved. In the properties panel > tools, you'll find a panel "Node Presets'. Here your blend file(s) will show and can be selected as the target file where you want to save it. Then use the "Save Node Group" button or the shortcut. The blend file will be opened and the node group will be placed last in line. Depending on your options, it will either automatically save and close and return to the orginal working file or you need to press the button "return to file". NB Texture Node Groups have been removed since its a feature which will be removed.
The best way to use the blend files, is to keep the node editor open for the target blend file type your using. When working with categories, this also implies. For materials and geometry node and simple object should be added with either a Material or a Geometry Node modifier. For the environment node groups keep the world type open. When saving compositor nodes keeps compositor editor open. Then save and close each type of file.

<b>Using categories</b>
There is the option to use categories, this makes it easier to identyfy all the different node groups from your saved files. Because by default its not clear which node groups can be used. When using categories its best to divide them using the following blend-file names; Materials, Compositor, Environment and Geometry Nodes. At this point i've added operator for automatically adding a Prefix to the type of blend which is open. This adds a prefix with 2 characters and is used to show the icon and add them to the specific categorie. The operator can be found in the setting menu in the panel. It will check all the node groups in the file and add the 2 character prefer followed by underscore, so ie materials will look like this; SH_Water refractive. Im thinking about expanding this with subcategories, but thats is a WIP.

!['Categories example add menu'](https://raw.githubusercontent.com/wiki/schroef/node-presets/images/node-presets-preferences-v015.png?22092022)
> Add menu when using categories

<b>Cleaning the source blend files</b>
When Node Groups are added to the target bled file, they are added and checked with Fake User. The easiest way to remove them is by going to the Outliner Header > Data API > Node Groups. Then uncheck Fake User, save and close the file and the Node Group should then be removed, mits the user count is 1 at that point. Otherwise there is an instance also in the Node Editor depending on what type of Node Group which was saved.

!['Cleaning unwanted Node Groups'](https://raw.githubusercontent.com/wiki/schroef/node-presets/images/addon-preferences_v011.jpg)
> Cleaning unwanted Node Groups

<b>Updated Features</b>

1. Automatically open and append node group to selected source blender file
2. Option to use Categories so you can separate by; Materials, Compositor, Geometry Nodes and Environment node groups
2. Add and remove prefixes to be used for categories
4. Option to ungroup node group when placing
5. Automatically save node group and return to original working fule
6. Shortcuts for faster workflow
7. Node groups will be placed automatically next to eacht other to keep overview

<b>WIP</b>

1. Expand categories with subcategories, usefull wwith large node group library


### System Requirements

| **OS** | **Blender** |
| ------------- | ------------- |
| OSX | Blender 2.80+ |
| Windows | Not Tested |
| Linux | Not Tested |


### Installation Process

1. Download the latest <b>[release](https://github.com/schroef/node-presets/releases/)</b>
2. If you downloaded the zip file.
3. Open Blender.
4. Go to File -> User Preferences -> Addons.
5. At the bottom of the window, choose *Install From File*.
6. Select the file `nodepresets-[VERSION].zip` from your download location..
7. Activate the checkbox for the plugin that you will now find in the list.
8. You'll get a warning for 2 addons with same name. You can delete the original one in the application folder


### Changelog
[Full Changelog](CHANGELOG.md)