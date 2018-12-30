#!/usr/bin/env python3

# Test for the robot controller. Moves the robot's head in all directions.

from time import sleep

from robot import Robot

print("Start")

robot = Robot()
robot.resetPosition()

# Waiting time, in seconds, between steps.
step_seconds = 0.2

# Angle increase/decrease per step.
step_deg = 2

while True:

  while not robot.deltaYaw(step_deg):
    sleep(step_seconds)

  sleep(step_seconds)
  robot.resetPosition()
  sleep(step_seconds)

  while not robot.deltaPitch(step_deg):
    sleep(step_seconds)

  sleep(step_seconds)
  robot.resetPosition()
  sleep(step_seconds)

  while not robot.deltaYaw(-step_deg):
    sleep(step_seconds)

  sleep(step_seconds)
  robot.resetPosition()
  sleep(step_seconds)

  while not robot.deltaPitch(-step_deg):
    sleep(step_seconds)

  sleep(step_seconds)
  robot.resetPosition()
  sleep(step_seconds)
