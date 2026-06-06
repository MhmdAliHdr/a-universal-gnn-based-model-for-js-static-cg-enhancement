# Code provided by Opdebeeck, R. D. from the VUB 2025
import contextlib
import tempfile
from collections.abc import Iterator
from multiprocessing import Process
from pathlib import Path

import git


@contextlib.contextmanager
def clone_repo_to_temporary_directory(
    full_name: str, repo_ref: str
) -> Iterator[git.Repo | None]:
    with tempfile.TemporaryDirectory() as d:
        repo = clone_repo(full_name, repo_ref, target_dir=Path(d))
        if repo is not None:
            yield repo
        else:
            yield None


def _clone_repo(repo_name: str, target_dir: Path) -> None:
    repo = git.Repo.clone_from(f"{repo_name}", target_dir)


def clone_repo(repo_name: str, repo_link: str, target_dir: Path) -> git.Repo | None:
    try:
        # Use a timeout, at least one repository seems to get stuck.
        p = Process(target=_clone_repo, args=(repo_link, target_dir))
        p.start()
        p.join(timeout=300)
        if p.exitcode is None:
            print(f"{repo_name} TIMED OUT!")
            p.kill()
        return git.Repo(target_dir)
    except Exception as e:
        print(f"{repo_name} FAILED! {type(e).__name__}")
        print(e)
        return None