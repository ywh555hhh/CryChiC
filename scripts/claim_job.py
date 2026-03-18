from __future__ import annotations

import shutil
from pathlib import Path


def main() -> None:
    """
    最小版：从 jobs/pending 取一个 job，移到 jobs/running，并打印路径。
    用于外部 while loop 驱动。
    """
    project_root = Path(__file__).resolve().parent.parent
    pending_dir = project_root / "jobs" / "pending"
    running_dir = project_root / "jobs" / "running"
    running_dir.mkdir(parents=True, exist_ok=True)

    jobs = sorted(pending_dir.glob("job-*.json"))
    if not jobs:
        raise SystemExit(1)

    job_path = jobs[0]
    target = running_dir / job_path.name
    shutil.move(str(job_path), str(target))
    print(target)


if __name__ == "__main__":
    main()
