import asyncio
from mavsdk import System


class GoTo:
    def __init__(self, position, altitude=12.0):
        self.position = position
        self.altitude = altitude

    async def __call__(self, drone):
      
        print("-- Fetching amsl altitude at home location....") # asml: above mean sea level
        async for terrain_info in drone.telemetry.home():
            absolute_altitude = terrain_info.absolute_altitude_m
            break
        
        # if drone is not flying
        if not drone.telemetry.in_air():
            print("-- Arming")
            await drone.action.arm()
            print("-- Taking off")
            await drone.action.takeoff()
            # wait for takeoff
            await asyncio.sleep(1)

        # To fly drone 20m above the ground plane
        flying_alt = absolute_altitude + self.altitude # default 20.0
        # goto_location() takes Absolute MSL altitude
        latitude_deg = self.position[0]
        longitude_deg = self.position[1]
        await drone.action.goto_location(latitude_deg, longitude_deg, flying_alt, 0)

        # while True:
        #     print("Staying connected, press Ctrl-C to exit")
        #     await asyncio.sleep(1)
