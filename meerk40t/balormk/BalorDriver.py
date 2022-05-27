import time

from meerk40t.balor.command_list import CommandList, Wobble
from meerk40t.balor.sender import BalorMachineException, Sender
from meerk40t.core.cutcode import LineCut, QuadCut, CubicCut, PlotCut
from meerk40t.core.drivers import PLOT_FINISH, PLOT_JOG, PLOT_RAPID, PLOT_SETTING
from meerk40t.core.plotplanner import PlotPlanner


class BalorDriver:
    def __init__(self, service):
        self.service = service
        self.native_x = 0x8000
        self.native_y = 0x8000
        self.name = str(self.service)
        self.channel = self.service.channel("balor")
        self.connection = Sender(debug=self.channel)
        self.paused = False

        self.connected = False

        self.is_relative = False
        self.laser = False

        self._shutdown = False

        self.redlight_preferred = False

        self.queue = list()
        self.plot_planner = PlotPlanner(
            dict(), single=True, smooth=False, ppi=False, shift=False, group=True
        )
        self.wobble = None
        self.value_penbox = None
        self.plot_planner.settings_then_jog = True

    def __repr__(self):
        return "BalorDriver(%s)" % self.name

    def service_attach(self):
        self._shutdown = False

    def service_detach(self):
        self._shutdown = True

    def connect_if_needed(self):
        if not self.connected:
            self.connect()

    def connect(self):
        """
        Connect to the Balor Sender

        @return:
        """
        self.connected = False
        while not self.connected:
            try:
                self.connected = self.connection.open(
                    mock=self.service.mock,
                    machine_index=self.service.machine_index,
                    cor_file=self.service.corfile
                    if self.service.corfile_enabled
                    else None,
                    first_pulse_killer=self.service.first_pulse_killer,
                    pwm_pulse_width=self.service.pwm_pulse_width,
                    pwm_half_period=self.service.pwm_half_period,
                    standby_param_1=self.service.standby_param_1,
                    standby_param_2=self.service.standby_param_2,
                    timing_mode=self.service.timing_mode,
                    delay_mode=self.service.delay_mode,
                    laser_mode=self.service.laser_mode,
                    control_mode=self.service.control_mode,
                    fpk2_p1=self.service.fpk2_p1,
                    fpk2_p2=self.service.fpk2_p2,
                    fpk2_p3=self.service.fpk2_p3,
                    fpk2_p4=self.service.fpk2_p3,
                    fly_res_p1=self.service.fly_res_p1,
                    fly_res_p2=self.service.fly_res_p2,
                    fly_res_p3=self.service.fly_res_p3,
                    fly_res_p4=self.service.fly_res_p4,
                )
                if self.redlight_preferred:
                    self.connection.light_on()
                else:
                    self.connection.light_off()
            except BalorMachineException as e:
                self.service.signal("pipe;usb_status", str(e))
                self.channel(str(e))
                return
            if not self.connected:
                self.service.signal("pipe;usb_status", "Connecting...")
                if self._shutdown:
                    self.service.signal("pipe;usb_status", "Failed to connect")
                    return
                time.sleep(1)
        self.connected = True
        self.service.signal("pipe;usb_status", "Connected")

    def disconnect(self):
        self.connection.close()
        self.connected = False
        self.service.signal("pipe;usb_status", "Disconnected")

    def hold_work(self):
        """
        This is checked by the spooler to see if we should hold any work from being processed from the work queue.

        For example if we pause, we don't want it trying to call some functions. Only priority jobs will execute if
        we hold the work queue. This is so that "resume" commands can be processed.

        @return:
        """
        return self.paused

    def hold_idle(self):
        """
        This is checked by the spooler to see if we should abort checking if there's any idle job after the work queue
        was found to be empty.
        @return:
        """
        return False

    def balor_job(self, job):
        self.connect_if_needed()
        self.connection.execute(job, 1)
        if self.redlight_preferred:
            self.connection.light_on()
        else:
            self.connection.light_off()

    def laser_off(self, *values):
        """
        This command expects to stop pulsing the laser in place.

        @param values:
        @return:
        """
        self.laser = False

    def laser_on(self, *values):
        """
        This command expects to start pulsing the laser in place.

        @param values:
        @return:
        """
        self.laser = True

    def plot(self, plot):
        """
        This command is called with bits of cutcode as they are processed through the spooler. This should be optimized
        bits of cutcode data with settings on them from paths etc.

        @param plot:
        @return:
        """
        self.queue.append(plot)

    def light(self, job):
        """
        This is not a typical meerk40t command. But, the light commands in the main balor add this as the idle job.

        self.spooler.set_idle(("light", self.driver.cutcode_to_light_job(cutcode)))
        That will the spooler's idle job be calling "light" on the driver with the light job. Which is a BalorJob.Job class
        We serialize that and hand it to the send_data routine of the connection.

        @param job:
        @return:
        """
        self.connect_if_needed()
        self.connection.light_off()
        self.connection.execute(job, 1)
        if self.redlight_preferred:
            self.connection.light_on()
        else:
            self.connection.light_off()

    def _set_settings(self, job, settings):
        """
        Sets the primary settings. Rapid, frequency, speed, and timings.

        @param job: The job to set these settings on
        @param settings: The current settings dictionary
        @return:
        """
        if (
                str(settings.get("rapid_enabled", False)).lower() == "true"
        ):
            job.set_travel_speed(float(settings.get(
                "rapid_speed", self.service.default_rapid_speed
            )))
        else:
            job.set_travel_speed(self.service.default_rapid_speed)
        job.set_power((
                float(settings.get("power", self.service.default_power)) / 10.0
        ))  # Convert power, out of 1000
        job.set_frequency(float(settings.get(
            "frequency", self.service.default_frequency
        )))
        job.set_cut_speed(float(settings.get("speed", self.service.default_speed)))

        if (
                str(settings.get("timing_enabled", False)).lower() == "true"
        ):
            job.set_laser_on_delay(settings.get(
                "delay_laser_on", self.service.delay_laser_on
            ))
            job.set_laser_off_delay(settings.get(
                "delay_laser_off", self.service.delay_laser_off
            ))
            job.set_polygon_delay(settings.get(
                "delay_laser_polygon", self.service.delay_polygon
            ))
        else:
            # Use globals
            job.set_laser_on_delay(self.service.delay_laser_on)
            job.set_laser_off_delay(self.service.delay_laser_off)
            job.set_polygon_delay(self.service.delay_polygon)

    def _set_wobble(self, job, settings):
        """
        Set the wobble parameters and mark modifications routines.

        @param job: The job to set these wobble parameters on.
        @param settings: The dict setting to extract parameters from.
        @return:
        """
        wobble_enabled = (
                str(settings.get("wobble_enabled", False)).lower() == "true"
        )
        if wobble_enabled:
            wobble_radius = settings.get("wobble_radius", "1.5mm")
            wobble_r = self.service.physical_to_device_length(
                wobble_radius, 0
            )[0]
            wobble_interval = settings.get("wobble_interval", "0.3mm")
            wobble_speed = settings.get("wobble_speed", 50.0)
            wobble_type = settings.get("wobble_type", "circle")
            wobble_interval = self.service.physical_to_device_length(
                wobble_interval, 0
            )[0]
            if self.wobble is None:
                self.wobble = Wobble(
                    radius=wobble_r,
                    speed=wobble_speed,
                    interval=wobble_interval,
                )
            else:
                # set our parameterizations
                self.wobble.radius = wobble_r
                self.wobble.speed = wobble_speed
            if wobble_type == "circle":
                job._mark_modification = self.wobble.circle
            elif wobble_type == "sinewave":
                job._mark_modification = self.wobble.sinewave
            elif wobble_type == "sawtooth":
                job._mark_modification = self.wobble.sawtooth
            elif wobble_type == "jigsaw":
                job._mark_modification = self.wobble.jigsaw
            elif wobble_type == "gear":
                job._mark_modification = self.wobble.gear
            elif wobble_type == "slowtooth":
                job._mark_modification = self.wobble.slowtooth
            else:
                raise ValueError
        else:
            job._mark_modification = None
            job._interpolations = None

    def plot_start(self):
        """
        This is called after all the cutcode objects are sent. This says it shouldn't expect more cutcode for a bit.

        @return:
        """
        self.connect_if_needed()
        job = CommandList()
        job.ready()
        # marked = False
        job.raw_mark_end_delay(0x0320)
        job.set_write_port(self.connection.get_port())
        job.set_travel_speed(self.service.default_rapid_speed)
        job.goto(0x8000, 0x8000)
        last_on = None
        self.wobble = None
        for q in self.queue:
            settings = q.settings
            penbox = settings.get("penbox_value")
            if penbox is not None:
                try:
                    self.value_penbox = self.service.elements.penbox[penbox]
                except KeyError:
                    self.value_penbox = None
            self._set_settings(job, settings)
            self._set_wobble(job, settings)

            if isinstance(q, LineCut):
                last_x, last_y = job.get_last_xy()
                x, y = q.start
                if last_x != x and last_y != y:
                    job.goto(x, y)
                job.mark(*q.end)
            elif isinstance(q, (QuadCut, CubicCut)):
                last_x, last_y = job.get_last_xy()
                x, y = q.start
                if last_x != x and last_y != y:
                    job.goto(x, y)
                interp = self.service.interpolate
                step_size = 1.0 / float(interp)
                t = 0
                for p in range(int(interp)):
                    while self.hold_work():
                        time.sleep(0.05)
                    p = q.point(t)
                    job.mark(*p)
                    t += step_size
            elif isinstance(q, PlotCut):
                last_x, last_y = job.get_last_xy()
                x, y = q.start
                if last_x != x and last_y != y:
                    job.goto(x, y)
                for x, y, on in q.plot:
                    # q.plot can have different on values, these are parsed
                    if last_on is None or on != last_on:
                        last_on = on
                        if self.value_penbox:
                            # There is an active value_penbox
                            settings = dict(q.settings)
                            limit = len(self.value_penbox) - 1
                            m = int(round(on * limit))
                            try:
                                pen = self.value_penbox[m]
                                settings.update(pen)
                            except IndexError:
                                pass
                            # Power scaling is exclusive to this penbox. on is used as a lookup and does not scale power.
                            self._set_settings(job, settings)
                        else:
                            # We are using traditional power-scaling
                            settings = self.plot_planner.settings
                            current_power = (
                                    float(settings.get("power", self.service.default_power)) / 10.0
                            )
                            job.set_power(current_power * on)
                    job.mark(x, y)
            else:
                self.plot_planner.push(q)
                for x, y, on in self.plot_planner.gen():
                    while self.hold_work():
                        time.sleep(0.05)
                    if on > 1:
                        # Special Command.
                        if on & PLOT_FINISH:  # Plot planner is ending.
                            break
                        elif on & PLOT_SETTING:  # Plot planner settings have changed.
                            settings = self.plot_planner.settings
                            penbox = settings.get("penbox_value")
                            if penbox is not None:
                                try:
                                    self.value_penbox = self.service.elements.penbox[penbox]
                                except KeyError:
                                    self.value_penbox = None
                            self._set_settings(job, settings)
                            self._set_wobble(job, settings)
                        elif on & (
                                PLOT_RAPID | PLOT_JOG
                        ):  # Plot planner requests position change.
                            # job.laser_off(int(self.service.delay_end / 10.0))
                            job.set_travel_speed(self.service.default_rapid_speed)
                            job.goto(x, y)
                        continue
                    if on == 0:
                        # job.laser_off(int(self.service.delay_end / 10.0))
                        job.set_travel_speed(self.service.default_rapid_speed)
                        job.goto(x, y)
                    else:
                        # on is in range 0 exclusive and 1 inclusive.
                        # This is a regular cut position
                        if last_on is None or on != last_on:
                            last_on = on
                            if self.value_penbox:
                                # There is an active value_penbox
                                settings = dict(self.plot_planner.settings)
                                limit = len(self.value_penbox) - 1
                                m = int(round(on * limit))
                                try:
                                    pen = self.value_penbox[m]
                                    settings.update(pen)
                                except IndexError:
                                    pass
                                # Power scaling is exclusive to this penbox. on is used as a lookup and does not scale power.
                                self._set_settings(job, settings)
                            else:
                                # We are using traditional power-scaling
                                settings = self.plot_planner.settings
                                current_power = (
                                        float(settings.get("power", self.service.default_power)) / 10.0
                                )
                                job.set_power(current_power * on)
                        # job.laser_on()
                        job.mark(x, y)
                        marked = True
        # job.laser_off(int(self.service.delay_end / 10.0))
        job.flush()
        self.connection.execute(job, 1)
        if self.redlight_preferred:
            self.connection.light_on()
        else:
            self.connection.light_off()

    def move_abs(self, x, y):
        """
        This is called with the actual x and y values with units. If without units we should expect to move in native
        units.

        @param x:
        @param y:
        @return:
        """
        self.connect_if_needed()
        self.native_x, self.native_y = self.service.physical_to_device_position(x, y)
        if self.native_x > 0xFFFF:
            self.native_x = 0xFFFF
        if self.native_x < 0:
            self.native_x = 0

        if self.native_y > 0xFFFF:
            self.native_y = 0xFFFF
        if self.native_y < 0:
            self.native_y = 0

        self.connection.set_xy(self.native_x, self.native_y)

    def move_rel(self, dx, dy):
        """
        This is called with dx and dy values to move a relative amount.

        @param dx:
        @param dy:
        @return:
        """
        self.connect_if_needed()
        unit_dx, unit_dy = self.service.physical_to_device_length(dx, dy)
        self.native_x += unit_dx
        self.native_y += unit_dy

        if self.native_x > 0xFFFF:
            self.native_x = 0xFFFF
        if self.native_x < 0:
            self.native_x = 0

        if self.native_y > 0xFFFF:
            self.native_y = 0xFFFF
        if self.native_y < 0:
            self.native_y = 0

        self.connection.set_xy(self.native_x, self.native_y)

    def home(self, x=None, y=None):
        """
        This is called with x, and y, to set an adjusted home or use whatever home we have.
        @param x:
        @param y:
        @return:
        """
        self.move_abs("50%", "50%")

    def blob(self, data_type, data):
        """
        This is called to give pure data to the backend. Data is assumed to be native data-type as loaded from a file.

        @param data_type:
        @param data:
        @return:
        """
        if data_type == "balor":
            self.connect_if_needed()
            self.connection.execute(data, 1)

    def set(self, attribute, value):
        """
        This is called to set particular attributes. These attributes will be set in the cutcode as well but sometimes
        there is a need to set these outside that context. This can also set the default values to be used inside
        the cutcode being processed.

        @param attribute:
        @param value:
        @return:
        """
        if attribute == "speed":
            pass
        print(attribute, value)

    def rapid_mode(self):
        """
        Expects to be in rapid jogging mode.
        @return:
        """
        pass

    def program_mode(self):
        """
        Expects to run jobs at a speed in a programmed mode.
        @return:
        """
        pass

    def raster_mode(self, *args):
        """
        Expects to run a raster job. Raster information is set in special modes to stop the laser head from moving
        too far.

        @return:
        """
        pass

    def wait_finished(self):
        """
        Expects to be caught up such that the next command will happen immediately rather than get queued.

        @return:
        """
        pass

    def function(self, function):
        function()

    def wait(self, secs):
        time.sleep(secs)

    def console(self, value):
        self.service(value)

    def beep(self):
        """
        Wants a system beep to be issued.

        @return:
        """
        self.service("beep\n")

    def signal(self, signal, *args):
        """
        Wants a system signal to be sent.

        @param signal:
        @param args:
        @return:
        """
        self.service.signal(signal, *args)

    def pause(self):
        """
        Wants the driver to pause.
        @return:
        """
        self.connect_if_needed()
        if self.paused:
            self.resume()
            return
        self.paused = True
        self.connection.raw_stop_list()

    def resume(self):
        """
        Wants the driver to resume.

        This typically issues from the realtime queue which means it will call even if we tell work_hold that we should
        hold the work.

        @return:
        """
        self.connect_if_needed()
        self.paused = False
        self.connection.raw_restart_list()

    def reset(self):
        """
        Wants the job to be aborted and action to be stopped.

        @return:
        """
        self.connection.abort()

    def status(self):
        """
        Wants a status report of what the driver is doing.
        @return:
        """
        pass
