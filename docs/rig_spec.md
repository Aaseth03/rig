# What does a finished rig look like?

## Harness setup
- Running install.js: The target harness configuration folder is set up in the directory
- Each harness has the correct setup, using the harness's documentation as source of truth


- install.js sets up the desired harness config (e.g `.claude`, `.github`)
- install.js sets up a `.rig` folder (Holding context map, docs, and misc rig documents that are not agent specific like skills, hooks etc. which has to stay in the harness's folder)

- Semi-automated context
    - Self contained map folder in `root/.context` containing the repo map and context, routing.
    - Self sustaining
        - Hooks that check context size when a .context/ file has been written. Any flagged files gets stored by path in a md file.
        - Running "/ICM-architect audit this repo" audits the repos structure and checks for bloat and fixes.
  



- Forced human gates for generated content


## Usage
1. Run install.js
2. Set up the map
    - For already existing project -> "ICM this project"
    - For new project without any code structure -> Start planning the project from an idea through an interview.
3. Plan features, milestones
4. Start coding with the agent
5. Repeat from 3.

## Features

A summary of the rig's features and their configurations.

### Skills
Skills are ...
#### ICM Architect - {Author: [RinDig](https://github.com/RinDig/icm-architect)}

### Hooks
Hooks are ...
#### Ask question - {Author: Aaseth03}
....
#### Context - {Author: }
....
#### Deny allowlist edits - {Author: }
....
#### Deny non-relative paths - {Author: }
....
#### Deny remove - {Author: }
....


### Agents
Agents are ...