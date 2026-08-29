Add Web searcher sub-agent.
- callable as a subagent through the main agent
- Web searcher searches the web instead of the main agent, preserving context
- Agent gets a goal, a question to answer -> searches the web -> returns a summary to the main agent answering the question in short detail


## Install script
- Add to the console log when running the install script:
    - Add a prompt to the user to initiate ICM in the .context folder

- Add the .agent-temp/ folder to be initiated on install


## Hooks
Change the context hook to look for files within `.context` rather than just looking for "context.md" files. Because of the ICM update, the map is now self-contained in a folder rather than spread out through the actual docs.

## Auto installed docs

### AGENTS.md
Fix a generic AGENTS.md template with pre-shipped instructions that always apply to use with `rig`setup (e.g `.agents-tmp/`, `.context/`)

### .github
Make a preconfigured .github file to the install so that cherry-picked files do not get git-tracked.

