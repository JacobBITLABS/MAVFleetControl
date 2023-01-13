import asyncio
from mavsdk import System
from MAVFleetControl.mavfleetcontrol.craft import Craft
from MAVFleetControl.mavfleetcontrol.craft import State

class GoTo:
    """
        Class responsible for instructing a drone to fly towards a location
    """
    def __init__(self, position, altitude=12.0):
        self.position = position
        self.altitude = altitude

    async def __call__(self, drone: Craft):
        print("-- Fetching amsl altitude at home location....") # asml: above mean sea level
        async for terrain_info in drone.conn.telemetry.home():
            absolute_altitude = terrain_info.absolute_altitude_m
            break

        # if drone is not flying
        async for in_air in drone.conn.telemetry.in_air():
            if in_air:
                break

            # Do takeoff
            print("-- Arming")
            await drone.conn.action.arm()
            print("-- Taking off")
            await drone.conn.action.takeoff()
            # Wait for takeoff
            await asyncio.sleep(50)

        drone.state = State.Travel
        # To fly drone 20m above the ground plane
        flying_alt = absolute_altitude + self.altitude # default 20.0
        # goto_location() takes Absolute MSL altitude
        latitude_deg = self.position[0]
        longitude_deg = self.position[1]
        await drone.conn.action.goto_location(latitude_deg, longitude_deg, flying_alt, 0)
        print("GOTO", latitude_deg, longitude_deg, flying_alt)
