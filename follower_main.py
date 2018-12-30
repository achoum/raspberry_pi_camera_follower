#!/usr/bin/env python3

# Use the 2d direction controller to follow the face on front of the camera.
# The color of the butter is controller by the smile of the user.
#
# See README for more details.

from picamera import PiCamera
from time import sleep

from aiy.leds import Leds, Color
from aiy.pins import BUZZER_GPIO_PIN
from aiy.toneplayer import TonePlayer
from aiy.vision.annotator import Annotator
from aiy.vision.inference import CameraInference
from aiy.vision.models import face_detection
from robot import Robot

# If true, display the camera image.
ENABLE_DISPLAY = False

# field of view of the camera.
CAMERA_FOV_WIDTH = 62.2
CAMERA_FOV_HEIGHT = 48.8

# If true, print the statistics about all the detected faces.
PRINT_LOGS = False

# Resolution of the camera.
CAMERA_WIDTH = 1640
CAMERA_HEIGHT = 1232

# Waiting time, in seconds, in the main loop.
SLEEP = 0.01

# Minimum angular difference to trigger a motion.
ANGULAR_MARGIN = 5

# Music played when the program starts.
START_SOUND = ('C5q', 'E5q', 'C6q')
STOP_SOUND = ('C6q', 'E5q', 'C5q')


def selectFaceWithHigherScore(faces):
  """Selects the face with the higher score."""

  stronger_face = None
  stronger_face_score = 0
  for face in faces:
    if face.face_score > stronger_face_score:
      stronger_face_score = face.face_score
      stronger_face = face
  return stronger_face


def controller(measure):
  """Outputs the direction delta.

  Args:
      measure: (float) Measured angular difference, in degree.

  Returns:
      The control angular difference i.e. the motion to apply, in degree.
  """

  return controller_v2(measure)


def controller_v1(measure, angular_step=3):
  if measure > ANGULAR_MARGIN:
    return angular_step
  elif measure < - ANGULAR_MARGIN:
    return -angular_step
  else:
    return 0.


def controller_v2(measure):
  if abs(measure) > ANGULAR_MARGIN:
    return min(measure / 2, 20)
  else:
    return 0.


def transform_annotator(bounding_box):
  scale_x = 320 / CAMERA_WIDTH
  scale_y = 240 / CAMERA_HEIGHT
  x, y, width, height = bounding_box
  return (scale_x * x, scale_y * y, scale_x * (x + width),
          scale_y * (y + height))


def loop(inference, robot, annotator, leds):
  for inference_result in inference.run(None):

    # Get all the faces.
    faces = face_detection.get_faces(inference_result)

    # Get the stronger face.
    stronger_face = selectFaceWithHigherScore(faces);

    if stronger_face is None:
      print("No face detected")
      continue

    # Angular difference between the face and the center of the camera.
    face_x_center = stronger_face.bounding_box[0] + stronger_face.bounding_box[2] / 2
    face_y_center = stronger_face.bounding_box[1] + stronger_face.bounding_box[3] / 2

    face_x_normalized = face_x_center / CAMERA_WIDTH
    face_y_normalized = face_y_center / CAMERA_HEIGHT

    face_x_angle = (face_x_normalized * 2 - 1) * (CAMERA_FOV_WIDTH / 2)
    # The screen and motor axis are reversed.
    face_y_angle = - (face_y_normalized * 2 - 1) * (CAMERA_FOV_HEIGHT / 2)

    print("Face delta: %s %s" % (face_x_angle, face_y_angle))
    robot.deltaYaw(controller(face_x_angle))
    robot.deltaPitch(controller(face_y_angle))

    leds.update(
      Leds.rgb_on((255 * (1 - stronger_face.joy_score), 255 * stronger_face.joy_score, 0)))

    if SLEEP > 0:
      sleep(SLEEP)

    if PRINT_LOGS:
      for face_idx, face in enumerate(faces):
        print("Face %i -> %s" % (face_idx, face))

    if ENABLE_DISPLAY:
      annotator.clear()
      for face in faces:
        annotator.bounding_box(transform_annotator(face.bounding_box), fill=0)
      annotator.update()


def main():
  print("Play tune")
  player = TonePlayer(gpio=BUZZER_GPIO_PIN, bpm=10)
  player.play(*START_SOUND)

  print("Initialize robot")
  robot = Robot()
  robot.resetPosition()

  print("Switch on leds")
  with Leds() as leds:
    leds.update(Leds.rgb_on(Color.GREEN))

    print("Switch on camera")
    with PiCamera(sensor_mode=4, resolution=(CAMERA_WIDTH, CAMERA_HEIGHT), framerate=30) as camera:

      if ENABLE_DISPLAY:
        camera.start_preview()
        annotator = Annotator(camera, dimensions=(320, 240))
      else:
        annotator = None

      print("Load model")
      with CameraInference(face_detection.model()) as inference:

        loop(inference=inference, robot=robot, annotator=annotator, leds=leds)

      if ENABLE_DISPLAY:
        camera.stop_preview()

  player.play(*STOP_SOUND)

  # Give time for the user to remote its finger.
  sleep(3)
  robot.resetPosition()


if __name__ == '__main__':
  print("Start")
  main()
