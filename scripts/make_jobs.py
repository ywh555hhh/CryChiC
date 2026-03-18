from __future__ import annotations

import json
from pathlib import Path


def main() -> None:
    """
    最小版：从 data/seed/entries.json 读取词条列表，
    为每个词条生成一个 job 文件到 jobs/pending。
    """
    project_root = Path(__file__).resolve().parent.parent
    seed_file = project_root / "data" / "seed" / "entries.json"
    pending_dir = project_root / "jobs" / "pending"
    pending_dir.mkdir(parents=True, exist_ok=True)

    if not seed_file.exists():
        raise FileNotFoundError(f"Missing seed file: {seed_file}")

    entries = json.loads(seed_file.read_text(encoding="utf-8"))
    if not isinstance(entries, list):
        raise ValueError("entries.json must be a JSON array")

    for idx, entry in enumerate(entries, start=1):
        job_id = f"job-{idx:06d}"
        job = {
            "job_id": job_id,
            **entry,
        }
        (pending_dir / f"{job_id}.json").write_text(
            json.dumps(job, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )

    print(f"Created {len(entries)} jobs in {pending_dir}")


if __name__ == "__main__":
    main()
