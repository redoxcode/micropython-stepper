import machine
import math
import uasyncio as asyncio

class Stepper:
    def __init__(self,step_pin,dir_pin,en_pin=None,steps_per_rev=200,speed_sps=10,invert_dir=False,timer_id=-1, get_pos_from_encoder=None):
        """
        Params:
            get_pos_from_encoder: 
                - It's a function provided by the encoder, this function must return the current position in steps.
                - In the case of the AS5600 encoder, it has a resolution of 4096 steps per revolution and a NEMA17 motor can be 
                configured to 3200 steps per rev, so get_pos_from_encoder() function must map ththe AS5600 resolution to the current
                step motor resolution.
                - In this link I have an example of a encoder library: https://gitlab.com/chaliuz_public/as5600#
        """
        
        if not isinstance(step_pin, machine.Pin):
            step_pin=machine.Pin(step_pin,machine.Pin.OUT)
        if not isinstance(dir_pin, machine.Pin):
            dir_pin=machine.Pin(dir_pin,machine.Pin.OUT)
        if (en_pin != None) and (not isinstance(en_pin, machine.Pin)):
            en_pin=machine.Pin(en_pin,machine.Pin.OUT)
                 
        self.step_value_func = step_pin.value
        self.dir_value_func = dir_pin.value
        self.en_pin = en_pin
        self.invert_dir = invert_dir

        self.timer = machine.Timer(timer_id)
        self.timer_is_running=False
        self.free_run_mode=0
        self.enabled=True
        
        self.steps_per_sec = speed_sps
        self.steps_per_rev = steps_per_rev

        if get_pos_from_encoder == None:
            """
            If the motor isn't using a encoder
            """
            self.pos = 0
            self.target_pos = 0
        else: 
            self.get_pos_from_encoder = get_pos_from_encoder
            steps = self.get_pos_from_encoder()

            if steps is not None:
                self.pos = steps
                self.target_pos = self.pos
            else:
                self.pos = 0
                self.target_pos = 0

        
        self.track_target()
        
    def speed(self,sps):
        self.steps_per_sec = sps
        if self.timer_is_running:
            self.track_target()
    
    def speed_rps(self,rps):
        self.speed(rps*self.steps_per_rev)

    def target(self,steps):
        self.target_pos = steps

    def target_deg(self,deg):
        steps = int(self.steps_per_rev*deg/360.0)
        self.target(steps)
    
    def target_rad(self,rad):
        self.target(self.steps_per_rev*rad/(2.0*math.pi))
    
    def get_pos(self):
        return self.pos
    
    def get_pos_deg(self):
        return self.get_pos()*360.0/self.steps_per_rev
    
    def get_pos_rad(self):
        return self.get_pos()*(2.0*math.pi)/self.steps_per_rev
    
    def overwrite_pos(self,p):
        self.pos = p
    
    def overwrite_pos_deg(self,deg):
        self.overwrite_pos(deg*self.steps_per_rev/360.0)
    
    def overwrite_pos_rad(self,rad):
        self.overwrite_pos(rad*self.steps_per_rev/(2.0*math.pi))

    def step(self,d):
        if d>0:
            if self.enabled:
                self.dir_value_func(1^self.invert_dir)
                self.step_value_func(1)
                self.step_value_func(0)

            steps = self.get_pos_from_encoder()
            if steps is not None:
                self.pos = steps # it converts the current stepmotor steps
            else:
                self.pos+=1
        elif d<0:
            if self.enabled:
                self.dir_value_func(0^self.invert_dir)
                self.step_value_func(1)
                self.step_value_func(0)

            steps = self.get_pos_from_encoder()
            if steps is not None:
                self.pos = steps
            else:
                self.pos-=1

    def _timer_callback(self,t):
        # print(f"self.target_pos: {self.target_pos} | self.pos: {self.pos}") 
        if self.free_run_mode>0:
            self.step(1)
        elif self.free_run_mode<0:
            self.step(-1)
        elif self.target_pos>self.pos:
            self.step(1)
        elif self.target_pos<self.pos:
            self.step(-1)
    
    def free_run(self,d):
        self.free_run_mode=d
        if self.timer_is_running:
            self.timer.deinit()
        if d!=0:
            self.timer.init(freq=self.steps_per_sec,callback=self._timer_callback)
            self.timer_is_running=True
        else:
            self.dir_value_func(0)

    def track_target(self):
        self.free_run_mode=0
        if self.timer_is_running:
            self.timer.deinit()
        self.timer.init(freq=self.steps_per_sec,callback=self._timer_callback)
        self.timer_is_running=True

    def stop(self):
        self.free_run_mode=0
        if self.timer_is_running:
            self.timer.deinit()
        self.timer_is_running=False
        self.dir_value_func(0)

    def enable(self,e):
        if self.en_pin:
            self.en_pin.value(e)
        self.enabled=e
        if not e:
            self.dir_value_func(0)
    
    def is_enabled(self):
        return self.enabled
