[![pypi version shield](https://img.shields.io/pypi/v/micropython-stepper)](https://pypi.org/project/micropython-stepper/) [![pypi downloads per month shield](https://img.shields.io/pypi/dm/micropython-stepper?color=brightgreen)](https://pypi.org/project/micropython-stepper/)
## Description
A micropython library to use stepper motors in a tidy way.

Your steppers should be connected to a stepper driver that is controlled using a step, a dir and optional an enable pin.

This library uses one timer per stepper to achive controlled speeds for multiple steppers in a non blocking way.

The steppers can be controlled by angle if the number of steps per rotation is supplied.

Multiple steppers can share a common dir pin, allowing for N steppers controlled by N+1 output pins.

## Examples
### Two steppers
```Python
from stepper import Stepper
import time

s1 = Stepper(18,19,steps_per_rev=200,speed_sps=50)
s2 = Stepper(20,21,steps_per_rev=200,speed_sps=50)

s1.target_deg(90)
s2.target_deg(45)
time.sleep(5.0)
s1.target_deg(0)
s2.target_deg(5)
time.sleep(5.0)
```

### Calibrate absolute position using an endswitch
```Python
import machine
import time
from stepper import Stepper

s1 = Stepper(18,19,steps_per_rev=200)
#create an input pin for the end switch (switch connects pin to GND)
endswitch = machine.Pin(2, machine.Pin.IN, machine.Pin.PULL_UP)

s1.speed(20) #use low speed for the calibration
s1.free_run(-1) #move backwards
while endswitch.value(): #wait till the switch is triggered
    pass
s1.stop() #stop as soon as the switch is triggered
s1.overwrite_pos(0) #set position as 0 point
s1.target(0) #set the target to the same value to avoid unwanted movement
s1.speed(100) #return to default speed
s1.track_target() #start stepper again

#calibration finished. Do something else below.
s1.target_deg(45)
time.sleep(5.0)
```

### Two steppers sharing a common dir pin
```Python
import machine
from stepper import Stepper

dir_pin = machine.Pin(19,machine.Pin.OUT)
s1 = Stepper(18,dir_pin,steps_per_rev=200,speed_sps=50)
s2 = Stepper(20,dir_pin,steps_per_rev=200,speed_sps=50)
```

## API
### class Stepper(step_pin,dir_pin,en_pin=None,steps_per_rev=200,speed_sps=10,invert_dir=False,timer_id=-1)
- step_pin: Pin id or machine.Pin object for the pin connected to the step input of the stepper driver
- dir_pin: Pin id or machine.Pin object for the pin connected to the direction select input of the stepper driver
- en_pin: (Optional) None or pin id or machine.Pin object for the pin connected to the enable input of the stepper driver
- steps_per_rev: Amount of stepper steps that would result in a 360° rotation
- speed_sps: Speed in steps per secound (= step frequency in Hz)
- invert_dir: True if the direction of the stepper should be inverted
- timer_id: Id of the timer that should be used. On most boards -1 will construct a new virtual timer (https://docs.micropython.org/en/latest/library/machine.Timer.html)


```speed(sps)```
- set the speed of the stepper
- sps: Speed in steps per secound (= step frequency in Hz)

```speed_rps(rps)```
- set the speed of the stepper
- rps: Speed in rotations per secound

```target(t)```
- set a target position. The stepper will move towards that position
- t: Target in steps

```target_deg(deg)```
- set a target position. The stepper will move towards that position
- deg: Target in degrees

```target_rad(rad)```
- set a target position. The stepper will move towards that position
- rad: Target in radians

```get_pos()```
- returns the current position in steps

```get_pos_deg()```
- returns the current position in degrees

```get_pos_rad()```
- returns the current position in radians

```overwrite_pos(p)```
- overwrites the current position. Used to calibrate the absolute position
- p: Current position in steps

```overwrite_pos_deg(deg)```
- overwrites the current position. Used to calibrate the absolute position
- deg: Current position in degree

```overwrite_pos_rad(rad)```
- overwrites the current position. Used to calibrate the absolute position
- rad: Current position in radians

```step(d)```
- instantly moves the stepper by a single step
- d: Direction of the step (d>0: Forwards, d<0: Backwards, d==0: No movement)

```free_run(d)```
- moves the stepper continuously until stopped
- d: Direction of movement (d>0: Forwards, d<0: Backwards, d==0: Stop)

```track_target()```
- puts the stepper back in the default mode, where it follows the target position after free_run(d) or stop() was used.

```stop()```
- stops the timer and all movement (single steps using the step() function are still possible)

```enable(e)```
- enable or disable the stepper driver using the enable pin. While this stops the movement of the actual hardware, the Stepper class will still act as if the stepper is moving. This can be used for testing. Recalibration of the absolute position might be needed if the stepper was disabled.
-e: True or False

```is_enabled()```
- returns the last status (True or False) of the enable(e) function
