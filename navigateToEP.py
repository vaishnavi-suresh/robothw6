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

# main2.py
import asyncio
from viam.components.base import Base
from viam.components.base import Vector3
from viam.robot.client import RobotClient
from viam.rpc.dial import Credentials, DialOptions
from viam.services.slam import SLAMClient
from viam.services.motion import MotionClient
import numpy as np


def getDist (currX, currY, wantX, wantY):
    return np.sqrt((wantX-currX)**2+(wantY-currY)**2)

async def computeAng(slam, target_angle):
    currPos = await slam.get_position()
    currTheta = currPos.theta
    toMove = (target_angle - currTheta + 180) % 360 -180 
    return toMove
    
async def moveAngle(base,slam,target_angle):
    toMove = await computeAng(slam,target_angle)
    while np.abs(toMove)>1:
        toMove = await computeAng(slam,target_angle)
        await base.spin(toMove/2, 45)

async def moveToPos(base, slam, x,y,theta):
    print("move to point call")
    currPos = await slam.get_position()
    currX = currPos.x
    currY = currPos.y
    currTheta = currPos.theta
    print (f'x={currX}')
    print (f'y={currY}')
    print (f'theta={currTheta}')
    print (f'want x={x}')
    print (f'want y={y}')
    target_angle_rad = np.arctan2(y - currY, x - currX)
    target_angle = np.degrees(target_angle_rad)
    print(f'moving to angle: {target_angle}')
    while getDist(currX,currY,x,y)>83:
        currPos = await slam.get_position()
        currX = currPos.x
        currY = currPos.y
        await moveAngle(base,slam,target_angle)
        await base.move_straight(30,400)

