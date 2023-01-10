"""
Bla
"""
from enum import Enum
from typing import Callable, Awaitable, List
import threading
import functools
import queue
import asyncio
import random

# State of the drone
class State(Enum):
	Start = 1 #Startup sequence
	Follow = 2
	FollowMission = 3
	Travel = 4 #Normal travel
	TravelWait = 5 #Is decending to waypoint
	Wait = 6 #Is at a waypoint
	End = 7 #At the end

from mavsdk import System
from mavsdk.offboard import Attitude, PositionNedYaw, OffboardError
from mavsdk.telemetry import PositionNed
import numpy as np
from MAVFleetControl.mavfleetcontrol.states.position import Position

class Craft(threading.Thread):
    def __init__(
        self,
        id: int,
        connection_address: str,
        mission_id = None,
        action: Callable[["Craft"], Awaitable[None]] = None,
    ):
        super().__init__()
        self.id: str = id
        self.mission_id = mission_id
        self.state = State.Start
        self.conn: System = None
        self.address: str = connection_address
        self.action: Callable[["Craft"], Awaitable[None]] = action
        self.loop = asyncio.new_event_loop()
        self.tasking = queue.Queue()
        self.current_task = None
        self.current_task_lock = threading.Lock()
        self.sensors = []
        self.armed = False
        self.position = None
        self.ambulance_position = None

    def run(self):
        # self.loop = asyncio.new_event_loop()
        # print("run loo[")
        try:
            self.loop.run_until_complete(self.connect())
            while True:
                action = self.tasking.get()
                print("ACTION: ", action)
                if isinstance(action, str) and action == "exit":
                    print("[INFO] exiting...")
                    break
                # self.loop.run_until_complete(action(self))
                with self.current_task_lock:
                    self.current_task = self.loop.create_task(action(self))
                try:
                    self.loop.run_until_complete(self.current_task)
                except asyncio.CancelledError:
                    print("[INFO] Asyncio Error")
                    pass

                # clear the tasked sensors     
                for task in self.sensors:
                    task.cancel()
                self.sensors = []

                with self.current_task_lock:
                    self.current_task = None
                # Blocking call will continously try and get a task
                # if no tasks, aircraft will default to pix4 default maybe?

        finally:
            print("[INFO] finally...")
            self.loop.run_until_complete(self.loop.shutdown_asyncgens())
            self.loop.call_soon_threadsafe(self.loop.stop)
            #self.loop.close()

    def add_action(self, action):
        self.tasking.put(action)
        # asyncio.run_coroutine_threadsafe(action(self),self.loop)
        # self.loop.call_soon_threadsafe(action,self)

    def close_conn(self, action):
        print("[INFO] Closing connection")
        with self.current_task_lock:
            self.tasking.queue.clear()
            # maybe add check to see if safe
            self.tasking.put(action)

            if self.current_task is not None:
                self.current_task.cancel()

    def close_conn(self):
        print("[INFO] Closing connection")
        self.tasking.put("exit")
        # self.loop.stop()

    async def arm(self, coordinate: List[float] = None, attitude: List[float] = None):
        async for arm in self.conn.telemetry.armed():
            if arm is False:
                try:
                    print(f"{self.name}: arming")
                    await self.conn.action.arm()
                    print(f"{self.name}: Setting initial setpoint")
                    if coordinate is not None:
                        await self.conn.offboard.set_position_ned(
                            PositionNedYaw(*coordinate, 0.0)
                        )
                    if attitude is not None:
                        await self.conn.offboard.set_attitude(Attitude(*attitude, 0.0))

                except Exception as bla:  # add exception later
                    print(bla)
                break
            else:
                break

    async def disarm(self):
        async for arm in self.conn.telemetry.armed():
            if arm is True:
                try:
                    print(f"{self.name}: Disarming")
                    await self.conn.action.disarm()
                    
                except Exception as bla:  # add exception later
                    print(bla)
                break
            else:
                break

    async def land(self):
        await self.conn.action.land()
        print("-- Landing in process")


    async def land_and_close_conn(self):
        await self.conn.action.land()

                   
    async def kill(self):
        async for arm in self.conn.telemetry.armed():
            if arm is True:
                try:
                    print(f"{self.name}: Killing")
                    await self.conn.action.kill()
                    
                except Exception as bla:  # add exception later
                    print(bla)
                break
            else:
                break   

    async def start_offboard(self):
             # print("-- Starting offboard")
        try:
            await self.conn.offboard.start()
            return True
        except OffboardError as error:
            # print(
                # f"Starting offboard mode failed with error code: {error._result.result}"
            # )
            # print("-- Disarming")
            await self.conn.action.disarm()
            return False

    async def connect(self):
        self.conn = System(port=random.randint(1000, 65535))

        print(f"{self.name}: connecting")
        await self.conn.connect(system_address=self.address)

        print(f"{self.name}: waiting for connection")
        async for state in self.conn.core.connection_state():
            print(f"{self.name}: {state}")
            if state.is_connected:
                print(f"{self.name}: connected!")
                break

    async def print_status_text(drone):
        try:
            async for status_text in drone.telemetry.status_text():
                print(f"Status: {status_text.type}: {status_text.text}")
        except asyncio.CancelledError:
            return


    @property
    async def current_position(self) -> PositionNed:
        async for position_ned in self.conn.telemetry.position_velocity_ned():
            return np.array(
                [
                    position_ned.position.north_m,
                    position_ned.position.east_m,
                    position_ned.position.down_m,
                ]
            )

    async def register_sensor(self,name:str,waitable:Awaitable):
        async def _sensor():
            async for x in waitable:
                setattr(self,name,x)
        setattr(self,name,None)
        self.sensors.append(asyncio.ensure_future(_sensor(),loop = self.loop))
