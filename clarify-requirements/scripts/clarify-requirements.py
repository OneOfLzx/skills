import argparse
import json
import os
import sys


def _is_interactive() -> bool:
    return sys.stdin is not None and sys.stdin.isatty()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Ask one interactive question and return a JSON answer."
    )
    parser.add_argument(
        "--question",
        required=True,
        help="Question text to show the user (single question).",
    )
    parser.add_argument(
        "--no-json",
        action="store_true",
        help="Print only the raw answer (not JSON).",
    )
    parser.add_argument(
        "--allow-empty",
        action="store_true",
        help="Allow empty answer.",
    )
    args = parser.parse_args()

    if not _is_interactive():
        sys.stderr.write(
            "interactive_clarify.py requires an interactive TTY (stdin).\n"
            "Run it in a real terminal session so it can block for user input.\n"
        )
        return 2

    q = args.question.strip()
    if not q:
        sys.stderr.write("--question must be non-empty.\n")
        return 2

    sys.stdout.write("\n=== Clarify Question ===\n")
    sys.stdout.write(q + "\n")
    sys.stdout.write("------------------------\n")
    sys.stdout.write("Your answer: ")
    sys.stdout.flush()

    try:
        answer = input()
    except (EOFError, KeyboardInterrupt):
        sys.stderr.write("\nNo answer provided.\n")
        return 130

    if not args.allow_empty and not answer.strip():
        sys.stderr.write("Empty answer is not allowed.\n")
        return 2

    if args.no_json:
        sys.stdout.write(answer + ("\n" if not answer.endswith("\n") else ""))
        return 0

    payload = {"answer": answer}
    sys.stdout.write(json.dumps(payload, ensure_ascii=False))
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

