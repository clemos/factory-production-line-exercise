import random

class Task:
    """Base Task class, implements timeout interface"""
    timeout = 1.0

    def is_complete(self):
        """Returns true if the task is complete i.e. when timeout is zero"""
        return self.timeout <= 0.0

    def start(self, state):
        """Called when starting the task.
        `state` is the production line"""
        pass

    def end(self, state):
        """Called when the task is ended.
        `state` is the production line"""
        pass
    
    def tick(self, delta):
        """Decrement internal `timeout` by `delta`"""
        self.timeout = self.timeout - delta

# TASK IMPLEMENTATION

class MineFoo(Task):

    timeout = 1.0

    FOO_OUTCOME = 1

    def end(self, state):
        """Ends mining foo: add 1 to foo count"""
        state.foo = state.foo + self.FOO_OUTCOME
        pass
    
    def __str__(self):
        return f'mining foo (timeout {self.timeout})'

class MineBar(Task):

    MIN_TIMEOUT = 0.5
    MAX_TIMEOUT = 2

    BAR_OUTCOME = 1

    def __init__(self):
        """Create mining bar task: calculate random timeout"""
        self.timeout = random.random() * (self.MAX_TIMEOUT-self.MIN_TIMEOUT) + self.MIN_TIMEOUT    
    
    def end(self, state):
        """Ends mining bar: increments bar by one"""
        state.bar = state.bar + self.BAR_OUTCOME

    def __str__(self):
        return f'mining bar (timeout {self.timeout})'


class AssembleFooBar(Task):
    timeout = 2.0

    FOO_COST = 1
    BAR_COST = 1

    SUCCESS_RATE = 0.6

    def start(self, state):
        """Starts assembling foobar: picks one foo and one bar"""
        assert(state.foo >= self.FOO_COST)
        assert(state.bar >= self.BAR_COST)
        state.foo = state.foo - self.FOO_COST
        state.bar = state.bar - self.BAR_COST

    def end(self, state):
        """Ends assembling foobar: adds a foobar, or put back a bar"""
        if random.random() <= self.SUCCESS_RATE:
            # Success! Add a foobar
            state.foobar = state.foobar + 1
        else:
            # Failure: Put back a bar
            state.bar = state.bar + 1
    
    def __str__(self):
        return f'assemble foobar (timeout {self.timeout})'

class SellFooBar(Task):
    timeout = 10.0
    MAX_FOOBAR_COST = 5

    def __init__(self, number_to_sell):
        """Constructor: stores the number of foobars to sell"""
        assert(number_to_sell >= self.MAX_FOOBAR_COST)
        self.number_to_sell = number_to_sell

    def start(self, state):
        """Starts selling foobars: pick selected number of foobars"""
        state.foobar = state.foobar - self.number_to_sell

    def end(self, state): 
        """Ends selling foobars: add money for the selected number of foobars"""
        state.money = state.money + self.number_to_sell
    
    def __str__(self):
        return f'sell {self.number_to_sell} foobar(s) (timeout {self.timeout})'
    
class BuyRobot(Task):

    timeout = 1.0

    MONEY_COST = 3
    FOO_COST = 6

    def start(self, state):
        """Starts buying a robot: pick 3 money and 6 foo"""
        assert(state.money >= self.MONEY_COST)
        assert(state.foo >= self.FOO_COST)
        state.money = state.money - self.MONEY_COST
        state.foo = state.foo - self.FOO_COST

    def end(self, state):
        """Ends buying a robot: add a new robot to the pool"""
        state.add_new_robot()
    
    def __str__(self):
        return f'buy robot (timeout {self.timeout})'


