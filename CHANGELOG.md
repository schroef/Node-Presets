All notable changes to this project will be documented in this file.
# Changelog


## [0.1.5] - 2022-02-09
### Added
- Prefix to list items so they are stored and can be customized
- Shortcut for save action and return action
### Fixed
- Saving wolrd note caused error due to wwrong node_tree check space_data

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

[0.1.5]:https://github.com/schroef/QuickSwitch/releases/tag/v.0.1.5