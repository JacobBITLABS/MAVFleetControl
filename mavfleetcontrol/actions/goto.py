import asyncio
from mavsdk import System
from MAVFleetControl.mavfleetcontrol.craft import Craft
from MAVFleetControl.mavfleetcontrol.craft import State

class GoTo:
    def __init__(self, position, altitude=12.0):
        self.position = position
        self.altitude = altitude

    async def __call__(self, drone: Craft):
        print("-- Fetching amsl altitude at home location....") # asml: above mean sea level
        async for terrain_info in drone.conn.telemetry.home():
            absolute_altitude = terrain_info.absolute_altitude_m
            break

        # if drone is not flying
        #if not drone.conn.telemetry.in_air():
        async for is_armed in drone.conn.telemetry.in_air():
            if is_armed:
                break

            print("-- Arming")
            await drone.conn.action.arm()
            print("-- Taking off")
            await drone.conn.action.takeoff()
            # wait for takeoff
            await asyncio.sleep(1)

        print("-- Starting offboard")
        try:
            #await drone.conn.offboard.start()
            pass
        except Exception as error:
            print(f"Starting offboard mode failed with error code: {error._result.result}")
            print("-- Disarming")
            await drone.conn.action.disarm()
            return

        drone.state = State.Travel
        # To fly drone 20m above the ground plane
        flying_alt = absolute_altitude + self.altitude # default 20.0
        # goto_location() takes Absolute MSL altitude
        latitude_deg = self.position[0]
        longitude_deg = self.position[1]
        await drone.conn.action.goto_location(latitude_deg, longitude_deg, flying_alt, 0)
        print("GOTO", latitude_deg, longitude_deg, flying_alt)

        # while True:
        #     print("Staying connected, press Ctrl-C to exit")
        #     await asyncio.sleep(1)