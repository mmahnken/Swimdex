import datetime
import random
import math

# SET_POPULATION = [1, 1, 1, 1, 2, 3, 4, 5]
# WORKOUT_POPULATION = [3, 3, 3, 3, 4, 5, 6]
LONG_DISTANCE = [200, 200, 200, 200, 225, 250, 275, 300, 300, 400, 500, 1000]
MID_DISTANCE = [100, 100, 100, 100, 125, 150, 150, 175]
SHORT_DISTANCE = [25, 50, 50, 75]


DISTANCES = {
    "mid": MID_DISTANCE,
    "long": LONG_DISTANCE,
    "short": SHORT_DISTANCE,
    "all": SHORT_DISTANCE + MID_DISTANCE + LONG_DISTANCE
}


class IntervalFactory(object):
    '''Interface for computing intervals for a workout.

    Defaults to 100 yard base interval.

    TODO: handle the quickening of intervals as yardage increases
    ie a different scale when num_yards > 500 or something '''

    def __init__(self, base_seconds, base_distance=100, distance_type='yards'):
        self.base = base_seconds
        self.distance_type = distance_type
        self.base_distance = base_distance

    def make_interval_as_seconds(self, distance, base=None):
        if not base:
            base = self.base
        if self.distance_type == 'meters':
            return base / 91.44 * distance
        elif self.distance_type == 'yards':
            return base / 100.0 * distance
        else:
            # raise InvalidDistanceType
            return "Invalid dist type"  # Actually throw an error here.

    def make_interval_as_time(self, distance=None, base=None, pretty=False):
        if not base:
            base = self.base
        if not distance:
            distance = self.base_distance
        minutes = self.make_interval_as_seconds(distance) / 60
        seconds = self.make_interval_as_seconds(distance) % 60
        time_obj = datetime.time(minute=int(minutes), second=int(seconds))
        if pretty:
            return "%s:%s:%s" % (time_obj.hour, time_obj.minute, time_obj.second)
        return time_obj

    def butterfly(self, distance, seconds=False):
        base = self.base + 5  # TODO: make this right
        if seconds:
            return self.make_interval_as_seconds(distance, base=base)
        return self.make_interval_as_time(distance, base=base)

    def back(self, distance, seconds=False):
        base = self.base + 5  # TODO: make this right
        if seconds:
            return self.make_interval_as_seconds(distance, base=base)
        return self.make_interval_as_time(distance, base=base)

    def breast(self, distance, seconds=False):
        base = self.base + 5  # TODO: make this right
        if seconds:
            return self.make_interval_as_seconds(distance, base=base)
        return self.make_interval_as_time(distance, base=base)

    def free(self, distance, seconds=False):
        if seconds:
            return self.make_interval_as_seconds(distance)
        return self.make_interval_as_time(distance)


class Swimmer(object):
    def __init__(self, interval_factory):
        self.interval_factory = interval_factory


class AbstractSet(object):
    '''attrs: num_reps, distance, total_distance
       methods:  set.long_distance(), set.sprint(), etc. are "flavor" functions to change set type;
                set.adjust_time(new_time), set.adjust_distance(new_distance) are to change attrs/props.
       properties: total_distance, total_time, pretty (pretty print the set)
    '''

    valid_flavors = ["long distance", "middle distance", "sprint", "drill", "transition"]
    valid_strokes = ["FL", "BK", "BR", "FR", "IM"]

    def __init__(self,
                 interval_factory,
                 num_reps=None,
                 total_distance=None,
                 distance=None,
                 stroke=None,
                 length=None
                 ):
        self.interval_factory = interval_factory
        if distance and num_reps:
            self.distance = distance
            self.num_reps = num_reps
            self.compute_total_distance(total_distance)
        # if stroke:
            # make a random set with stroke constraint
        self.stroke = stroke
        self.generate(total_distance, length)

    def generate(self, total_distance=None, length=None):
        if not total_distance:
            total_distance = 1000
        distance = random.choice(self.set_distance_population)
        num_reps = total_distance / distance
        new_total = num_reps * distance

        while not num_reps % 1 == 0:
            distance = random.choice(self.set_distance_population)
            num_reps = total_distance / distance
            new_total = num_reps * distance
        self.num_reps = num_reps
        self.distance = distance
        self.compute_total_distance(new_total)
        print "\ngenerated %s\n" % self.pretty

    def generate_random(self, total_distance=None):
        if not total_distance:
            total_distance = random.choice(range(100, 1000, 50))
        distance = total_distance / random.choice(range(2, 20, 2))
        num_reps = total_distance / distance
        while distance < 25 or num_reps < 1 or 100 % distance not in [0, 100] or distance % 100 % 25 != 0:
            distance = total_distance / random.choice(range(2, 20, 2))
            num_reps = total_distance / distance
        self.num_reps = num_reps
        self.distance = distance
        self.compute_total_distance(None)

    def transition(self):
        '''assign num_reps, interval, and stroke for transition set'''
        pass

    def drill(self):
        '''assign num_reps, interval, and stroke for a drill set'''
        pass

    def adjust_dist(distance, type_of_distance):
        ''' adjust the set to a specified distance'''
        pass

    def adjust_time(time_in_minutes):
        '''adjust the set to a specified amount of time'''
        pass

    def compute_total_distance(self, total_distance):
        if self.distance and self.num_reps:
            if not total_distance:
                self.total_distance = self.num_reps * self.distance
            else:
                self.total_distance = total_distance
        else:
            # Throw an error
            print "cannot compute total distance"
    @property
    def total_time(self):
        pass

    @property
    def pretty(self):
        i = self.interval_factory.make_interval_as_time(self.distance)
        return "%s X %s @ %s:%02d" % (self.num_reps, self.distance, i.minute, i.second)

