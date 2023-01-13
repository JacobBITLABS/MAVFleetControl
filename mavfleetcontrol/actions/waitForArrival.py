import geopy.distance
import asyncio
from MAVFleetControl.mavfleetcontrol.craft import Craft
from MAVFleetControl.mavfleetcontrol.craft import State
from MAVFleetControl.mavfleetcontrol.states.position import Position
from MAVFleetControl.mavfleetcontrol.actions.emergency import Emergency

class WaitForArrival:
    """
        Class responsible for waiting for a drone to reach its desired location
    """
    def __init__(self, position: Position, drone: Craft):
        self.position = position
        self.drone = drone
        self.tolerance = 3.0 # 5 meters tolerence

    def dist(self, a: Position, b: Position):
        return geopy.distance.distance((a.lat, a.lng), (b.lat, b.lng)).m

    async def __call__(self, drone: Craft):
        drone.state = State.Travel # maybe this should be something different???
        print("WaitForArrival")
        while True:
            if not drone.conn.telemetry.health_all_ok:
                print("-- drone ", drone.id, " is having issues aborting")
                drone.tasking.empty() # empty event loop
                drone.add_action(Emergency())
                break

            if self.dist(drone.position, self.position) > self.tolerance:
                await asyncio.sleep(2) # sleep for 0.2 second
            else:
                drone.state = State.Wait # is at a waypoint
                break
