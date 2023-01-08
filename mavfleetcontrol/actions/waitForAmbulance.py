import geopy.distance
import asyncio

class WaitForAmbulance:
    def __init__(self, ambulance):
        self.ambulance = ambulance

    def dist(self, a, b):
        return geopy.distance.geodesic((a.latitude_deg, a.longitude_deg), (b.latitude_deg, b.longitude_deg)).m

    async def __call__(self, drone, ambulance):
   
        while self.dist(drone.position, ambulance.position) > 5.0:
            await asyncio.sleep(0.2) # sleep for one second
        
