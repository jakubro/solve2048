import argparse
import datetime
import logging
import random
import sys

_log = logging.getLogger()


def main() -> None:
    parser = argparse.ArgumentParser(description="2048 game.")
    parser.add_argument(
        'action', choices=['solve', 'play'])
    parser.add_argument(
        '-ww', '--width', type=int, default=3,  # 4
        help="Width of the board.")
    parser.add_argument(
        '-hh', '--height', type=int, default=3,  # 4
        help="Height of the board.")
    parser.add_argument(
        '-v', '--verbose', action='store_true',
        help="Be verbose.")
    parser.add_argument(
        '-vv', '--debug', action='store_true',
        help="Be even more verbose.")
    parser.add_argument(
        '--depth', type=int, default=5,  # 6
        help="Number of steps to look forward. -1 for unlimited steps.")
    parser.add_argument(
        '--score', type=int, default=512,  # 2048
        help="Game ends when player achieves this score.")
    parser.add_argument(
        '--cache-size', type=int, default=None,  # 32
        help="Cache size. (Actual cache size is 2 ** cache_size)")
    parser.add_argument(
        '--search-algorithm', choices=['expectimax', 'minimax'],
        default='expectimax',
        help="Search algorithm")

    args = parser.parse_args()
    setup_logging(args)

    random.seed(0)
    sys.setrecursionlimit(1500)

    if args.cache_size:
        import cache
        cache.CACHE_MAXSIZE = 2 ** args.cache_size

    if args.action == 'solve':
        solve(args)
    else:
        assert args.action == 'play'
        play(args)


def solve(args: argparse.Namespace) -> None:
    import rules
    import search

    game_ = rules.Game2048.initialize(
        size=(args.height, args.width),
        terminal_score=args.score)

    i = 0
    dt = None
    while True:
        print("\n---------------------------------------------")
        update_statistics(game_, i, dt)
        i += 1
        dt = datetime.datetime.now()

        if game_.score() >= args.score:
            print("\n---------------------------------------------")
            print("\nAI won!")
            break

        # Max's (AI player) ply

        try:
            if args.search_algorithm == 'expectimax':
                action = search.expectimax_decision(
                    game_,
                    depth=args.depth,
                    alpha=game_.min_utility(),
                    beta=game_.max_utility())
            else:
                assert args.search_algorithm == 'minimax'
                action = search.expectimax_decision(
                    game_,
                    depth=args.depth,
                    alpha=game_.min_utility(),
                    beta=game_.max_utility())
        except KeyboardInterrupt:
            break
        except StopIteration:
            print("\n---------------------------------------------")
            print("\nAI lost!")
            break
        else:
            print(f"\n{action['direction'].name}")
            game_ = game_.invoke(**action)

        # Min's (opponent) ply

        actions = game_.actions()
        if not actions:
            continue
        game_ = game_.invoke(**random.choice(actions))


def play(args: argparse.Namespace) -> None:
    import rules

    game_ = rules.Game2048.initialize(
        size=(args.height, args.width),
        terminal_score=args.score)

    i = 0
    dt = None
    while True:
        print("\n---------------------------------------------")
        update_statistics(game_, i, dt)
        i += 1
        dt = datetime.datetime.now()

        if game_.score() >= args.score:
            print("\n---------------------------------------------")
            print("You won!")
            break

        # Max's (player) ply

        actions = game_.actions()
        if not actions:
            print("\n---------------------------------------------")
            print("You lost!")
            break

        print("Type W for UP, A for LEFT, S for DOWN and D for RIGHT:  ",
              end='')
        s = input().lower()
        if s == 'w':
            direction = rules.Direction.UP
        elif s == 's':
            direction = rules.Direction.DOWN
        elif s == 'a':
            direction = rules.Direction.LEFT
        elif s == 'd':
            direction = rules.Direction.RIGHT
        else:
            continue

        try:
            action = next(a for a in actions if a['direction'] == direction)
        except StopIteration:
            continue

        game_ = game_.invoke(**action)

        # Min's (opponent) ply

        actions = game_.actions()
        if not actions:
            continue
        game_ = game_.invoke(**random.choice(actions))


def update_statistics(game_, i, dt):
    utility = game_.utility()
    score = game_.score()
    actions = game_.actions()

    now = datetime.datetime.now()
    elapsed = (now - dt).total_seconds() if dt else "-"

    print(f"\n{game_}")
    print(f"\nIteration: {i}. Elapsed: {elapsed}. "
          f"Utility: {utility:.2f}. Score: {score}. "
          f"Directions: {[d['direction'].name for d in actions]}")

    for a in actions:
        d = a['direction']
        ply = game_.invoke(**a)
        _log.info(f"\t{d.name}\t"
                  f"Utility: {ply.utility()}. Score: {ply.score()}")

    print()


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
