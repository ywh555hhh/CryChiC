from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

import yaml
from jsonschema import validate


def load_yaml(path: Path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def run_claude_headless(prompt: str, model: str) -> str:
    env = os.environ.copy()
    env["ANTHROPIC_MODEL"] = model
    result = subprocess.run([
        "claude", "-p", prompt
    ], capture_output=True, text=True, env=env, check=False)
    if result.returncode != 0:
        raise RuntimeError(result.stderr)
    return result.stdout


def extract_json(raw: str):
    raw = raw.strip()
    if raw.startswith("```"):
        lines = raw.splitlines()
        lines = lines[1:-1]
        raw = "\n".join(lines).strip()
    return json.loads(raw)


def run_stage(project_root: Path, job_dir: Path, stage_name: str):
    configs = project_root / "configs"
    providers = load_yaml(configs / "providers.yaml")
    profiles = load_yaml(configs / "profiles.yaml")
    stages = load_yaml(configs / "stages.yaml")

    stage = stages["stages"][stage_name]
    profile = profiles["profiles"][stage["profile"]]
    provider_ref = profile["provider_chain"][0]
    provider = providers["providers"][provider_ref["provider"]]
    model = provider["models"][provider_ref["model_slot"]]

    input_data = json.loads((job_dir / "input.json").read_text(encoding="utf-8"))
    prompt_text = (project_root / stage["prompt"]).read_text(encoding="utf-8") if (project_root / stage["prompt"]).exists() else ""
    schema = json.loads((project_root / stage["schema"]).read_text(encoding="utf-8"))

    prompt = f"{prompt_text}\n\n输入数据：\n{json.dumps(input_data, ensure_ascii=False, indent=2)}\n\n仅输出 JSON。"

    if provider["adapter"] == "claude_code_headless":
        raw = run_claude_headless(prompt, model)
    else:
        raise NotImplementedError("Only claude_code_headless is minimally wired in this skeleton")

    parsed = extract_json(raw)
    validate(instance=parsed, schema=schema)
    (job_dir / stage["output_to"]).write_text(json.dumps(parsed, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--job-dir", required=True)
    parser.add_argument("--stage", required=True)
    args = parser.parse_args()

    run_stage(Path(args.project_root), Path(args.job_dir), args.stage)
