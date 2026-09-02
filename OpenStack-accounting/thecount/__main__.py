import sys

from thecount.cli import setup_parser, build_config
from thecount.run_jobs import run_jobs

def main() -> int:
    """main function - sets up parser, parses args and calls run_jobs()"""
    parser = setup_parser()
    args = parser.parse_args()

    try:
        run_details = build_config(args)
    except ValueError as exc:
        parser.error(str(exc))

    run_jobs(run_details)
    return 0


if __name__ == "__main__":
    sys.exit(main())
