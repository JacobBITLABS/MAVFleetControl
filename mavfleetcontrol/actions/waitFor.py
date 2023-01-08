from craft import Craft
from MAVFleetControl.mavfleetcontrol.actions.waitForAmbulance import WaitFor
import geopy.distance
import asyncio

class WaitFor:
    def __init__(self, ambulance, drones, all_drones):
        self.ambulance = ambulance
        self.drones = drones
        self.all_drones = all_drones

    def dist(self, a, b):
        return geopy.distance.geodesic((a.latitude_deg, a.longitude_deg), (b.latitude_deg, b.longitude_deg)).m

    async def __call__(self, drone: Craft):
        while True:
            if not drone.conn.telemetry.health_all_ok:
                print("-- drone ", drone.id, " is having issues aborting")
                drone.tasking.empty() # empty event loop
                drone.add_action()

                break

            # test drones
            for other_drone in self.all_drones:
                # test that it is not the drone it self
                if not drone.id == other_drone.id and not drone.mission_id == other_drone.mission_id:
                    # test distance
                    if self.dist(drone.position, other_drone.position) < 5.0:
                        break # next waypoint pushed off the pin

            # test ambulances
            if self.dist(drone.position, self.ambulance.position) > 5.0:
                await asyncio.sleep(0.2) # sleep for 0.2 second
            else:
                break
                
