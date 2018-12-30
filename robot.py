# Controller for the robot.

from gpiozero import Servo

from aiy.pins import PIN_A
from aiy.pins import PIN_B


class Robot(object):
  def __init__(self):
    self._yaw_half_range = 90.0
    self._pitch_half_range = 90.0

    self._angular_margin = 0

    self._yaw = 0.0
    self._pitch = 0.0

    self._yaw_servo = Servo(PIN_A)
    self._pitch_servo = Servo(PIN_B)

  def disable(self):
    self._yaw_servo.value = None
    self._pitch_servo.value = None

  def enable(self):
    save_yaw = self._yaw
    save_pitch = self._pitch
    self._yaw = None
    self._pitch = None

    self.setYaw(save_yaw)
    self.setPitch(save_pitch)

  def resetPosition(self):
    self.setYaw(0.0)
    self.setPitch(0.0)

  def deltaLook(self, delta_yaw, delta_pitch):
    touch_yaw = self.deltaYaw(delta_yaw)
    touch_pitch = self.setPitch(delta_pitch)
    return touch_yaw or touch_pitch

  def deltaYaw(self, delta):
    return self.setYaw(self._yaw + delta)

  def deltaPitch(self, delta):
    return self.setPitch(self._pitch + delta)

  def setYaw(self, value):
    if self._yaw == value:
      return False
    self._yaw = value
    touch_side = False
    if self._yaw < -self._yaw_half_range + self._angular_margin:
      touch_side = True
      self._yaw = -self._yaw_half_range + self._angular_margin
    elif self._yaw > self._yaw_half_range - self._angular_margin:
      touch_side = True
      self._yaw = self._yaw_half_range - self._angular_margin
    raw_value = round(-self._yaw / self._yaw_half_range, 4)
    self._yaw_servo.value = raw_value
    return touch_side

  def setPitch(self, value):
    if self._pitch == value:
      return False
    self._pitch = value
    touch_side = False
    if self._pitch < -self._pitch_half_range + self._angular_margin:
      touch_side = True
      self._pitch = -self._pitch_half_range + self._angular_margin
    elif self._pitch > self._pitch_half_range - self._angular_margin:
      touch_side = True
      self._pitch = self._pitch_half_range - self._angular_margin
    raw_value = round(-self._pitch / self._pitch_half_range, 4)
    self._pitch_servo.value = raw_value
    return touch_side