class LongDistanceSet(AbstractSet):
    set_distance_population = [200, 200, 200, 200, 
        225, 250, 275, 300, 300, 400, 500, 1000]

class ShortDistanceSet(AbstractSet):
    set_distance_population = [25, 50, 50, 75]

class MidDistanceSet(AbstractSet):
    set_distance_population = [100, 100, 100, 100, 125, 150, 150, 175]

class SprintSet(AbstractSet):
    '''lots of rest, suffixed with SPRINT, takes in seconds of rest as parameter'''
    def __init__(self, rest=20):
        super(SprintSet, self).__init__()
        old_base = self.interval_factory.base
        old_base_distance = self.interval_factory.base_distance
        i = IntervalFactory(old_base, base_distance=old_base_distance)
        self.interval_factory = i


class AbstractWorkout(object):
    '''Pass in kwargs time (in minutes) or distance (in default yards) and
       distance type (yards or meters) to make workout.
       Takes in workout params, does pseudorandom computations, makes sets, returns a workout.'''
    num_sets = 4
    distance = 1650
    distance_type = 'yards'
    time = 45

    def __init__(self, **kwargs):
        self.interval_factory = IntervalFactory(base_seconds=90)
        if 'time' in kwargs:
            self.num_sets = kwargs['time'] / random.choice(self.set_total_time_population)
        elif 'distance' in kwargs:
            self.num_sets = kwargs['distance'] / random.choice(self.set_total_distance_population)

        for k, v in kwargs.iteritems():
            vars(self)[k] = v

    @property
    def pretty(self):
        pretty = ""
        pretty = "%s" % self.warmup
        if self.distance > self.total and self.goal_warmup and self.goal_warmup > self.warmup:
            pretty = pretty + "-%s" % self.goal_warmup
        pretty = pretty + " Warm Up\n"
        for s in self.sets:
            pretty = pretty + "%s\n" % s.pretty
        pretty = pretty + "%s" % self.cooldown
        if self.distance > self.total and self.goal_cooldown and self.goal_cooldown > self.cooldown:
            pretty = pretty + "-%s" % self.goal_cooldown
        pretty = pretty + " Cool Down\n"
        pretty = pretty + "Total: %s" % self.total
        if self.distance > self.total and self.distance > self.total:
            pretty = pretty + "-%s" % (self.goal_warmup + self.sets_total + self.goal_cooldown)
        return pretty


