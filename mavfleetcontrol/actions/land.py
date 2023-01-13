from MAVFleetControl.mavfleetcontrol.craft import State
from MAVFleetControl.mavfleetcontrol.craft import Craft
from mavsdk import System
import numpy as np
import asyncio

class land:
	async def __call__(self, drone):
		await drone.land()
		print("-- Land")
		drone.state = State.End # End drone state, stop background position tracking
