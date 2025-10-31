```markdown
# 🛡️ Direitos Autorais e Propriedade Intelectual

**Arquitetura de Controle Multi-Agente para Replanejamento de Missões de VANTs (MRCF)**  
📄 *Propriedade Intelectual de* **Jackson Tavares Veiga**

**Título:** Mission Replanning and Control Framework (MRCF)  
**Autor:** Jackson Tavares Veiga  
**Nome do Arquivo:** Deposito_PropriedadeIntelectual_MRCF.pdf  
**Tamanho:** 2,2 MB  
**Criado em:** D:20250916233558Z  
**Modificado em:** D:20250916233558Z  
**Registro Oficial:** Depositado no Escritório de Direitos Autorais da Fundação Biblioteca Nacional  
**N°ID:** E0000000020250917001514721634186

---

# Projeto de Simulação de Drones  
## Mission Replanning and Control Framework (MRCF)
### Versão Acadêmica: *A Strategic Architecture for BVLOS Operations in UTM Environments*

Este projeto foi refatorado para ser **didático, modular e flexível**, facilitando a compreensão, manutenção e expansão por parte de alunos e pesquisadores.  
A estrutura de diretórios foi organizada com base em princípios **Orientados a Componentes**, permitindo o acoplamento controlado entre módulos e a futura integração com ambientes de simulação UTM.

---

## 🧭 Estrutura do Projeto

A organização modular favorece o reuso e a clareza de responsabilidades entre componentes.

```

.
├── config/
│   └── mission_config.json   # Configuração da missão e ambiente de simulação
├── src/
│   ├── **init**.py
│   ├── mas/
│   │   ├── **init**.py
│   │   ├── agents.py         # Definições dos Agentes do MAS (PAS, Broker, YPA, MRA, CLA)
│   │   └── contracts.py      # Contratos e Recursos (usando @dataclass)
│   ├── bt/
│   │   ├── **init**.py
│   │   └── behaviors.py      # Nós da Árvore de Comportamento (BT)
│   ├── core/
│   │   ├── **init**.py
│   │   └── interface.py      # Interface compartilhada entre módulos
│   └── simulation.py         # Lógica principal da simulação e execução
├── main.py                   # Ponto de entrada da aplicação
└── README.md

````

---

## ⚙️ Paradigmas de Programação

A arquitetura adota uma abordagem **Orientada a Agentes (POA)**, integrada ao conceito de **Component-Based Software Engineering (CBSE)**.  
Cada módulo representa um componente com funções bem definidas.

### Comparativo entre Abordagens

| Paradigma | Foco | Vantagens | Limitações |
|------------|------|------------|-------------|
| **Orientado a Agentes (POA)** | Autonomia e decisões locais | Modela proatividade, reatividade e cooperação | Maior complexidade conceitual |
| **Orientado a Dados (POD)** | Processamento e fluxo de dados | Simulações massivas mais rápidas | Perde clareza em decisões autônomas |

**Conclusão:**  
> Mantenha o paradigma *Orientado a Agentes* para capturar decisões autônomas (BT), mas use `@dataclass` e interfaces explícitas para isolamento de dados, alinhando-se ao paradigma *Orientado a Componentes*.

---

## 🧩 Correção do Erro `multitree` do PyFly

O erro `multitree` ocorre quando múltiplas instâncias do simulador `PyFly` são criadas fora da *main thread* ou sem controle de concorrência.

### ✅ Soluções Aplicadas

1. **Instância Única do PyFly:** Criada centralmente em `simulation.py`.  
2. **Uso de `py_trees.decorators.RunningIsFailure`:** Evita acessos simultâneos ao *hardware virtual*.  
3. **PID Encapsulado:** Substituição de variáveis globais por atributos de instância para segurança didática e thread-safe.

---

## ⚙️ Flexibilidade e Configuração

1. **Configuração via JSON:**  
   O arquivo `config/mission_config.json` define parâmetros de simulação, rotas e comportamento dos drones.

2. **Suporte a Múltiplos Drones:**  
   Cada drone tem sua própria instância de BT e configuração de rota.

