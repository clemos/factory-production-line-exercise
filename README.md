# Factory Production Line Exercise

## Usage

Just:
```
python production-line.py
```

Will output a log of the production line activity to `stdout` in the form of a list of events.

Each event corresponds to the time of completion of one of more robot tasks

Each event starts with a `---` line, and outputs
1. current event time
2. number of resources available to the production line (foo, bar, foobar, money and robots)
3. list of ongoing robot tasks with their current timeout
4. list of robots who completed their tasks during this event, and which new task they have been assigned to next

Sample event:
```
---
time = 664.2953750876165,
foo = 3, bar = 3, foobar = 3, money = 2, robots = 29
        -> buy robot (timeout 0.45079961324662854)
        -> buy robot (timeout 10.12365989839571)
        -> assemble foobar (timeout 9.988049260943589)
        -> assemble foobar (timeout 5.701984232964747)
        -> assemble foobar (timeout 3.4225624714551035)
        -> assemble foobar (timeout 10.223090968089837)
        -> assemble foobar (timeout 3.2982013540256485)
        -> buy robot (timeout 1.1888534054865563)
        -> assemble foobar (timeout 3.441316441095987)
        -> assemble foobar (timeout 7.95204148618909)
        -> assemble foobar (timeout 3.2820471140257386)
        -> assemble foobar (timeout 9.441316441095983)
        -> mining bar (timeout 1.1556967168451762)
        -> assemble foobar (timeout 3.3152091647374267)
        -> assemble foobar (timeout 4.1728258007983055)
        -> assemble foobar (timeout 3.7088993843576485)
        -> assemble foobar (timeout 3.422975996010754)
        -> assemble foobar (timeout 9.952041486189094)
        -> assemble foobar (timeout 3.9939096476893403)
        -> buy robot (timeout 1.3165147439626868)
        -> assemble foobar (timeout 3.441316441095987)
        -> assemble foobar (timeout 3.8813383944762854)
        -> assemble foobar (timeout 4.005674230980377)
        -> assemble foobar (timeout 3.738698573596052)
        -> sell 5 foobar(s) (timeout 0.47900642924703796)
        -> assemble foobar (timeout 3.9520414861890933)
        -> assemble foobar (timeout 3.3031204534837055)
        -> assemble foobar (timeout 4.223090968089837)
        -> mining bar (timeout 1.0052341122803732)
robot #0
        ending: buy robot (timeout 0.0)
        new task: mining bar (timeout 1.1250158297220478)
```

Eventually, the script should output `finished generating 30 robots !` and exit.

## Notes

The script mainly instantiates a `ProductionLine`, with:
* `min_robots=2`: number of robots at beginning
* `max_robots=30`: number of robots to reach the end

`ProductionLine.tasks` represents the Production Line robots, and is just a list of ongoing tasks.

When calling `ProductionLine.start()`, the initial robots will be created (i.e. their tasks selected and started)
and `ProductionLine.next_tick()` will be called until the expected number of robots is reached

Within `ProductionLine.next_tick()`, we will:
* find the next ending task (the one with the lowest `timeout`)
* increment internal time to reach this ending, and update all tasks `timeout` accordingly
* end tasks that were completed, and select new tasks to start

`ProductionLine.select_next_task()` is the method that implements the business algorithm, i.e. the method responsible for
selecting the next task for a new robot, or for a robot who completed its task.

Each robot task is implemented by extending the `Task` class, overriding:
* `timeout`: the task duration; can be computed/overwritten during start()
* `start()`: start the task, typically by consuming resources from the `state` (i.e. production line) if required
* `end()`: end the task, typically by adding resources to the `state`