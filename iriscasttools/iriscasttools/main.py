import sys
from iriscasttools.stats import get_iriscast_stats, parse_args

if __name__ == "__main__":
    cmd_args = parse_args(sys.argv[1:])
    print(get_iriscast_stats(cmd_args.as_csv, cmd_args.include_header))
