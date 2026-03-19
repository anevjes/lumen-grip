"""
LumenGrip Agent — A Microsoft Agent Framework agent that:
1. Assembles context by retrieving relevant skills, checklists, and memories
2. Plans and executes multi-step work using checklists
3. Can generate and run Python code to complete tasks
4. Feeds results back into skills, checklists, and memories for continuous learning
"""

import os
import sys
import glob
import subprocess
from datetime import datetime, timezone

from dotenv import load_dotenv

load_dotenv(override=False)

from agent_framework import BaseAgent, tool
from agent_framework.azure import AzureAIClient
from azure.identity.aio import DefaultAzureCredential
from azure.ai.agentserver.agentframework import from_agent_framework


_base_dir = os.path.dirname(os.path.abspath(__file__))
SKILLS_FOLDER = os.getenv("SKILLS_FOLDER", os.path.join(_base_dir, "skills"))
MEMORY_FOLDER = os.getenv("MEMORY_FOLDER", os.path.join(_base_dir, "memory"))
CHECKLISTS_FOLDER = os.getenv("CHECKLISTS_FOLDER", os.path.join(_base_dir, "checklists"))

os.makedirs(MEMORY_FOLDER, exist_ok=True)
os.makedirs(CHECKLISTS_FOLDER, exist_ok=True)
os.makedirs(SKILLS_FOLDER, exist_ok=True)


# ===================================================================
# Skill tools
# ===================================================================

@tool
def list_skills() -> str:
    """List all available skill names loaded from the skills folder."""
    md_files = glob.glob(os.path.join(SKILLS_FOLDER, "*.md"))
    if not md_files:
        return "No skills found in the skills folder."
    names = [os.path.splitext(os.path.basename(f))[0] for f in md_files]
    return "Available skills:\n" + "\n".join(f"- {n}" for n in names)


@tool
def read_skill(skill_name: str) -> str:
    """Read the full content of a skill markdown file by name.

    Args:
        skill_name: The name of the skill (without .md extension).
    """
    safe_name = os.path.basename(skill_name)
    filepath = os.path.join(SKILLS_FOLDER, f"{safe_name}.md")
    if not os.path.isfile(filepath):
        return f"Skill '{safe_name}' not found. Use list_skills to see available skills."
    with open(filepath, encoding="utf-8") as f:
        return f.read()


# ===================================================================
# Memory tools
# ===================================================================

@tool
def list_memories() -> str:
    """List all memory entries stored in the memory folder."""
    md_files = sorted(glob.glob(os.path.join(MEMORY_FOLDER, "*.md")))
    if not md_files:
        return "No memories recorded yet."
    names = [os.path.splitext(os.path.basename(f))[0] for f in md_files]
    return "Stored memories:\n" + "\n".join(f"- {n}" for n in names)


@tool
def read_memory(memory_name: str) -> str:
    """Read the full content of a memory markdown file.

    Args:
        memory_name: The name of the memory (without .md extension).
    """
    safe_name = os.path.basename(memory_name)
    filepath = os.path.join(MEMORY_FOLDER, f"{safe_name}.md")
    if not os.path.isfile(filepath):
        return f"Memory '{safe_name}' not found. Use list_memories to see stored memories."
    with open(filepath, encoding="utf-8") as f:
        return f.read()


@tool
def save_memory(memory_name: str, content: str) -> str:
    """Save or overwrite a memory entry as a markdown file.

    Use this after completing a task to record a summary of what happened,
    what worked, what didn't, and any improvement suggestions.

    Args:
        memory_name: Short descriptive name (used as filename, without .md).
        content: Markdown content to store — should include a summary of the
                 interaction, outcomes, and any lessons learned.
    """
    safe_name = os.path.basename(memory_name)
    if not safe_name:
        return "Invalid memory name."
    filepath = os.path.join(MEMORY_FOLDER, f"{safe_name}.md")
    header = f"<!-- saved: {datetime.now(timezone.utc).isoformat()} -->\n\n"
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(header + content)
    return f"Memory '{safe_name}' saved successfully."


@tool
def delete_memory(memory_name: str) -> str:
    """Delete a memory entry that is no longer relevant.

    Args:
        memory_name: The name of the memory to delete (without .md extension).
    """
    safe_name = os.path.basename(memory_name)
    filepath = os.path.join(MEMORY_FOLDER, f"{safe_name}.md")
    if not os.path.isfile(filepath):
        return f"Memory '{safe_name}' not found."
    os.remove(filepath)
    return f"Memory '{safe_name}' deleted."


