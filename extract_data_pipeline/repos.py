# Code provided by Opdebeeck, R. D. from the VUB 2025
import contextlib
import tempfile
from collections.abc import Iterator
from multiprocessing import Process
from pathlib import Path
import logging
import git
import shutil
# The following reference was used for logging timestamps
# AdamE, C. Josh, djvg, Gab, gae123, G., Hans, H. James, Michael, paidhima, Toros91, user2176576, Zipp, R. StackOverflow February, 4 2015. Print timestamp for logging in Python.
# https://stackoverflow.com/questions/28330317/print-timestamp-for-logging-in-python. Retrieved on November 20, 2025
logging.basicConfig(format="%(asctime)s %(message)s", level=logging.WARNING, datefmt='%Y-%m-%d %H:%M:%S')

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


def _clone_repo(repo_name: str, target_dir: Path, c_hash: str) -> None:
    repo = git.Repo.clone_from(f"{repo_name}", target_dir)
    try:
        repo.git.checkout(c_hash)
        logging.warning("Checkout Successful: " + repo_name)
    except Exception as e:
        logging.warning("Failed to checkout: " + repo_name + " due to " + str(e))
        file = open("failed_to_checkout.txt", "a")
        file.writelines([str(target_dir) + "\n"])
        file.close()
def clone_repo(repo_name: str, repo_link: str, target_dir: Path, c_hash: str) -> git.Repo | None:
    try:
        # Use a timeout, at least one repository seems to get stuck.
        p = Process(target=_clone_repo, args=(repo_link, target_dir, c_hash))
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