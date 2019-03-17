import argparse
import logging

import rules


def main() -> None:
    parser = argparse.ArgumentParser(description="2048 game.")
    parser.add_argument(
        'action', choices=['solve', 'play'])
    parser.add_argument(
        '-ww', '--width', type=int, default=5,
        help="Width of the board.")
    parser.add_argument(
        '-hh', '--height', type=int, default=5,
        help="Height of the board.")
    parser.add_argument(
        '-v', '--verbose', action='store_true',
        help="Be verbose.")
    parser.add_argument(
        '-vv', '--debug', action='store_true',
        help="Be even more verbose.")

    args = parser.parse_args()
    setup_logging(args)

    if args.action == 'solve':
        solve(args)
    else:
        assert args.action == 'play'
        play(args)


def solve(args: argparse.Namespace) -> None:
    raise NotImplementedError()


def play(args: argparse.Namespace) -> None:
    problem_ = rules.Game2048.initialize(width=args.width, height=args.height)
    while True:
        print(f"\n{problem_}")
        print("\nType W for UP, A for RIGHT, S for DOWN and L for LEFT:  ",
              end='')

        s = input().lower()
        if s == 'w':
            action = rules.Action.UP
        elif s == 's':
            action = rules.Action.DOWN
        elif s == 'a':
            action = rules.Action.LEFT
        elif s == 'd':
            action = rules.Action.RIGHT
        else:
            continue

        problem_ = problem_.invoke(action)


def setup_logging(args: argparse.Namespace) -> None:
    log = logging.getLogger()
    if args.debug:
        log.setLevel(logging.DEBUG)
    elif args.verbose:
        log.setLevel(logging.INFO)
    else:
        log.setLevel(logging.WARNING)
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(message)s')
    handler.setFormatter(formatter)
    log.addHandler(handler)


if __name__ == '__main__':
    main()
