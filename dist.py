#!/usr/bin/env python3
"""
Generate a standalone Geckodriver distfile from within a mozilla-unified clone.

Geckodriver depends upon several crates local to the mozilla-unified source
tree. This script bundles up the Geckodriver source code and the local
dependencies into a standalone tarball for easy distribution.

Usage:
    dist.py <version>

For example `dist.py 1.2.3` will create `target/dist/geckodriver-1.2.3.tar.gz`.

"""

import toml
import sys
import os
import shutil
import tarfile
from tempfile import TemporaryDirectory

OUT_DIR = "target/dist"


def main(version):
    os.makedirs(OUT_DIR, exist_ok=True)
    with TemporaryDirectory() as tmpd:
        print(make_tarball(tmpd, populate_dest_dir(tmpd, version)))


def populate_dest_dir(tmpd, version):
    deps = get_dep_paths()
    dest_dir = os.path.join(tmpd, f"geckodriver-{version}")
    os.mkdir(dest_dir)

    # Copy main sources.
    geckodriver_dest_dir = os.path.join(dest_dir, f"geckodriver")
    shutil.copytree(".", geckodriver_dest_dir)

    # Copy local dependencies.
    for dep in deps:
        dep_dest_dir = os.path.join(geckodriver_dest_dir, dep)
        os.makedirs(os.path.dirname(dep), exist_ok=True)  # Scaffold dirs.
        shutil.copytree(dep, dep_dest_dir)
        return os.path.basename(dest_dir)


def get_dep_paths():
    """Find local dependencies that need to be distributed along with the
    geckodriver sources"""

    with open("Cargo.toml") as f:
        cargo_toml = toml.load(f)

    paths = set()
    for dep in cargo_toml["dependencies"].values():
        if not isinstance(dep, dict):
            # Then it's a simple dependency that can't have a `path` override.
            # e.g. `base64 = "0.10"`.
            continue

        if "path" not in dep:
            # Doesn't have a `path` override.
            continue

        path = dep["path"]
        if path.startswith("./") or (len(path) > 0 and path[0].isalnum()):
            # A crate in a subdir of CWD. No need to consider.
            continue

        assert path.startswith("../")
        paths.add(path)
    return paths


def make_tarball(tmpd, direc):
    tgz_name = f"{direc}.tar.gz"
    tgz_path = os.path.abspath(os.path.join(OUT_DIR, tgz_name))
    os.chdir(tmpd)
    with tarfile.open(tgz_path, "w:gz") as tgz:
        tgz.add(direc)
    return tgz_path


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.stderr.write(__doc__)
        sys.exit(1)

    main(sys.argv[1])