# ===================================================================
# Checklist tools
# ===================================================================

@tool
def list_checklists() -> str:
    """List all available checklist templates in the checklists folder."""
    md_files = sorted(glob.glob(os.path.join(CHECKLISTS_FOLDER, "*.md")))
    if not md_files:
        return "No checklists found."
    names = [os.path.splitext(os.path.basename(f))[0] for f in md_files]
    return "Available checklists:\n" + "\n".join(f"- {n}" for n in names)


@tool
def read_checklist(checklist_name: str) -> str:
    """Read the full content of a checklist markdown file.

    Use this to load a step-by-step plan template before starting
    a multi-step task. Follow the checklist items in order and
    report progress against each step.

    Args:
        checklist_name: The name of the checklist (without .md extension).
    """
    safe_name = os.path.basename(checklist_name)
    filepath = os.path.join(CHECKLISTS_FOLDER, f"{safe_name}.md")
    if not os.path.isfile(filepath):
        return f"Checklist '{safe_name}' not found. Use list_checklists to see available checklists."
    with open(filepath, encoding="utf-8") as f:
        return f.read()


@tool
def save_checklist(checklist_name: str, content: str) -> str:
    """Save or update a checklist template for future reuse.

    Call this when you discover a repeatable workflow that would benefit
    from a checklist template. Use markdown with `- [ ]` task items.

    Args:
        checklist_name: Short descriptive name (used as filename, without .md).
        content: Markdown checklist content with step-by-step items.
    """
    safe_name = os.path.basename(checklist_name)
    if not safe_name:
        return "Invalid checklist name."
    filepath = os.path.join(CHECKLISTS_FOLDER, f"{safe_name}.md")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    return f"Checklist '{safe_name}' saved to {CHECKLISTS_FOLDER}."


# ===================================================================
# Skill authoring tools
# ===================================================================

@tool
def save_skill(skill_name: str, content: str) -> str:
    """Save or update a skill markdown file for future reuse.

    Call this when you identify a domain, technique, or procedure that
    should be captured as reusable knowledge for future requests.

    Args:
        skill_name: Short descriptive name (used as filename, without .md).
        content: Markdown content describing the skill — purpose, guidelines,
                 output format, and examples.
    """
    safe_name = os.path.basename(skill_name)
    if not safe_name:
        return "Invalid skill name."
    filepath = os.path.join(SKILLS_FOLDER, f"{safe_name}.md")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    return f"Skill '{safe_name}' saved to {SKILLS_FOLDER}."


# ===================================================================
# Code execution tools
# ===================================================================

_MAX_OUTPUT = 10_000  # truncate stdout/stderr to prevent huge payloads
_SCRIPTS_DIR = os.path.join(_base_dir, "generated_scripts")
os.makedirs(_SCRIPTS_DIR, exist_ok=True)


@tool
def run_python(code: str) -> str:
    """Execute a Python code snippet on the LOCAL machine and return its output.

    The code runs as a subprocess using the same Python interpreter and
    virtual-environment packages as the agent.  Environment variables
    (including those loaded from .env) are inherited, and the working
    directory is the project root.

    A copy of every script is saved under generated_scripts/ so the user
    can inspect or re-run it.

    Args:
        code: Python source code to execute. Must be self-contained.
    """
    # Persist a copy for the user to inspect / re-run
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    saved_path = os.path.join(_SCRIPTS_DIR, f"script_{timestamp}.py")
    with open(saved_path, "w", encoding="utf-8") as f:
        f.write(code)

    try:
        result = subprocess.run(
            [sys.executable, saved_path],
            capture_output=True,
            text=True,
            timeout=120,
            cwd=_base_dir,
            env=os.environ.copy(),
        )
        stdout = result.stdout[:_MAX_OUTPUT] if result.stdout else ""
        stderr = result.stderr[:_MAX_OUTPUT] if result.stderr else ""
        parts = [f"Script saved: {saved_path}"]
        if stdout:
            parts.append(f"STDOUT:\n{stdout}")
        if stderr:
            parts.append(f"STDERR:\n{stderr}")
        parts.append(f"Exit code: {result.returncode}")
        return "\n".join(parts)
    except subprocess.TimeoutExpired:
        return f"ERROR: Code execution timed out after 120 seconds. Script saved: {saved_path}"


