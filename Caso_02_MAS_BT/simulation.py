# src/simulation.py (Versão Ajustada para Case Study 2)
import json
import random
import time
import os
import matplotlib.pyplot as plt
import imageio
import py_trees
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple

from interface import DroneMissionInterface
from agents import PAS, Broker, YPA, MRA, CLA
from contracts import CandidateResource, log_event, SIMULATION_LOGS
from behaviors import create_behavior_tree, MockPyFly
from metrics import calculate_area_coverage_and_redundancy, calculate_individual_autonomy


# === VISUALIZAÇÃO ===
def draw_frame(tick, interface: DroneMissionInterface, coalition_id, path_data, output_dir="debug_frames"):
    os.makedirs(output_dir, exist_ok=True)
    plt.figure(figsize=(6,6))
    
    for route in interface.routes.values():
        if route:
            px, py = zip(*route)
            plt.scatter(px, py, c='black', marker='x', alpha=0.5)

    for drone_id in interface.get_all_drone_ids():
        s = interface.get_state(drone_id)
        x, y = s['position']
        
        trajectory = path_data.get(drone_id, [])
        if trajectory:
            tx, ty = zip(*trajectory)
            plt.plot(tx, ty, c='lightblue', alpha=0.7)
            
        color = 'blue' if s['status'] == 'PATROL' else ('red' if s['status'] == 'FAILURE' else 'green')
        plt.scatter(x, y, c=color, s=120, label=f"Drone {drone_id}")
        plt.text(x+0.2, y+0.2, f"{drone_id}\n{int(s['battery'])}%", fontsize=8)
        
    plt.scatter(0, 0, c='gray', s=120, marker='s', label='Base')
    
    plt.title(f"Tick {tick} | Coalizão: {coalition_id}")
    plt.xlim(-1, 10)
    plt.ylim(-1, 10)
    plt.grid(True)
    plt.legend(loc='upper right', fontsize=8)
    
    plt.savefig(f"{output_dir}/frame_{tick:03d}.png")
    plt.close()


