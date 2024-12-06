import numpy as np

async def main():
    robot = await connect()
    base = Base.from_robot(robot, 'viam_base')
    slam = SLAMClient.from_robot(robot, 'slam-2')


if __name__ == '__main__':
    asyncio.run(main())
    