class ProductionLine:
    # internal production line time
    time = 0.0

    # number of foos mined
    foo = 0

    # number of bars mined
    bar = 0

    # number of foobars assembled
    foobar = 0

    # amount of money earned
    money = 0

    # represents the pool of robots, each slot is a robot and contains its current task
    tasks = []

    TASK_SWITCHING_PENALTY = 5.0

    def __init__(self, min_robots, max_robots):
        self.min_robots = min_robots
        self.max_robots = max_robots

    def start(self):
        """Starts the production line: add `min_robots` new robots, and call tick until `max_robots` is reached"""
        for i in range(0,self.min_robots):
            self.add_new_robot()

        while len(self.tasks) < self.max_robots:
            self.next_tick()

        print(f'finished generating {self.max_robots} robots !')
      
    def next_tick(self):
        """Processes with all tasks until one task is finished, and reassign robots who completed to a new task"""

        # Pick the next ending task from the list, i.e. the one with the lowest timeout
        tasks_by_timeout = sorted(self.tasks, key=lambda task: task.timeout)
        next_ending_task = tasks_by_timeout[0]

        # `delta` represents the amount of time until next ending task is complete
        delta = next_ending_task.timeout

        # increment internal time
        self.time = self.time + delta

        print('---')
        print(self)

        # updates all task by `delta`
        for task in self.tasks:
            task.tick(delta)
            
        # ends completed tasks and pick new tasks
        for index, task in enumerate(self.tasks):
            if task.is_complete():
                print(f'robot #{index}')
                print(f'\tending: {task}')
                task.end(self)
                # select next task, eventually adding switch task penalty
                next_task = self.switch_to_task(self.select_next_task(task), task)
                next_task.start(self)
                print(f'\tnew task: {next_task}')
                # replace ended task with new task
                self.tasks[index] = next_task

    def switch_to_task(self, task, previous_task):
        """Apply timeout penalty to `task` if `previous_task` is not of the same type as `task`"""

        if (not previous_task is None) and (not type(task) is type(previous_task)):
            task.timeout = task.timeout + self.TASK_SWITCHING_PENALTY
        return task

    def select_next_task(self, task=None):
        """Selects the next task for a robot.
        Passed task is the previous task, if any.
        This method can be used to optimize the production line algorithm.
        Its current implementation is naive and unoptimized, especially regarding switching cost,
        as previous task is not taken into account.

        A possible optimization to avoid switching would be to compute a bunch of foos and bars in reserve before switching to new tasks:
        2 robots mine X foos and bars
        then the bar bot switches to assemble all foobars
        then to sell all of them until money is roughly half the number of available foos
        then buy as many robots as possible

        Then we likely have enough robots to setup an optimized production line:
        half robots mine Y foos, half robots mine X bars (X and Y to be determined)
        then a portion of the robots move to assembling everything,
        then a portion move to selling everything,
        then a portion move to buying as much robots as possible

        all proportions to be determined by worst case scenario to avoid needing robots going back to mining
        """

        # The first two robots always mine foos and bars
        n_tasks = len(self.tasks)
        if n_tasks == 0:
            return MineFoo()
        elif n_tasks == 1:
            return MineBar()

        # Otherwise, try to buy a robot, or sell 5 foobar, or assemble a foobar if possible

        # Buy a robot if possible
        if self.foo >= BuyRobot.FOO_COST and self.money >= BuyRobot.MONEY_COST:
            return BuyRobot()
        
        # Sell 5 foobars if possible
        if self.foobar >= SellFooBar.MAX_FOOBAR_COST:
            return SellFooBar(5)
            
        # Assemble foobar if possible
        # always keeping 6 foos to eventually buy a robot
        if self.foo >= BuyRobot.FOO_COST+AssembleFooBar.FOO_COST and self.bar >= AssembleFooBar.BAR_COST:
            return AssembleFooBar()
    
        # If none is possible, go back to mining either bars if less numerous than foos
        if self.foo >= self.bar:
            return MineBar()
        
        # ... or back to mining foos
        return MineFoo()

    def add_new_robot(self):
        """Adds a new robot to the pool, selects a task for him and start it"""

        new_task = self.select_next_task()
        new_task.start(self)
        self.tasks.append(new_task)

    def __str__(self):
        outp = f'time = {self.time},\nfoo = {self.foo}, bar = {self.bar}, foobar = {self.foobar}, money = {self.money}, robots = {len(self.tasks)}'
        for task in self.tasks:
            outp = outp + f'\n\t-> {task}'
        return outp

state = ProductionLine(min_robots=2, max_robots=30)
state.start()