3. **Seleção Dinâmica de BTs:**  
   O `simulation.py` permite criar árvores de comportamento conforme a missão.

---

## 🚀 Execução

Para rodar o projeto localmente:

```bash
python3 main.py
````

---

# 🧩 Execução no Google Colab

> ⚠️ O Google Colab **não possui suporte nativo ao PyFly**.
> Esta seção adapta o projeto com uma simulação de movimento em Python puro (MockPyFly).

---

## **Guia Passo a Passo**

### 🧱 Passo 1: Preparar o Ambiente e Estrutura

```python
import os
os.makedirs('src/mas', exist_ok=True)
os.makedirs('src/bt', exist_ok=True)
os.makedirs('src/core', exist_ok=True)
os.makedirs('config', exist_ok=True)
print("Estrutura de pastas criada.")
```

---

### 🗂️ Passo 2: Criar Arquivo `config/mission_config.json`

```python
config_json = """
{
  "simulation_ticks": 150,
  "tick_delay_seconds": 0.05,
  "pyfly_config_path": "pyfly_config.json",
  "pyfly_param_path": "x8_param.mat",
  "drones": [
    {
      "id": "drone_01",
      "initial_position": [0.0, 0.0],
      "initial_battery": 100,
      "skills": ["skill_A", "skill_B"],
      "cost": 100,
      "time": 5,
      "quality": 0.9,
      "route_type": "random_patrol",
      "route_points": 9
    }
  ],
  "mas_config": {
    "contract_skills": ["skill_A"],
    "contract_frequency": 20
  }
}
"""
with open('config/mission_config.json', 'w') as f:
    f.write(config_json)
print("Arquivo de configuração criado.")
```

---

### 📦 Passo 3: Instalar Dependências

```python
!pip install py-trees
```

---

### 🧠 Passo 4: Criar Mock do PyFly (`src/bt/behaviors.py`)

Inclua a classe `MockPyFly`, os controladores PID e os nós de comportamento BT, conforme o modelo adaptado no projeto original.
Esse mock substitui o simulador real e permite a execução no Colab.

*(Ver versão completa no arquivo original ou código acima.)*

---

### 🧩 Passo 5: Criar Demais Módulos

* `src/core/interface.py`
* `src/mas/contracts.py`
* `src/mas/agents.py`

Copie o conteúdo completo dos arquivos fornecidos.

---

### 🧮 Passo 6: Criar e Executar `src/simulation.py` (Adaptado)

O `MockPyFly` é importado em vez do `PyFly`, e os frames são gerados para visualização com `matplotlib` e `imageio`.

---

## 🎞️ Saída Visual

Durante a execução, os frames são salvos em `debug_frames/frame_001.png`, `frame_002.png`, etc.
Esses frames podem ser combinados em um **GIF animado** mostrando a trajetória dos drones.

---

# 📚 Créditos e Licenciamento

**Autor:** Jackson Tavares Veiga
**Instituição:** ITA / SAC / Projeto BR-UTM
**Ano:** 2025

O conteúdo deste repositório é de uso **acadêmico e educacional**, protegido por registro de propriedade intelectual.
Citações devem incluir o nome do autor e o título do trabalho.

> “Mission Replanning and Control Framework (MRCF)”
> *© 2025 Jackson Tavares Veiga. Todos os direitos reservados.*

---

# 🛡️ Direitos Autorais e Propriedade Intelectual (Rodapé)

**Propriedade Intelectual:** Arquitetura de Controle Multi-Agente para Replanejamento de Missões de VANTs
**Autor Registrado:** Jackson Tavares Veiga
**Depósito:** Escritório de Direitos Autorais - Fundação Biblioteca Nacional
**Registro:** E0000000020250917001514721634186
**Data:** 17 de setembro de 2025
**© Todos os Direitos Reservados**

```

---

Deseja que eu gere também a versão **PDF** desse README (com formatação preservada e cabeçalho/rodapé de direitos autorais)?  
Posso gerar direto em estilo técnico (A4, margens adequadas, fonte monoespaçada tipo `Consolas` ou `Courier`).
```
