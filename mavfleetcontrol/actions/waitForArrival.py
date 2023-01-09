import geopy.distance
import asyncio
from craft import Craft
from craft import State
from states.position import Position
from  MAVFleetControl.mavfleetcontrol.actions.emergency import Emergency

class WaitForArrival:
    def __init__(self, position: Position, drone: Craft):
        self.position = position
        self.drone = drone
        self.tolerance = 5.0 # 5 meters tolerence

    def dist(self, a: Position, b: Position):
        return geopy.distance.geodesic((a.lat, a.lng), (b.lng, b.lng)).m

    async def __call__(self, drone: Craft):
        drone.state = State.Travel # maybe this should be something different???
        while True:
            if not drone.conn.telemetry.health_all_ok:
                print("-- drone ", drone.id, " is having issues aborting")
                drone.tasking.empty() # empty event loop
                drone.add_action(Emergency())
                break

            if self.dist(drone.position, self.position) > self.tolerance:
                # drone.state = State.Travel
                await asyncio.sleep(0.5) # sleep for 0.2 second
            else:
                drone.state = State.Wait # is at a waypoint
                break
