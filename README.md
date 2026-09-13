# skills

Shared Claude Code / Codex skills for good-shepherd-insights agents.

Drop a skill directory in `skills/<name>/` (must contain `SKILL.md`) and it's
available to any agent that mounts this repo. Add new skills via PR.

Symlink or copy into your agent's skills directory to use locally, e.g.:

```
ln -s /path/to/skills/skills/<name> ~/.claude/skills/<name>
ln -s /path/to/skills/skills/<name> ~/.codex/skills/<name>
```
