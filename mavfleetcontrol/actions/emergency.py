
class Emergency:

    def __init__(self):
        self.test = None
    
    async def __call__(self, drone):
        print("[INFO] Emergency plan is being communicated to drone")
        # find the rally points that is closed to the the drone
        print("-- evacuating")
        lat = 55.381227831425505
        lng = 10.364954425301825
        alt = 20.0
        
        await drone.action.goto_location(lat, lng, alt, 0)
        print("-- reached site")
        await drone.land()
        print("-- Land")