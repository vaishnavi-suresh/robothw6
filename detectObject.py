import asyncio
from viam.robot.client import RobotClient
from viam.rpc.dial import Credentials, DialOptions
from viam.components.board import Board
from viam.components.motor import Motor
from viam.components.base import Base
from viam.components.camera import Camera
from viam.components.encoder import Encoder
from viam.components.movement_sensor import MovementSensor
from viam.services.vision import VisionClient
from viam.media.utils.pil import pil_to_viam_image, viam_to_pil_image
import threading
import time


async def getDetections(colorDetector, cam, base, vel):
    detections = await colorDetector.get_detections_from_camera(cam)
    if not detections:
        for i in range(40):
            await base.spin(18, vel)
            detections = await colorDetector.get_detections_from_camera(cam)
            await asyncio.sleep(2) # added delay for camera
            if detections:
                break
    return detections if detections else None

def findRange(detections):
    totalX = 0
    totalY = 0
    rangeX = 0
    rangeY = 0
    xmax = detections[0].x_max
    xmin = detections[0].x_min
    ymax = detections[0].y_max
    ymin = detections[0].y_min
    for detection in detections:
        if detection.x_max>xmax:
            xmax = detection.x_max
        if detection.y_max>ymax:
            ymax = detection.y_max
        if detection.x_min<xmin:
            xmin = detection.x_min
        if detection.y_min<ymin:
            ymin = detection.y_min
        totalX += (detection.x_max-detection.x_min)/2+detection.x_min
        totalY += (detection.y_max-detection.y_min)/2+detection.y_min
    rangeX = xmax - xmin
    rangeY = ymax -ymin
    totalX *= (1/len(detections))
    totalY *=(1/len(detections))
    return totalX, totalY, rangeX, rangeY

async def leftOrRight(totalX,midpoint):
    if midpoint - midpoint/6 < totalX<midpoint+midpoint/6:
        return 0
    if totalX <midpoint-midpoint/6:
        return 1
    if totalX>midpoint+midpoint/6:
        return -1
    else:
        return None

async def detectDistance(pf, rangeX, rangeY):
    if rangeX > pf.size[0] or rangeY > pf.size[1]:
        return 1
    return 0
    

async def motion(pf,myDetector,myCam, base, dist,spinnum, vel, mp):
    while True:
        detections = await getDetections(myDetector, myCam, base, 10)
        totalX,totalY,rangeX,rangeY = findRange(detections)
        LorR = await leftOrRight(totalX, mp)
        if LorR ==0:
            await base.move_straight(dist,vel)
        elif LorR ==-1:
            await base.spin(-spinnum,vel)
            await base.move_straight(dist,vel)
        elif LorR ==1:
            await base.spin(spinnum,vel)
            await base.move_straight(dist,vel)
        
        await asyncio.sleep(0.1) 
        status = await detectDistance(pf,rangeX,rangeY)
        if status ==1:
            asyncio.get_event_loop().stop()
            break

"""

async def main():
    machine = await connect()
    camera_name = "cam"
    camera = Camera.from_robot(machine, camera_name)
    base = Base.from_robot(machine, "viam_base")
    my_detector = VisionClient.from_robot(machine, "color_detector")
    frame = await camera.get_image(mime_type="image/jpeg")
    pil_frame = viam_to_pil_image(frame)


    
    asyncio.create_task(motion(pil_frame,my_detector,camera_name, base, 150,15, 500, pil_frame.size[0]/2))  # Adjust parameters as needed
    print("Motion task started. Press Enter to quit.")
    await asyncio.get_event_loop().run_in_executor(None, input, "")

        


    await machine.close()

if __name__ == '__main__':
    asyncio.run(main())"""