All notable changes to this project will be documented in this file.
# Changelog


## [0.1.5.1] - 2022-09-23
### Added
- Opening preferences from Extras menu open addon expandded
- Save & Reload operator when cleaning blend files
### Fixed
- Error report messages
- Auto add & remove prefix operator > wouldnt add and remove prefix properly
- Poll for auto save & reload operator
- Issue when adding Node Preset for Lights 
- when Using Categories for Material and World

## [0.1.5] - 2022-09-13
### Added
- Prefix to list items so they are stored and can be customized
- Shortcut for save action and return action
- Error report when base files isnt setup properly for adding node groups

### Fixed
- Saving wolrd note caused error due to wwrong node_tree check space_data
- Reports when operator can not place node group due to error. Added better reports as well
- Issue not using categories. 22-09-2022
- Add prefix operator, now checks world or material
- Checks if node tree is

## [0.1.4] - 2022-05-10
### Fixed
- Issue with template in panel, suddenly wont show. np_preset_files keeps being 0 because its never called. Used to work fine
- Checking modifiers, active is not supported with bl.2.83
- Add issue with not support node tree, #295

## [0.1.3] - 2022-05-05
### Removed
- Prefix when adding node group

## [0.1.2] - 2022-02-09
### Added
- Functionality like "edit linked" addon
  Addon automatically open, add node group and closes file, return to original working file

## [0.1.1] - 2022-02-03
### New
- Initial addon

## Notes
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
<!--### Official Rigify Info-->

[0.1.5.1]:https://github.com/schroef/QuickSwitch/releases/tag/v.0.1.5.1
[0.1.5]:https://github.com/schroef/QuickSwitch/releases/tag/v.0.1.5
