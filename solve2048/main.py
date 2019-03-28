import argparse
import logging
import random
import sys

import rules
import search

_log = logging.getLogger()

random.seed(0)
sys.setrecursionlimit(1500)


def main() -> None:
    parser = argparse.ArgumentParser(description="2048 game.")
    parser.add_argument(
        'action', choices=['solve', 'play'])
    parser.add_argument(
        '-ww', '--width', type=int, default=3,
        help="Width of the board.")
    parser.add_argument(
        '-hh', '--height', type=int, default=3,
        help="Height of the board.")
    parser.add_argument(
        '-v', '--verbose', action='store_true',
        help="Be verbose.")
    parser.add_argument(
        '-vv', '--debug', action='store_true',
        help="Be even more verbose.")
    parser.add_argument(
        '--depth', type=int, default=10,
        help="Number of steps to look forward. -1 for unlimited steps.")
    parser.add_argument(
        '--score', type=int, default=512,
        help="Game ends when player achieves this score.")

    args = parser.parse_args()
    setup_logging(args)

    if args.action == 'solve':
        solve(args)
    else:
        assert args.action == 'play'
        play(args)


def solve(args: argparse.Namespace) -> None:
    game_ = rules.Game2048.initialize(
        width=args.width,
        height=args.height,
        terminal_score=args.score)

    depth = args.depth

    i = 0
    while True:
        i += 1

        utility = game_.utility()
        score = game_.score()
        directions = [d['direction'] for d in game_.actions()]

        # max's (AI player) ply

        print(f"\n{game_}")
        print(f"\nIteration: {i}. Utility: {utility}. Score: {score}. "
              f"Directions: {[d.name for d in directions]}")
        if score >= args.score:
            print(f"\n---------------------------------------------")
            print("\nAI won!")
            break

        for d in directions:
            temp = game_.invoke(player=+1, direction=d)
            _log.info(f"\t{d.name}\t"
                      f"Utility: {temp.utility()}. Score: {temp.score()}")

        # if i % 10 == 0:
        #     depth = depth + 1
        print(f"\nDepth: {depth}")

        try:
            # action = search.minimax_decision(game_, depth=depth)
            action = search.expectimax_decision(game_, depth=depth)
        except KeyboardInterrupt:
            break
        except StopIteration:
            print(f"\n---------------------------------------------")
            print("\nAI lost!")
            break
        else:
            print(f"\n{action['direction'].name}")
            game_ = game_.invoke(**action)

        # min's (opponent) ply

        actions = game_.actions()
        if not actions:
            continue
        game_ = game_.invoke(**random.choice(actions))

        print(f"\n---------------------------------------------")


def play(args: argparse.Namespace) -> None:
    game_ = rules.Game2048.initialize(
        width=args.width,
        height=args.height,
        terminal_score=args.score)

    i = 0
    while True:
        i += 1

        utility = game_.utility()
        score = game_.score()
        directions = [d['direction'] for d in game_.actions()]

        print(f"\n{game_}")
        print(f"\nIteration: {i}. Utility: {utility}. Score: {score}. "
              f"Directions: {[d.name for d in directions]}")
        if score >= args.score:
            print(f"\n---------------------------------------------")
            print("\nYou won!")
            break

        for d in directions:
            temp = game_.invoke(player=+1, direction=d)
            _log.info(f"\t{d.name}\t"
                      f"Utility: {temp.utility()}. Score: {temp.score()}")

        # max's (player) ply

        actions = game_.actions()
        if not actions:
            print(f"\n---------------------------------------------")
            print("\nYou lost!")
            break

        print("\nType W for UP, A for LEFT, S for DOWN and D for RIGHT:  ",
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

        # min's (opponent) ply

        actions = game_.actions()
        if not actions:
            continue
        game_ = game_.invoke(**random.choice(actions))

        print(f"\n---------------------------------------------")


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
