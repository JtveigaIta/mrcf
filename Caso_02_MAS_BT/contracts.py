import datetime
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import List

# Lista global para armazenar todos os logs da simulação
SIMULATION_LOGS: List[str] = []

# === Log ===
def log_event(message):
    """Função centralizada para log de eventos, agora armazena na lista global."""
    full_message = f"[{datetime.now().strftime('%H:%M:%S')}] {message}"
    print(full_message) # Mantém a impressão para acompanhamento
    SIMULATION_LOGS.append(full_message) # Armazena o log
# Função de log simplificada para o Colab

class ContractTemplate:
    """Template de Contrato para o MAS."""
    def __init__(self, id, required_skills):
        self.id = id
        self.required_skills = required_skills

class CoalitionContract:
    """Contrato de Coalizão para o MAS."""
    def __init__(self, id, required_skills):
        self.id = id
        self.required_skills = required_skills
        self.members = []

class CandidateResource:
    """Recurso Candidato (Drone) para o MAS."""
    def __init__(self, id, skills, cost, time, quality, battery, position, available):
        self.id = id
        self.skills = skills
        self.cost = cost
        self.time = time
        self.quality = quality
        self.battery = battery
        self.position = position
        self.available = available
