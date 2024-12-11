"""
IT IS UNCLEAR IF THIS CODE IS NECESSARY

the implementation plan of this is that we need a high enough velocity to pick up the obj
To do so, this file will get the perfect angle to be at the center of the object
it will then move a certain distance at a certain velocity (TBD) to pick up the ball
It will have a function that tests if the ball is in the frame
"""
import numpy as np
import detectObject
# this detector must detect only black
async def grabBall(colorDetector,pf,cam,base,dist,vel):
    base.moveStraight(dist,vel)
    detections = await colorDetector.get_detections_from_camera(cam)
    if detections:
        totalX,totalY,rangeX,rangeY = detectObject.findRange(detections)
        return inRange(pf,rangeX,rangeY)
    print("No black detections found, camera is not covered")
    return False
    

def readyToGrab(pf, rangeX, rangeY,prevXrange, prevYrange):
    print (f'PREV X: {prevXrange} PREV Y: {[prevYrange]}')
    print (f'CURR X: {rangeX} CURR Y: {[rangeY]}')
    if np.abs(prevXrange-rangeX) <30 and np.abs(prevYrange-rangeY)<30:
        return True
    return False
    

def inRange(pf, rangeX, rangeY):
    if rangeX == pf.size[0] or rangeY == pf.size[1]:
        return True
    return False