class ShortDistanceWorkout(AbstractWorkout):
    set_total_time_population = range(8, 30, 2)
    set_total_distance_population = range(200, 800, 50)
    min_cooldown_percentage = 0.20  # long cool down
    min_warmup_percentage = 0.10  # mid warmup
    # short dist sets
    

    def __init__(self, **kwargs):
        super(ShortDistanceWorkout, self).__init__(**kwargs)
        self.leftover = self.distance * 0.10
        self.generate()

    def generate(self):
        '''make a workout that fits in time/distance contraints'''

        min_leftover_total = self.distance * (self.min_warmup_percentage + self.min_cooldown_percentage)

        sets = []
        set_distance_sum = 0
        actual_leftover = min_leftover_total + 1

        while self.distance > set_distance_sum and min_leftover_total < actual_leftover:
            set_total_dist = random.choice(self.set_total_distance_population)
            s = ShortDistanceSet(self.interval_factory, total_distance=set_total_dist)
            actual_leftover = self.distance - (set_distance_sum + s.distance)
            if set_distance_sum + s.total_distance < self.distance:
                sets.append(s)
                set_distance_sum = set_distance_sum + s.total_distance
            else:
                break

        self.sets = sets
        self.sets_total = set_distance_sum
        self.goal_warmup = roundup(self.distance * self.min_warmup_percentage)
        self.goal_cooldown = roundup(self.distance * self.min_cooldown_percentage)
        self.warmup = roundup(self.sets_total * self.min_warmup_percentage)
        self.cooldown = roundup(self.sets_total * self.min_cooldown_percentage)
        self.total = self.sets_total + self.warmup + self.cooldown


class MidDistanceWorkout(AbstractWorkout):
    set_total_time_population = range(10, 60, 5)
    set_total_distance_population = range(500, 2000, 100)
    min_cooldown_percentage = 0.05  # short cooldown
    min_warmup_percentage = 0.20  # long warmup
    # mid dist sets

    def __init__(self, **kwargs):
        super(MidDistanceWorkout, self).__init__(**kwargs)
        self.generate()

    def generate(self):
        '''make a workout that fits in time/distance contraints'''

        min_leftover_total = self.distance * (self.min_warmup_percentage + self.min_cooldown_percentage)

        sets = []
        set_distance_sum = 0
        actual_leftover = min_leftover_total + 1

        while self.distance > set_distance_sum and min_leftover_total < actual_leftover:
            set_total_dist = random.choice(self.set_total_distance_population)
            s = MidDistanceSet(self.interval_factory, total_distance=set_total_dist)
            actual_leftover = self.distance - (set_distance_sum + s.distance)
            if set_distance_sum + s.total_distance < self.distance:
                sets.append(s)
                set_distance_sum = set_distance_sum + s.total_distance
            else:
                break

        self.sets = sets
        self.sets_total = set_distance_sum
        self.goal_warmup = roundup(self.distance * self.min_warmup_percentage)
        self.goal_cooldown = roundup(self.distance * self.min_cooldown_percentage)
        self.warmup = roundup(self.sets_total * self.min_warmup_percentage)
        self.cooldown = roundup(self.sets_total * self.min_cooldown_percentage)
        self.total = self.sets_total + self.warmup + self.cooldown


class LongDistanceWorkout(AbstractWorkout):
    set_total_time_population = range(30, 60, 5)
    set_total_distance_population = range(600, 3000, 100)
    min_cooldown_percentage = 0.10  # # mid cool down
    min_warmup_percentage = 0.10  # mid warmup
    # long dist sets

    def __init__(self, **kwargs):
        super(LongDistanceWorkout, self).__init__(**kwargs)
        self.generate()

    def generate(self):
        '''make a workout that fits in time/distance contraints'''

        min_leftover_total = self.distance * (self.min_warmup_percentage + self.min_cooldown_percentage)

        sets = []
        set_distance_sum = 0
        actual_leftover = min_leftover_total + 1

        while self.distance > set_distance_sum and min_leftover_total < actual_leftover:
            set_total_dist = random.choice(self.set_total_distance_population)
            s = LongDistanceSet(self.interval_factory, total_distance=set_total_dist)
            actual_leftover = self.distance - (set_distance_sum + s.distance)
            if set_distance_sum + s.total_distance < self.distance:
                sets.append(s)
                set_distance_sum = set_distance_sum + s.total_distance
            else:
                break

        self.sets = sets
        self.sets_total = set_distance_sum
        self.goal_warmup = roundup(self.distance * self.min_warmup_percentage)
        self.goal_cooldown = roundup(self.distance * self.min_cooldown_percentage)
        self.warmup = roundup(self.sets_total * self.min_warmup_percentage)
        self.cooldown = roundup(self.sets_total * self.min_cooldown_percentage)
        self.total = self.sets_total + self.warmup + self.cooldown


def roundup(x):
    return int(math.ceil(x / 25.0)) * 25