@tool
def pip_install(packages: str) -> str:
    """Install one or more Python packages into the local virtual environment.

    Call this BEFORE run_python when the generated code needs a package
    that is not already installed.

    Args:
        packages: Space-separated package specifiers (e.g. "requests pandas").
    """
    pkg_list = packages.strip().split()
    if not pkg_list:
        return "No packages specified."
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "--quiet"] + pkg_list,
            capture_output=True,
            text=True,
            timeout=120,
            cwd=_base_dir,
            env=os.environ.copy(),
        )
        stdout = result.stdout[:_MAX_OUTPUT] if result.stdout else ""
        stderr = result.stderr[:_MAX_OUTPUT] if result.stderr else ""
        parts = []
        if stdout:
            parts.append(stdout)
        if stderr:
            parts.append(stderr)
        parts.append(f"Exit code: {result.returncode}")
        return "\n".join(parts)
    except subprocess.TimeoutExpired:
        return "ERROR: pip install timed out after 120 seconds."


# ===================================================================
# Dynamic system prompt — defines the agentic context-assembly loop
# ===================================================================

def _load_memory_summaries() -> str:
    """Read all memory files and concatenate them into a prompt section."""
    md_files = sorted(glob.glob(os.path.join(MEMORY_FOLDER, "*.md")))
    if not md_files:
        return ""
    sections = []
    for path in md_files:
        name = os.path.splitext(os.path.basename(path))[0]
        with open(path, encoding="utf-8") as f:
            body = f.read().strip()
        sections.append(f"### {name}\n{body}")
    return "\n\n".join(sections)


def _build_instructions() -> str:
    # --- catalogue summaries ---
    skill_files = sorted(glob.glob(os.path.join(SKILLS_FOLDER, "*.md")))
    skill_names = [os.path.splitext(os.path.basename(f))[0] for f in skill_files]

    checklist_files = sorted(glob.glob(os.path.join(CHECKLISTS_FOLDER, "*.md")))
    checklist_names = [os.path.splitext(os.path.basename(f))[0] for f in checklist_files]

    memory_text = _load_memory_summaries()

    # --- prompt ---
    prompt = (
        "You are LumenGrip, an autonomous AI agent. You solve tasks end-to-end "
        "by assembling context, planning, executing code, and recording what you "
        "learned.\n\n"

        "# MANDATORY WORKFLOW\n"
        "You MUST follow these phases in strict order for EVERY user request. "
        "NEVER skip a phase. NEVER answer the user's question directly without "
        "completing Phases 1–3 first.\n\n"

        "## Phase 1: Assemble Context (REQUIRED — do this FIRST)\n"
        "You MUST call these tools before doing anything else:\n"
        "1. Call `list_skills`. Read the list. Then call `read_skill` for EVERY "
        "skill name that could relate to the user's request.\n"
        "2. Call `list_memories`. Then call `read_memory` for any memory whose "
        "name relates to the request.\n"
        "3. Call `list_checklists`. Then call `read_checklist` for the "
        "best-matching checklist.\n\n"
        "⚠️ You MUST NOT proceed to Phase 2 until you have called at least "
        "`list_skills`, `read_skill`, and `list_checklists`. If you skip these "
        "calls, your response is invalid.\n\n"

        "## Phase 2: Plan (REQUIRED — show before executing)\n"
        "Using the checklist you loaded (or an ad-hoc one if none matched), "
        "present a numbered plan to the user. Each step must:\n"
        "- Reference which skill it draws from (by name).\n"
        "- State the concrete action (e.g., 'Call Graph API to fetch unread "
        "emails using the endpoint from the email-checking skill').\n\n"
        "⚠️ You MUST NOT proceed to Phase 3 until the plan is shown.\n\n"

        "## Phase 3: Execute (REQUIRED — use `run_python`)\n"
        "For each step in your plan, generate and run Python code:\n\n"
        "### Code generation rules — STRICT\n"
        "1. **Derive code from the skill.** Open the skill content from Phase 1. "
        "Find its 'Integration Notes', code snippets, API endpoints, and auth "
        "patterns. Your script MUST use those EXACT endpoints, auth methods, "
        "and parameters. Do NOT invent different approaches.\n"
        "2. **Map code to plan steps.** Each step from Phase 2 becomes a "
        "labelled block in the script: `# Step N: <description from plan>`.\n"
        "3. **Apply memory fixes.** If a memory records a failure or "
        "workaround, incorporate it before running.\n"
        "4. **Self-contained.** Every `run_python` call must be a complete "
        "runnable script — imports, auth, logic, structured output.\n"
        "5. **Check output.** Inspect stdout/stderr. If it fails, fix using "
        "skill + memory context and retry.\n"
        "6. **No hallucinated APIs.** If the skill does not specify how to do "
        "something, state that explicitly — never guess endpoints or methods.\n\n"
        "⚠️ You MUST call `run_python` at least once. If you answer without "
        "executing code, your response is invalid.\n\n"

        "## Phase 4: Update Context (REQUIRED — do this LAST)\n"
        "After execution, update the knowledge base:\n"
        "1. Call `save_memory` — summarise: what was requested, what you did, "
        "which skills/checklists were used, what worked, what to improve.\n"
        "2. If you discovered reusable knowledge, call `save_skill`.\n"
        "3. If the task revealed a repeatable workflow, call `save_checklist`.\n"
        "4. Call `delete_memory` for any outdated memories.\n\n"

        "# Tool reference\n"
        "| Tool | Purpose |\n"
        "|------|--------|\n"
        "| `list_skills` / `read_skill` | Browse and load skill documents |\n"
        "| `save_skill` | Create or update a skill document |\n"
        "| `list_memories` / `read_memory` | Browse and load past learnings |\n"
        "| `save_memory` / `delete_memory` | Record or remove learnings |\n"
        "| `list_checklists` / `read_checklist` | Browse and load plan templates |\n"
        "| `save_checklist` | Create or update a checklist template |\n"
        "| `run_python` | Execute generated Python code on the LOCAL machine |\n"
        "| `pip_install` | Install Python packages into the local venv |\n"
    )

    if skill_names:
        prompt += (
            "\n# Available skills\n"
            + ", ".join(skill_names)
            + "\n"
        )
    if checklist_names:
        prompt += (
            "\n# Available checklists\n"
            + ", ".join(checklist_names)
            + "\n"
        )
    if memory_text:
        prompt += (
            "\n# Prior memories (apply these insights)\n\n"
            + memory_text
            + "\n"
        )

    return prompt


