
# Relatório de Avaliação - Case Study 1: Patrulha Multi-Drone Independente

## Configuração da Simulação
- **Drones Simulados:** 3 (D1, D2, D3)
- **Ticks Totais:** 200
- **MAS Ativo:** Não (Frequência de Contrato: 9999)
- **Objetivo:** Observar ineficiências globais devido à tomada de decisão isolada.

## Métricas de Desempenho

| Métrica | Valor | Interpretação |
| :--- | :--- | :--- |
| **Cobertura Média da Área (%)** | 13.96% | Efetividade coletiva sem coordenação. |
| **Redundância de Rota (%)** | 20.92% | Ineficiência operacional devido à sobreposição de rotas. |

## Autonomia Individual Mantida (Robustez da BT)

| Drone ID | Eventos de Recarga | Interpretação |
| :--- | :--- | :--- |
| D1 | 1 | Recarga acionada pela BT |
| D2 | 0 | Autonomia mantida |
| D3 | 0 | Autonomia mantida |

## Conclusão
A simulação confirma que, embora a BT individual garanta a autonomia (Recarga: True), a falta de coordenação resulta em uma Redundância de Rota de 20.92%.
