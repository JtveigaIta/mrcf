import uuid
import json
import pandas as pd
from contracts import ContractTemplate, CoalitionContract, log_event

class PAS:
    """Problem Agent System (PAS) - Agente que cria o contrato."""
    def create_contract_template(self, skills):
        contract = ContractTemplate(id=str(uuid.uuid4())[:4], required_skills=skills)
        log_event(f"PAS criou contrato {contract.id} com habilidades {skills}")
        return contract

class Broker:
    """Broker - Agente que transmite a requisição para o YPA."""
    def transmit_request(self, request, ypa):
        data = json.dumps({"id": request.id, "required_skills": request.required_skills})
        log_event(f"Broker transmitiu requisição: {data}")
        ypa.store_request_json(data)

class YPA:
    """Yellow Pages Agent (YPA) - Agente que armazena as requisições."""
    def __init__(self):
        # Usando DataFrame do pandas para ser didático, mas em produção seria um banco de dados
        self.database = pd.DataFrame(columns=["Contract_ID", "Required_Skills"])
        log_event("YPA inicializado.")

    def store_request_json(self, json_data):
        data = json.loads(json_data)
        row = {"Contract_ID": data["id"], "Required_Skills": data["required_skills"]}
        # O uso de pd.concat em um loop é ineficiente, mas mantido para didática
        self.database = pd.concat([self.database, pd.DataFrame([row])], ignore_index=True)
        log_event(f"YPA armazenou requisição: {row}")

class MRA:
    """Matching and Resource Agent (MRA) - Agente que identifica candidatos."""
    def identify_candidates(self, resource_pool, required_skills):
        candidates = [r for r in resource_pool if r.available and any(s in r.skills for s in required_skills)]
        log_event(f"MRA encontrou {len(candidates)} candidatos com habilidades compatíveis.")
        return candidates

class CLA:
    """Coalition and Logistics Agent (CLA) - Agente que forma a coalizão."""
    def __init__(self): 
        self.coalitions = []
        log_event("CLA inicializado.")

    def create_coalition_contract(self, required_skills):
        c = CoalitionContract(id=str(uuid.uuid4())[:4], required_skills=required_skills)
        log_event(f"CLA criou contrato de coalizão {c.id}")
        return c

    def recruit_members(self, candidates, contract):
        """Recruta o melhor candidato para cada habilidade requerida."""
        for skill in contract.required_skills:
            suitable = [c for c in candidates if skill in c.skills and c.available]
            if not suitable:
                log_event(f"Nenhum candidato com habilidade {skill}")
                continue
            
            # Critério de seleção: Custo e Tempo baixos, Qualidade e Bateria altas.
            # O critério de escolha dos nós das BTs é feito aqui, no agente MRA/CLA
            # O usuário pode facilmente mudar essa função de custo.
            best = min(suitable, key=lambda c: c.cost*0.3 + c.time*0.3 - c.quality*0.2 - c.battery*0.2)
            
            if best.id not in contract.members:
                contract.members.append(best.id)
                log_event(f"CLA recrutou {best.id} para habilidade {skill}. Critério de otimização aplicado.")
                best.available = False # Marca o recurso como indisponível
        
        self.coalitions.append(contract)