# === SIMULAÇÃO ===
def run_simulation(config_path="mission_config.json", disable_visual=False, return_metrics=False):
    """
    Executa a simulação do Case Study 2 com eventos dinâmicos:
    - Falha de drone (D2) no tick 100
    - Novo POI e missão de resgate no tick 150 (replanejamento dinâmico)
    """
    log_event("Iniciando simulação (Case Study 2)...")
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        log_event(f"Erro: Arquivo de configuração não encontrado em {config_path}")
        return
    
    SIMULATION_TICKS = config.get("simulation_ticks", 10)
    TICK_DELAY = config.get("tick_delay_seconds", 0.1)
    PYFLY_CONFIG = config.get("pyfly_config_path", "")
    PYFLY_PARAM = config.get("pyfly_param_path", "")
    
    interface = DroneMissionInterface()
    skywalker = MockPyFly(PYFLY_CONFIG, PYFLY_PARAM)
    
    pas, broker, ypa, mra, cla = PAS(), Broker(), YPA(), MRA(), CLA()
    
    drone_trees = {}
    drone_resources = []
    trajectory_data = {} 
    
    # --- Inicialização dos Drones ---
    for drone_conf in config.get("drones", []):
        drone_id = drone_conf["id"]
        resource = CandidateResource(
            id=drone_id,
            skills=drone_conf.get("skills", []),
            cost=drone_conf.get("cost", 1),
            time=drone_conf.get("time", 1),
            quality=drone_conf.get("quality", 1),
            battery=drone_conf.get("initial_battery", 100),
            position=tuple(drone_conf.get("initial_position", (0,0))),
            available=True
        )
        drone_resources.append(resource)
        
        if drone_conf.get("route_type") == "random_patrol":
            patrol_points = [(random.uniform(1,9), random.uniform(1,9)) for _ in range(drone_conf.get("route_points", 3))]
        elif drone_conf.get("route_type") == "fixed_patrol":
            patrol_points = [tuple(p) for p in drone_conf.get("route", [])]
        else:
            patrol_points = []
            
        interface.assign_route(drone_id, patrol_points)
        interface.update_drone_state(drone_id, resource.battery, resource.position, status='IDLE')
        trajectory_data[drone_id] = [resource.position]
        
        tree = create_behavior_tree(drone_id, interface, skywalker)
        drone_trees[drone_id] = tree
        
    coalition_id = None
    
    # --- Loop Principal ---
    for t in range(SIMULATION_TICKS):
        if not disable_visual:
            log_event(f"[Tempo t={t}]")
        
        # === 1. EVENTOS DINÂMICOS ===
        if t == 100:
            failed_drone_id = "D2"
            
            # Atualiza o estado do drone
            state = interface.get_state(failed_drone_id)
            interface.update_drone_state(failed_drone_id, battery=state['battery'], position=state['position'], status='FAILURE')
            log_event(f"EVENTO DINÂMICO: Drone {failed_drone_id} falhou no tick {t}. Status: FAILURE.")
            
            # Marca o recurso como indisponível
            for res in drone_resources:
                if res.id == failed_drone_id:
                    res.available = False
                    log_event(f"MAS: Recurso {failed_drone_id} marcado como indisponível para contratação.")
        
        # === 2. LÓGICA DO MAS ===
        if t % config.get("mas_config", {}).get("contract_frequency", 1) == 0 or t == 150:
            
            if t == 150:
                contract_skills = ["rescue"]
                log_event(f"EVENTO DINÂMICO: Novo POI (Missão de Resgate) surgiu no tick {t}.")
            else:
                contract_skills = config.get("mas_config", {}).get("contract_skills", [])
            
            template = pas.create_contract_template(contract_skills)
            broker.transmit_request(template, ypa)
            
            # Atualiza disponibilidade (considera falha e recarga)
            for res in drone_resources:
                state = interface.get_state(res.id)
                res.battery = state['battery']
                res.position = state['position']
                res.available = (state['status'] not in ['REFUELING', 'FAILURE'])
                
            candidates = mra.identify_candidates(drone_resources, template.required_skills)
            contract = cla.create_coalition_contract(template.required_skills)
            cla.recruit_members(candidates, contract)
            coalition_id = contract.id
            
            # === 3. REPLANEJAMENTO ===
            if t == 150 and contract.members:
                recruited_drone_id = contract.members[0]
                poi_route = [(5, 5), (6, 6)]
                interface.assign_route(recruited_drone_id, poi_route)
                log_event(f"REPLANEJAMENTO: Drone {recruited_drone_id} recrutado para POI. Nova rota atribuída: {poi_route}.")
        
        # === 4. EXECUÇÃO DAS BEHAVIOR TREES ===
        for drone_id, tree in drone_trees.items():
            tree.tick()
            current_pos = interface.get_state(drone_id)['position']
            trajectory_data[drone_id].append(current_pos)
            
        if not disable_visual:
            draw_frame(t, interface, coalition_id, trajectory_data)
        time.sleep(TICK_DELAY)
        
    skywalker.close()
    
    # === MÉTRICAS ===
    drone_ids = list(trajectory_data.keys())
    area_bounds = (-1.0, 10.0, -1.0, 10.0)
    
    try:
        area_coverage, route_redundancy = calculate_area_coverage_and_redundancy(trajectory_data, area_bounds)
    except Exception as e:
        log_event(f"Erro ao calcular métricas: {e}")
        area_coverage, route_redundancy = 0.0, 0.0

    try:
        recharge_counts = calculate_individual_autonomy(SIMULATION_LOGS, drone_ids)
    except Exception as e:
        log_event(f"Erro autonomia: {e}")
        recharge_counts = {did: 0 for did in drone_ids}
    
    if return_metrics:
        metrics = {
            "area_coverage": area_coverage,
            "route_redundancy": route_redundancy
        }
        metrics.update({f"recharge_count_{d}": recharge_counts.get(d, 0) for d in drone_ids})
        return metrics
    
    # === RELATÓRIO ===
    report = f"""
# Relatório de Avaliação - Case Study 2 (Eventos Dinâmicos)

| Métrica | Valor |
| :--- | :--- |
| **Cobertura Média da Área (%)** | {area_coverage:.2f} |
| **Redundância de Rota (%)** | {route_redundancy:.2f} |
"""
    with open("relatorio_case2.md", "w") as f:
        f.write(report)
    
    frames = [imageio.v2.imread(f"debug_frames/frame_{t:03d}.png") for t in range(SIMULATION_TICKS) if os.path.exists(f"debug_frames/frame_{t:03d}.png")]
    if frames:
        imageio.mimsave("simulacao_case2.gif", frames, duration=TICK_DELAY)
    
    return "simulacao_case2.gif"


