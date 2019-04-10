An automated solver for the [2048 Game](https://en.wikipedia.org/wiki/2048_(video_game)). This program searches for a
solution using Expectimax algorithm with a heuristics which prefers sorted tiles.

Notes:

* The actual Expectimax search algorithm is in `search.py`. The command-line interface is in `main.py`.
`game.py` contains some boilerplate used to represent the problem in general, while `rules.py` contains the
actual rules of the 2048 Game.


To get started, run `main.py`:

```
$ python ./solve2048/main.py
usage: main.py [-h] [-ww WIDTH] [-hh HEIGHT] [-v] [-vv] [--depth DEPTH]
               [--score SCORE] [--cache-size CACHE_SIZE]
               [--search-algorithm {expectimax,minimax}]
               {solve,play}

2048 game.

positional arguments:
  {solve,play}

optional arguments:
  -h, --help            show this help message and exit
  -ww WIDTH, --width WIDTH
                        Width of the board.
  -hh HEIGHT, --height HEIGHT
                        Height of the board.
  -v, --verbose         Be verbose.
  -vv, --debug          Be even more verbose.
  --depth DEPTH         Number of steps to look forward. -1 for unlimited
                        steps.
  --score SCORE         Game ends when player achieves this score.
  --cache-size CACHE_SIZE
                        Cache size. (Actual cache size is 2 ** cache_size)
  --search-algorithm {expectimax,minimax}
                        Search algorithm
```

Example session (note that large portion of the output is omitted for brevity):

```
$ python ./solve2048/main.py --width 3 --height 3 --score 512 --depth 5 solve

---------------------------------------------

. . .
. . .
2 . .

Iteration: 0. Elapsed: -. Utility: 296.50. Score: 2. Directions: ['UP', 'RIGHT']


RIGHT

---------------------------------------------

. . .
. . .
2 . 2

Iteration: 1. Elapsed: 0.245572. Utility: 243.50. Score: 2. Directions: ['UP', 'RIGHT', 'LEFT']


UP

---------------------------------------------

2 2 2
. . .
. . .

Iteration: 2. Elapsed: 0.268227. Utility: 874.00. Score: 2. Directions: ['RIGHT', 'DOWN', 'LEFT']


RIGHT

---------------------------------------------

. 2 4
. 2 .
. . .

Iteration: 3. Elapsed: 0.356844. Utility: 139.00. Score: 4. Directions: ['UP', 'RIGHT', 'DOWN', 'LEFT']


LEFT

---------------------------------------------

2 4 .
2 . .
. 2 .

Iteration: 4. Elapsed: 0.513983. Utility: 450.50. Score: 4. Directions: ['UP', 'RIGHT', 'DOWN', 'LEFT']


LEFT

---------------------------------------------

2 4 .
2 . .
2 2 .

Iteration: 5. Elapsed: 0.570778. Utility: 942.50. Score: 4. Directions: ['UP', 'RIGHT', 'DOWN', 'LEFT']


UP

---------------------------------------------

4 4 .
2 2 .
. 2 .

Iteration: 6. Elapsed: 0.639437. Utility: 1056.00. Score: 4. Directions: ['UP', 'RIGHT', 'DOWN', 'LEFT']


LEFT

---------------------------------------------

8 . .
4 2 .
2 . .

Iteration: 7. Elapsed: 0.479102. Utility: 1588.50. Score: 8. Directions: ['UP', 'RIGHT', 'DOWN']


DOWN

---------------------------------------------

8 . .
4 . 2
2 2 .

Iteration: 8. Elapsed: 0.366372. Utility: 1808.50. Score: 8. Directions: ['UP', 'RIGHT', 'DOWN', 'LEFT']


DOWN

---------------------------------------------

8 . .
4 2 .
2 2 2

Iteration: 9. Elapsed: 0.5276. Utility: 1959.50. Score: 8. Directions: ['UP', 'RIGHT', 'DOWN', 'LEFT']


UP

---------------------------------------------

8 4 2
4 . 2
2 . .

Iteration: 10. Elapsed: 0.457273. Utility: 1917.00. Score: 8. Directions: ['UP', 'RIGHT', 'DOWN', 'LEFT']


LEFT

---------------------------------------------

8 4 2
4 2 .
2 . 2

Iteration: 11. Elapsed: 0.362493. Utility: 1386.00. Score: 8. Directions: ['UP', 'RIGHT', 'DOWN', 'LEFT']


UP

---------------------------------------------

8 4 4
4 2 2
2 . .

Iteration: 12. Elapsed: 4.283093. Utility: 2183.00. Score: 8. Directions: ['RIGHT', 'DOWN', 'LEFT']


LEFT

---------------------------------------------

8 8 .
4 4 .
2 2 .

Iteration: 13. Elapsed: 0.042796. Utility: 2100.00. Score: 8. Directions: ['RIGHT', 'LEFT']


LEFT

---------------------------------------------

16 .  2
8  .  .
4  .  .

Iteration: 14. Elapsed: 0.214677. Utility: 2744.50. Score: 16. Directions: ['RIGHT', 'DOWN', 'LEFT']


DOWN

---------------------------------------------

16 2  .
8  .  .
4  .  2

Iteration: 15. Elapsed: 0.277419. Utility: 2674.50. Score: 16. Directions: ['UP', 'RIGHT', 'DOWN', 'LEFT']


DOWN

---------------------------------------------

16 .  .
8  2  .
4  2  2

Iteration: 16. Elapsed: 0.268117. Utility: 3179.50. Score: 16. Directions: ['UP', 'RIGHT', 'DOWN', 'LEFT']


UP

---------------------------------------------

16 4  2
8  .  2
4  .  .

Iteration: 17. Elapsed: 0.34924. Utility: 2937.00. Score: 16. Directions: ['UP', 'RIGHT', 'DOWN', 'LEFT']


DOWN

---------------------------------------------

16 .  .
8  2  .
4  4  4

Iteration: 18. Elapsed: 0.298979. Utility: 3445.00. Score: 16. Directions: ['UP', 'RIGHT', 'LEFT']


UP

---------------------------------------------

16 2  4
8  4  2
4  .  .

Iteration: 19. Elapsed: 0.260401. Utility: 2760.00. Score: 16. Directions: ['RIGHT', 'DOWN']


DOWN

---------------------------------------------

16 2  .
8  2  4
4  4  2

Iteration: 20. Elapsed: 0.080746. Utility: 3621.50. Score: 16. Directions: ['UP', 'RIGHT', 'DOWN', 'LEFT']


DOWN

---------------------------------------------

16 .  2
8  4  4
4  4  2

Iteration: 21. Elapsed: 0.246112. Utility: 3472.50. Score: 16. Directions: ['UP', 'RIGHT', 'DOWN', 'LEFT']


DOWN

---------------------------------------------

...

---------------------------------------------

 2  128  64
 2  256  64
 .   2   4

Iteration: 260. Elapsed: 0.117743. Utility: 6757.50. Score: 256. Directions: ['UP', 'DOWN', 'LEFT']


UP

---------------------------------------------

 4  128 128
 2  256  4
 .   2   .

Iteration: 261. Elapsed: 0.15501. Utility: 6004.00. Score: 256. Directions: ['RIGHT', 'DOWN', 'LEFT']


LEFT

---------------------------------------------

 4  256  .
 2  256  4
 2   .   2

Iteration: 262. Elapsed: 0.163212. Utility: 4326.50. Score: 256. Directions: ['UP', 'RIGHT', 'DOWN', 'LEFT']


UP

---------------------------------------------

 4  512  4
 4   .   2
 .   2   .

Iteration: 263. Elapsed: 0.107998. Utility: 10000000000000000000.00. Score: 512. Directions: ['UP', 'RIGHT', 'DOWN', 'LEFT']


---------------------------------------------

AI won!
```
