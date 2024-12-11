import asyncio
from viam.components.base import Base
from viam.robot.client import RobotClient
from viam.rpc.dial import Credentials, DialOptions
from viam.services.slam import SLAMClient
from viam.components.base import Vector3
import numpy as np
from viam.robot.client import RobotClient
from viam.rpc.dial import Credentials, DialOptions
from viam.components.board import Board
from viam.components.motor import Motor
from viam.components.base import Base
from viam.components.camera import Camera
from viam.components.encoder import Encoder
from viam.services.vision import VisionClient
from viam.media.utils.pil import pil_to_viam_image, viam_to_pil_image
import threading
import detectObject as DO
import grabObj as GO
import navigateToEP as EP

async def connect():
    opts = RobotClient.Options.with_api_key(
        api_key='i11ph4btwvdp1kixh3oveex92tmvdtx2',
        api_key_id='8b19e462-949d-4cf3-9f7a-5ce0854eb7b8'
    )
    return await RobotClient.at_address('rover6-main.9883cqmu1w.viam.cloud', opts)

async def findObject(pil_frame, my_detector,base,camera_name):
        detections = await DO.getDetections(my_detector,camera_name,base,100)
        x,y,Xrange,Yrange =  DO.findRange(detections)
        prevXrange=0
        prevYrange = 0
        while GO.readyToGrab(pil_frame,Xrange,Yrange, prevXrange, prevYrange)==False:
            await DO.motion(pil_frame,my_detector,camera_name, base, 150,15, 500, pil_frame.size[0]/2)
            asyncio.sleep(2)
            prevXrange, prevYrange =Xrange,Yrange
            detections = await DO.getDetections(my_detector,camera_name,base,10)
            x,y,Xrange,Yrange =  DO.findRange(detections)
        return Xrange,Yrange

async def main():
    machine = await connect()
    camera_name = "cam"
    camera = Camera.from_robot(machine, camera_name)
    base = Base.from_robot(machine, "viam_base")
    my_detector = VisionClient.from_robot(machine, "color_detector")
    slam = SLAMClient.from_robot(machine, 'slam-2')
    frame = await camera.get_image(mime_type="image/jpeg")
    pil_frame = viam_to_pil_image(frame)
    currPos = await slam.get_position()
    #TO DO: change the endpoint so that it doesn't go back
    EPx = currPos.x
    EPy = currPos.y
    await base.set_power(
    linear=Vector3(x=0, y=0.5, z=0),
    angular=Vector3(x=0, y=0, z=0.75))

    
    

    detections = await DO.getDetections(my_detector,camera_name,base,10)
    x,y,Xrange,Yrange =  DO.findRange(detections)
    Xrange,Yrange = await findObject(pil_frame, my_detector,base,camera_name)
    #When the loop breaks, the object is positioned correctly to pick up. The next step is to actually pick it up, which can be done by moving forward
    base.move_straight(300,200) #play with velocity and distance to get optimal mix
    """if GO.inRange(pil_frame,Xrange,Yrange)==False:
        Xrange,Yrange = await findObject(pil_frame, my_detector,base,camera_name)"""
    #Navigate to endpoints
    await base.set_power(
    linear=Vector3(x=0, y=0.5, z=0),
    angular=Vector3(x=0, y=0, z=0.25))
    await EP.moveToPos(base,slam,EPx,EPy)
    await GO.dropobject(base)














if __name__ == '__main__':
    asyncio.run(main())
