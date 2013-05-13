
def main():
    from mbrat.argparser import parser
    from mbrat.commander import load_commands

    load_commands()
    args = parser.parse_args()
    args.command.run(args)