# === FUNÇÕES DE BATCH ===
def generate_random_patrol_config(num_drones: int, num_points: int, area_bounds: Tuple[int, int, int, int] = (1, 9, 1, 9)) -> List[Dict]:
    min_coord, max_coord = area_bounds[0], area_bounds[1]
    drone_configs = []
    for i in range(num_drones):
        patrol_points = [
            [random.uniform(min_coord, max_coord), random.uniform(min_coord, max_coord)]
            for _ in range(num_points)
        ]
        drone_configs.append({
            "id": f"D{i+1}",
            "skills": ["search"],
            "cost": 1,
            "time": 1,
            "quality": 1,
            "initial_battery": 100,
            "initial_position": [5.0, 5.0],
            "route_type": "fixed_patrol",
            "route": patrol_points
        })
    return drone_configs


def run_batch_simulation(num_batches: int = 10, num_drones: int = 3, num_points: int = 5, config_path: str = "mission_config.json"):
    log_event(f"Iniciando Batch de {num_batches} Simulações (Case Study 2).")
    
    try:
        with open(config_path, 'r') as f:
            base_config = json.load(f)
    except FileNotFoundError:
        log_event(f"Erro: Arquivo de configuração não encontrado em {config_path}")
        return
    
    results = []
    for b in range(1, num_batches + 1):
        log_event(f"\n--- Simulação Batch {b}/{num_batches} ---")
        new_drones = generate_random_patrol_config(num_drones, num_points)
        config_copy = base_config.copy()
        config_copy["drones"] = new_drones
        temp_path = f"temp_config_batch_{b}.json"
        with open(temp_path, "w") as f:
            json.dump(config_copy, f, indent=4)
        metrics = run_simulation(temp_path, disable_visual=True, return_metrics=True)
        metrics["batch_id"] = b
        results.append(metrics)
    
    df = pd.DataFrame(results)
    summary = df.describe().loc[["mean", "std", "min", "max"]]
    
    final_report = f"""
# Relatório de Batch - Case Study 2 (Eventos Dinâmicos)

| Métrica | Média | Desvio Padrão | Mínimo | Máximo |
| :--- | :--- | :--- | :--- | :--- |
| **Cobertura Média da Área (%)** | {summary.loc['mean', 'area_coverage']:.2f} | {summary.loc['std', 'area_coverage']:.2f} | {summary.loc['min', 'area_coverage']:.2f} | {summary.loc['max', 'area_coverage']:.2f} |
| **Redundância de Rota (%)** | {summary.loc['mean', 'route_redundancy']:.2f} | {summary.loc['std', 'route_redundancy']:.2f} | {summary.loc['min', 'route_redundancy']:.2f} | {summary.loc['max', 'route_redundancy']:.2f} |
"""
    with open("relatorio_batch_case2.md", "w") as f:
        f.write(final_report)
    log_event("✅ Relatório de Batch gerado: relatorio_batch_case2.md")
    return df


# === EXECUÇÃO DIRETA ===
if __name__ == "__main__":
    run_batch_simulation(num_batches=5)