# ===================================================================
# Main
# ===================================================================

async def main():
    credential = DefaultAzureCredential()

    agent = AzureAIClient(
        project_endpoint=os.getenv("FOUNDRY_PROJECT_ENDPOINT"),
        model_deployment_name=os.getenv("FOUNDRY_MODEL_DEPLOYMENT_NAME"),
        credential=credential,
    ).as_agent(
        name="LumenGrip",
        instructions=_build_instructions(),
        tools=[
            list_skills, read_skill, save_skill,
            list_checklists, read_checklist, save_checklist,
            list_memories, read_memory, save_memory, delete_memory,
            run_python, pip_install,
        ],
    )

    use_devui = os.getenv("DEVUI", "").lower() in ("1", "true", "yes")

    if use_devui:
        from agent_framework.devui import serve
        # serve() is synchronous — it launches uvicorn with its own event loop,
        # so we pass the agent without entering async context here.
        serve(
            entities=[agent],
            port=int(os.getenv("DEVUI_PORT", "8080")),
            host=os.getenv("DEVUI_HOST", "127.0.0.1"),
            auto_open=True,
            mode="developer",
        )
    else:
        async with agent:
            await from_agent_framework(agent).run_async()


if __name__ == "__main__":
    import asyncio

    if os.getenv("DEVUI", "").lower() in ("1", "true", "yes"):
        # DevUI serve() calls uvicorn.run() which starts its own event loop.
        # Avoid asyncio.run() to prevent "cannot be called from a running loop".
        from agent_framework.devui import serve
        from azure.identity.aio import DefaultAzureCredential as _Cred

        _credential = _Cred()
        _agent = AzureAIClient(
            project_endpoint=os.getenv("FOUNDRY_PROJECT_ENDPOINT"),
            model_deployment_name=os.getenv("FOUNDRY_MODEL_DEPLOYMENT_NAME"),
            credential=_credential,
        ).as_agent(
            name="LumenGrip",
            instructions=_build_instructions(),
            tools=[
                list_skills, read_skill, save_skill,
                list_checklists, read_checklist, save_checklist,
                list_memories, read_memory, save_memory, delete_memory,
                run_python, pip_install,
            ],
        )
        serve(
            entities=[_agent],
            port=int(os.getenv("DEVUI_PORT", "8080")),
            host=os.getenv("DEVUI_HOST", "127.0.0.1"),
            auto_open=True,
            mode="developer",
        )
    else:
        asyncio.run(main())
