
def main():
    from mbrat.argparser import parser
    from mbrat.commander import load_commands

    load_commands()
    args = parser.parse_args()
    run = args.command.run(args)
    if not run:
        exit(1)
