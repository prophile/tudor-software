def _position_to_duty(position):
    return 50 + 50*position

def _duty_to_position(duty):
    return (duty - 50)/50.0

def _position_calibrate(position, calibration):
    gradient, constant = calibration if calibration else (1.0, 0.0)
    output = gradient*position + constant
    if abs(output) > 1:
        output /= abs(output)
    return output

def _position_uncalibrate(position, calibration):
    gradient, constant = calibration if calibration else (1.0, 0.0)
    output = (position - constant) / gradient
    if abs(output) > 1:
        output /= abs(output)
    return output

def set(robot, servo, position, calibration = None):
    """
    Utility method for setting a servo position. If the servo is given as
    None, this has no effect.
    
    """
    if servo is None:
        return
    position = _position_calibrate(position, calibration)
    robot.servos[servo[0]][servo[1]] = _position_to_duty(position)

def get(robot, servo, calibration = None):
    if servo is None:
        return None
    position = _duty_to_position(robot.servos[servo[0]][servo[1]])
    return _position_uncalibrate(position, calibration)

