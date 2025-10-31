# src/core/metrics.py

import numpy as np
from typing import Dict, List, Tuple

def calculate_area_coverage_and_redundancy(
    trajectory_data: Dict[str, List[Tuple[float, float]]], 
    area_bounds: Tuple[float, float, float, float], # (min_x, max_x, min_y, max_y)
    grid_size: int = 50
) -> Tuple[float, float]:
    """
    Calcula a Cobertura Média da Área e a Redundância de Rota.
    
    A cobertura é calculada usando uma grade (grid) sobre a área.
    A redundância é a frequência com que células do grid foram visitadas por múltiplos drones.
    """
    min_x, max_x, min_y, max_y = area_bounds
    
    # 1. Inicializar o Grid
    # O grid armazena o número de vezes que cada célula foi visitada
    grid = np.zeros((grid_size, grid_size), dtype=int)
    
    # Fatores de conversão de coordenada (x, y) para índice do grid (i, j)
    x_scale = grid_size / (max_x - min_x)
    y_scale = grid_size / (max_y - min_y)
    
    # 2. Popular o Grid com as Trajetórias
    for drone_id, trajectory in trajectory_data.items():
        # Usamos um grid temporário para contar visitas por drone
        drone_grid = np.zeros((grid_size, grid_size), dtype=bool)
        
        for x, y in trajectory:
            # Converte as coordenadas para índices do grid
            i = int((x - min_x) * x_scale)
            j = int((y - min_y) * y_scale)
            
            # Garante que os índices estejam dentro dos limites
            i = np.clip(i, 0, grid_size - 1)
            j = np.clip(j, 0, grid_size - 1)
            
            # Marca a célula como visitada por este drone
            drone_grid[i, j] = True
        
        # Adiciona o grid de visitas do drone ao grid total
        grid += drone_grid.astype(int)
        
    # 3. Cálculo da Cobertura Média da Área (%)
    # Células visitadas (grid > 0)
    visited_cells = np.sum(grid > 0)
    total_cells = grid_size * grid_size
    area_coverage = (visited_cells / total_cells) * 100.0
    
    # 4. Cálculo da Redundância de Rota (%)
    # Células visitadas mais de uma vez (grid > 1)
    redundant_cells = np.sum(grid > 1)
    
    # A redundância é a proporção de células visitadas que foram visitadas por múltiplos drones
    if visited_cells == 0:
        route_redundancy = 0.0
    else:
        route_redundancy = (redundant_cells / visited_cells) * 100.0
        
    return area_coverage, route_redundancy

def calculate_individual_autonomy(log_events: List[str], drone_ids: List[str]) -> Dict[str, int]:
    """
    Calcula o número de eventos de recarga (Refuel) por drone.
    Um número menor significa maior autonomia mantida.
    """
    recharge_counts = {did: 0 for did in drone_ids}
    
    for event in log_events:
        if "REABASTECIDO" in event:
            for did in drone_ids:
                if f"Drone {did}" in event:
                    recharge_counts[did] += 1
                    break
                    
    return recharge_counts
