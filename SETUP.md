# Setup Instructions for OpenClaw Clone

This is a "pure and harmonious" clone of the original AI assistant, with all adult content removed while preserving core personality traits.

## What's Included

- **Core identity files** (cleaned of adult content):
  - `IDENTITY.md` - Professional stock analyst identity
  - `SOUL.md` - Core principles and vibe (professional, direct, efficient)
  - `USER.md` - Basic user information
  - `AGENTS.md` - Workspace guidelines
  - `TOOLS.md` - Local notes template
  - `HEARTBEAT.md` - System health checks (professional version)
  - `MEMORY.md` - Sample long-term memory
  - `BOOTSTRAP.md` - Initialization script

- **Essential skills** (selected for professional use):
  - `chat` - Communication preferences
  - `find` - Search and location
  - `tavily` - Web search
  - `telegram` - Telegram workflow design
  - `telegram-bot` - Telegram bot management
  - `token-counter` - Token usage tracking

- **Supporting scripts**:
  - `hippocampus_memory.py` - Memory compression system
  - `archive_and_compress.py` - Archive and compression utility

## Excluded Content

The following original skills were **not included** due to potential adult content or inappropriate themes for a "pure and harmonious" version:

- `roleplay` - Roleplaying scenarios
- `social` - Social network integration (inbed.ai)

## Installation

1. **On the target machine**, ensure OpenClaw is installed:
   ```bash
   npm install -g openclaw
   ```

2. **Copy this workspace** to the target machine:
   ```bash
   # Copy the entire Openclaw folder to the workspace directory
   cp -r /Volumes/Lexar/Openclaw ~/.openclaw/workspace/clean-clone
   ```

3. **Configure OpenClaw** to use this workspace:
   ```bash
   # Option A: Set as default workspace
   ln -sf ~/.openclaw/workspace/clean-clone ~/.openclaw/workspace/default
   
   # Option B: Specify workspace when starting
   openclaw --workspace ~/.openclaw/workspace/clean-clone
   ```

4. **Start OpenClaw**:
   ```bash
   openclaw start
   ```

## Customization

This clone maintains the core personality traits:
- Direct, no-nonsense communication style
- Resourceful problem-solving approach
- Professional yet personable demeanor
- Opinionated when it matters

You can further customize the files to match your preferences, particularly:
- `IDENTITY.md` - Adjust name, title, or vibe
- `SOUL.md` - Modify core principles
- `USER.md` - Add your specific preferences

## Notes

- Token balance and revenue tracking files are not included; new instances will create their own
- Memory files are minimal; the system will build its own memory over time
- All adult content has been removed while preserving efficiency and personality
- The heartbeat system includes survival prioritization (token balance > memory compression)

---

This clone is ready for professional use in any environment.