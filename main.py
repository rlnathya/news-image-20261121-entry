#!/usr/bin/env python3
"""Entrypoint for the news-image-20261121 bounty.

Copies the pre-rendered front page (entry.png) to the output directory
the grader provides through MAKEFUN_OUTPUT_DIR (or /output by default).
Python 3.13, standard library only; it runs offline, twice, and writes
identical bytes on every run because it only copies a fixed file.
"""

import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    shutil.copyfile(os.path.join(HERE, "entry.png"),
                    os.path.join(out_dir, "entry.png"))


if __name__ == "__main__":
    main()
