import sys
from iriscasttools.main import get_iriscast_stats, parse_args

cmd_args = parse_args(sys.argv[1:])
print(get_iriscast_stats(cmd_args.as_csv, cmd_args.include_header))
