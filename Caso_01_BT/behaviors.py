import py_trees
import math
import numpy as np
from contracts import log_event
from interface import DroneMissionInterface

# === MOCK PYFLY (Para rodar no Colab ou sem o simulador real) ===
class MockPyFly:
    def __init__(self, *args):
        self.state = {"yaw": 0.0}
        self.roll = 0.0
        self.pitch = 0.0
        self.throttle = 0.0
        self.rudder = 0.0
        
    def set_control(self, roll, pitch, throttle, rudder):
        pass
        
    def update(self):
        pass
        
    def reset(self):
        pass
        
    def close(self):
        pass


# === PID Controller para o curso (yaw) ===
class PIDControllerCourse:
    def __init__(self, kp=1.0, ki=0.00001, kd=0.01):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.integral_course = 0.0
        self.error_previous_course = 0.0

    def calculate(self, reference, value):
        if value < 0.0:
            value += 360.0
            
        error = reference - value
        if error < -180:
            error += 360
        if error > 180:
            error -= 360
        
        error = math.radians(error)
        
        proportional = self.kp * error
        self.integral_course += self.ki * error
        derivative = self.kd * (error - self.error_previous_course)
        self.error_previous_course = error
        
        control = proportional + self.integral_course + derivative
        
        return np.clip(control, -math.radians(45), math.radians(45))


# === Condições e Ações do Behavior Tree ===

class Condition_Low_Battery(py_trees.behaviour.Behaviour):
    def __init__(self, drone_id: str, interface: DroneMissionInterface):
        super().__init__("LowBattery?")
        self.drone_id = drone_id
        self.interface = interface

    def update(self):
        b = self.interface.get_state(self.drone_id)['battery']
        if b < 30:
            log_event(f"BT: Drone {self.drone_id} com bateria baixa ({b}%).")
            return py_trees.common.Status.SUCCESS
        return py_trees.common.Status.FAILURE


class Action_Refuel(py_trees.behaviour.Behaviour):
    def __init__(self, drone_id: str, interface: DroneMissionInterface, skywalker: MockPyFly):
        super().__init__("Refuel")
        self.drone_id = drone_id
        self.interface = interface
        self.skywalker = skywalker

    def update(self):
        self.skywalker.reset()
        self.interface.update_drone_state(self.drone_id, 100, (0, 0), status='IDLE')
        log_event(f"BT: Drone {self.drone_id} REABASTECIDO na base (0, 0).")
        return py_trees.common.Status.SUCCESS


class Action_Patrol(py_trees.behaviour.Behaviour):
    def __init__(self, drone_id: str, interface: DroneMissionInterface, skywalker: MockPyFly):
        super().__init__(name="Action_Patrol")
        self.drone_id = drone_id
        self.interface = interface
        self.skywalker = skywalker
        self.pid_controller = PIDControllerCourse()
        self.index = 0
        self.step_size = 0.25 # Aumentado para movimento mais rápido
        
    def update(self):
        mission = self.interface.get_mission(self.drone_id)
        if mission is None or mission.get("type") != "patrol":
            return py_trees.common.Status.FAILURE

        points = mission.get("route", [])
        if not points:
            return py_trees.common.Status.FAILURE

        if self.index >= len(points):
            log_event(f"BT: Drone {self.drone_id} completou a patrulha. Reiniciando.")
            self.index = 0
            return py_trees.common.Status.SUCCESS

        pos = self.interface.get_position(self.drone_id)
        target = points[self.index]
        dx, dy = target[0] - pos[0], target[1] - pos[1]

        desired_course = math.degrees(math.atan2(dy, dx))
        current_yaw = desired_course
        control_roll = self.pid_controller.calculate(desired_course, current_yaw)

        new_pos = (
            pos[0] + self.step_size * math.cos(math.radians(desired_course)),
            pos[1] + self.step_size * math.sin(math.radians(desired_course))
        )

        state = self.interface.get_state(self.drone_id)
        new_battery = max(0, state['battery'] - 0.3) # Decaimento de bateria mais rápido
        
        self.interface.update_drone_state(self.drone_id, battery=new_battery, position=new_pos, status='PATROL')
        self.skywalker.set_control(roll=control_roll, pitch=0, throttle=0.7, rudder=0)
        self.skywalker.update()

        if math.hypot(dx, dy) < 0.3:
            log_event(f"BT: Drone {self.drone_id} chegou ao ponto {self.index + 1}/{len(points)}.")
            self.index += 1

        return py_trees.common.Status.RUNNING


# === Montagem da Árvore de Comportamento ===
def create_behavior_tree(drone_id: str, interface: DroneMissionInterface, skywalker: MockPyFly) -> py_trees.trees.BehaviourTree:
    root = py_trees.composites.Selector("RootSelector", memory=True)

    low_batt_seq = py_trees.composites.Sequence("LowBatterySeq", memory=True)
    low_batt_seq.add_children([
        Condition_Low_Battery(drone_id, interface),
        Action_Refuel(drone_id, interface, skywalker)
    ])

    patrol_action = Action_Patrol(drone_id, interface, skywalker)

    root.add_children([low_batt_seq, patrol_action])

    return py_trees.trees.BehaviourTree(root)
