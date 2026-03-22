from __future__ import annotations

import sys
from typing import Sequence

from .diagnostics import render_dev_report
from .resources import read_version, render_help
from .runtime import UNSUPPORTED_EXIT, execute


HELP_TOKENS = {"ajuda", "help", "--help", "-h"}
VERSION_TOKENS = {"version", "--version", "-v"}


def main(argv: Sequence[str] | None = None) -> int:
    args = list(argv if argv is not None else sys.argv[1:])
    if not args:
        print("❌ comando inválido")
        return 1

    first = args[0].strip().lower()

    if first in HELP_TOKENS:
        print(render_help())
        return 0

    if first in VERSION_TOKENS:
        print(f"💜 Aury {read_version()}")
        return 0

    if first == "dev":
        phrase = " ".join(args[1:]).strip()
        print(render_dev_report(phrase))
        return 0 if phrase else 1

    text = " ".join(args).strip()
    return execute(text)


if __name__ == "__main__":
    raise SystemExit(main())
