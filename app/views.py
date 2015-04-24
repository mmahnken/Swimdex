from flask import render_template, request
from flask.ext.login import LoginManager

from app import app
from model import IntervalFactory, MidDistanceWorkout

# import pdb

TIME_FACTOR = 0.2  # 0.2 of every 60 minutes is REST

login_manager = LoginManager()
login_manager.init_app(app)

@app.route('/')
@app.route('/index')
def index():
    return render_template("index.html")


@app.route('/workout')
def get_workout():
    if request.args:
        total_time = request.args.get('total_time')
        total_dist = request.args.get('total_distance')
        base = request.args.get('base')
        dist = request.args.get('distance')

        if total_dist:
            total_dist = int(total_dist)
        if total_time:
            total_time = int(total_time)

        if base and dist:
            try:
                dist = int(dist)
                mins, secs = base.split(':')
                base = convert_time_to_seconds(int(mins), int(secs))
            except:
                # TODO: actually throw an error here
                print "Invalid input"
        else:
            base = 90
            dist = 100

        i = IntervalFactory(base_seconds=base, base_distance=dist)

        if total_dist and total_time:
            # TODO: compromise the two params
            print "got two params for workout"
            print total_dist, total_time

        if not total_time and not total_dist:
            # TODO: throw an error here
            return "not enough params"

        if total_time and not total_dist:
            total_dist = convert_time_to_distance(int(total_time), i)

        workout = MidDistanceWorkout(interval_factory=i,
                                     distance=total_dist)

        return render_template("workout.html",
                               workout_lines=workout.pretty.split('\n'),
                               workout=workout)
    else:
        return render_template("index.html")


def convert_time_to_distance(num_minutes, interval_factory):
    """Helper fn that takes an interval factory object with number
    of minutes, and computes how far the swimmer with that
    inverval factory could swim in that amount of time.

    Depends on global TIME_FACTOR defined above
    TODO: let this depend on the swimmer's preference
    """
    num_seconds_for_100 = interval_factory.make_interval_as_seconds(100)
    num_seconds = (num_minutes - (num_minutes*0.2)) * 60
    seconds_per_yard = num_seconds_for_100/100
    num_yards = seconds_per_yard * num_seconds
    return num_yards


def convert_time_to_seconds(minutes, seconds):
    """Helper fn that takes minutes, seconds, and
    optionally, a time object, and returns
    the total number of seconds for these inputs.
    """
    return (minutes * 60) + seconds
