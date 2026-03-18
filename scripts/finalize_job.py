from __future__ import annotations

import json
import shutil
from pathlib import Path


def main(job_dir_str: str) -> None:
    """
    最小版：检查 job_dir 中是否存在 audit.json，
    如果通过则移到 jobs/done，否则移到 jobs/failed。
    """
    project_root = Path(__file__).resolve().parent.parent
    job_dir = Path(job_dir_str)
    running_file = project_root / "jobs" / "running" / f"{job_dir.name}.json"
    done_dir = project_root / "jobs" / "done"
    failed_dir = project_root / "jobs" / "failed"
    done_dir.mkdir(parents=True, exist_ok=True)
    failed_dir.mkdir(parents=True, exist_ok=True)

    audit_file = job_dir / "audit.json"
    if not audit_file.exists():
        target = failed_dir / f"{job_dir.name}.json"
        if running_file.exists():
            shutil.move(str(running_file), str(target))
        print("failed:no_audit")
        return

    audit = json.loads(audit_file.read_text(encoding="utf-8"))
    status = audit.get("status")

    if status == "pass":
        target = done_dir / f"{job_dir.name}.json"
        if running_file.exists():
            shutil.move(str(running_file), str(target))
        print("done")
    else:
        target = failed_dir / f"{job_dir.name}.json"
        if running_file.exists():
            shutil.move(str(running_file), str(target))
        print(f"failed:{status}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("job_dir")
    args = parser.parse_args()
    main(args.job_dir)
