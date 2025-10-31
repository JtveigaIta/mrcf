import numpy as np

class DroneMissionInterface:
    """
    Interface Compartilhada para comunicação entre o MAS/BT e os drones.
    Isso simula um barramento de dados ou uma base de dados centralizada.
    """
    def __init__(self):
        # {drone_id: [ponto1, ponto2, ...]}
        self.routes = {} 
        # {drone_id: {'battery': 100, 'position': (x, y), 'status': 'IDLE'}}
        self.states = {} 
        # {drone_id: {"route": [ponto1, ...], "type": "patrol"}}
        self.missions = {} 

    def set_mission(self, drone_id, mission):
        """Define a missão atual para um drone."""
        self.missions[drone_id] = mission

    def get_mission(self, drone_id):
        """Retorna a missão atual de um drone."""
        return self.missions.get(drone_id, None)

    def set_position(self, drone_id, position):
        """Atualiza apenas a posição do drone."""
        if drone_id not in self.states:
            self.states[drone_id] = {'battery': 100, 'position': position, 'status': 'IDLE'}
        else:
            self.states[drone_id]['position'] = position

    def get_position(self, drone_id):
        """Retorna a posição (x, y) do drone."""
        return self.states.get(drone_id, {'position': (0.0, 0.0)})['position']

    def update_drone_state(self, drone_id, battery, position, status='RUNNING'):
        """Atualiza o estado completo do drone."""
        self.states[drone_id] = {'battery': battery, 'position': position, 'status': status}

    def get_state(self, drone_id):
        """Retorna o estado completo do drone."""
        return self.states.get(drone_id, {'battery': 100, 'position': (0, 0), 'status': 'IDLE'})

    def assign_route(self, drone_id, route):
        """Atribui uma rota e define a missão de patrulha."""
        self.routes[drone_id] = route
        self.set_mission(drone_id, {"route": route, "type": "patrol"})
        
    def get_next_point(self, drone_id):
        """Retorna o próximo ponto da rota mais próximo (lógica de seleção de nó da BT)."""
        route = self.routes.get(drone_id, [])
        pos = self.get_position(drone_id)
        
        # Lógica de seleção de nó (simplificada para o ponto mais próximo)
        if not route:
            return None
            
        # Encontra o ponto mais próximo na rota
        closest_point = min(route, key=lambda p: np.linalg.norm(np.array(p) - np.array(pos)))
        return closest_point

    def get_all_drone_ids(self):
        """Retorna todos os IDs de drones conhecidos."""
        return list(self.states.keys())

