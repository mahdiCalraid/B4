#!/usr/bin/env python3
"""Visualize and analyze the B4 agents pipeline map."""

import json
from pathlib import Path
from typing import Dict, List, Set

def load_agents_map(file_path: str = "agents_map.json") -> Dict:
    """Load the agents map from JSON file."""
    with open(file_path, 'r') as f:
        return json.load(f)

def print_pipeline_flow(agents_map: Dict):
    """Print a visual representation of the pipeline flow."""
    print("🌊 B4 MEMORY WATERFALL PIPELINE FLOW")
    print("=" * 70)

    # Group nodes by stage
    stages = {}
    for node in agents_map['nodes']:
        stage = node.get('stage', 'SYSTEM')
        if stage not in stages:
            stages[stage] = []
        stages[stage].append(node)

    # Print in stage order
    stage_order = ['SYSTEM', 'ATTENTION', 'PERCEPTION', 'COMPREHENSION', 'CONSOLIDATION', 'INTEGRATION']

    for stage in stage_order:
        if stage in stages:
            if stage == 'SYSTEM':
                print(f"\n📥 INPUT/OUTPUT")
            else:
                print(f"\n🔹 Stage: {stage}")
            print("-" * 40)

            for node in stages[stage]:
                node_type = "→" if node['type'] == 'trigger' else "←" if node['type'] == 'endpoint' else "•"
                parallel = " [PARALLEL]" if node.get('parallel') else ""
                print(f"  {node_type} {node['name']:<30} (id: {node['id']}){parallel}")
                if node.get('description'):
                    print(f"    └─ {node['description']}")

def print_connections_matrix(agents_map: Dict):
    """Print a connection matrix showing data flow."""
    print("\n\n📊 CONNECTION MATRIX")
    print("=" * 70)

    # Build connection map
    connections = {}
    for conn in agents_map['connections']:
        if isinstance(conn['source'], list):
            for source in conn['source']:
                if source not in connections:
                    connections[source] = []
                connections[source].append({
                    'target': conn['target'],
                    'type': conn['type'],
                    'flow': conn['data_flow']
                })
        else:
            source = conn['source']
            if source not in connections:
                connections[source] = []
            connections[source].append({
                'target': conn['target'],
                'type': conn['type'],
                'flow': conn['data_flow']
            })

    # Print connections
    for source, targets in connections.items():
        print(f"\n📍 {source}")
        for target in targets:
            arrow = "═══>" if target['type'] == 'main' else "--->" if target['type'] == 'conditional' else "~~~>"
            print(f"    {arrow} {target['target']:<20} [{target['flow']}]")

def print_model_usage(agents_map: Dict):
    """Print model usage for each agent."""
    print("\n\n🤖 MODEL ASSIGNMENTS")
    print("=" * 70)

    model_groups = {}
    for node in agents_map['nodes']:
        if 'model' in node:
            model = node['model']
            if model not in model_groups:
                model_groups[model] = []
            model_groups[model].append(node['name'])

    for model, agents in model_groups.items():
        print(f"\n📌 {model}:")
        for agent in agents:
            print(f"    • {agent}")

def print_database_access(agents_map: Dict):
    """Print which agents access the database."""
    print("\n\n💾 DATABASE ACCESS")
    print("=" * 70)

    for node in agents_map['nodes']:
        if 'database_access' in node:
            print(f"\n🔸 {node['name']}:")
            db_access = node['database_access']
            for db_type, details in db_access.items():
                print(f"    Database: {db_type}")
                print(f"    Tables: {', '.join(details['tables'])}")
                print(f"    Operations: {', '.join(details['operations'])}")

def analyze_parallel_execution(agents_map: Dict):
    """Analyze parallel execution opportunities."""
    print("\n\n⚡ PARALLEL EXECUTION")
    print("=" * 70)

    parallel = agents_map['execution']['parallel_execution']
    for stage, agents in parallel.items():
        print(f"\n{stage}: {len(agents)} agents run in parallel")
        for agent in agents:
            # Find agent details
            for node in agents_map['nodes']:
                if node['id'] == agent:
                    print(f"    • {node['name']}")
                    break

def generate_mermaid_diagram(agents_map: Dict) -> str:
    """Generate a Mermaid diagram for visualization."""
    diagram = ["graph TD"]

    # Add nodes
    for node in agents_map['nodes']:
        shape = "([" if node['type'] == 'trigger' else "])" if node['type'] == 'endpoint' else "]"
        shape_start = "([" if node['type'] == 'trigger' else "[(" if node['type'] == 'endpoint' else "["
        label = f"{node['name']}<br/>{node.get('stage', '')}"
        diagram.append(f"    {node['id']}{shape_start}{label}{shape}")

    # Add connections
    for conn in agents_map['connections']:
        if isinstance(conn['source'], list):
            for source in conn['source']:
                arrow = "==>" if conn['type'] == 'main' else "-..->" if conn['type'] == 'conditional' else "-->"
                diagram.append(f"    {source} {arrow} {conn['target']}")
        else:
            arrow = "==>" if conn['type'] == 'main' else "-..->" if conn['type'] == 'conditional' else "-->"
            diagram.append(f"    {conn['source']} {arrow} {conn['target']}")

    return "\n".join(diagram)

def main():
    """Main execution."""
    # Load the map
    agents_map = load_agents_map()

    # Print various visualizations
    print_pipeline_flow(agents_map)
    print_connections_matrix(agents_map)
    print_model_usage(agents_map)
    print_database_access(agents_map)
    analyze_parallel_execution(agents_map)

    # Generate Mermaid diagram
    print("\n\n📈 MERMAID DIAGRAM")
    print("=" * 70)
    print("Copy this to https://mermaid.live for visualization:")
    print("-" * 70)
    mermaid = generate_mermaid_diagram(agents_map)
    print(mermaid)

    # Summary
    print("\n\n📋 SUMMARY")
    print("=" * 70)
    print(f"Total Nodes: {len(agents_map['nodes'])}")
    print(f"Processing Agents: {len([n for n in agents_map['nodes'] if n['type'] == 'processor'])}")
    print(f"Total Connections: {len(agents_map['connections'])}")
    print(f"Stages: {len(agents_map['workflow']['stages'])}")

if __name__ == "__main__":
    main()