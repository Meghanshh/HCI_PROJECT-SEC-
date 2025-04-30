import os
import matplotlib.pyplot as plt
import networkx as nx
from pathlib import Path

def create_flowchart():
    G = nx.DiGraph()
    
    # Add nodes
    nodes = [
        'Start', 'Select Mode', 'Capture Media', 'Process Data',
        'Detect Emotion?', 'Detect Sign Language?', 'Analyze Results',
        'Display Results', 'End'
    ]
    G.add_nodes_from(nodes)
    
    # Add edges
    edges = [
        ('Start', 'Select Mode'),
        ('Select Mode', 'Capture Media'),
        ('Capture Media', 'Process Data'),
        ('Process Data', 'Detect Emotion?'),
        ('Detect Emotion?', 'Detect Sign Language?'),
        ('Detect Emotion?', 'Analyze Results'),
        ('Detect Sign Language?', 'Analyze Results'),
        ('Analyze Results', 'Display Results'),
        ('Display Results', 'End')
    ]
    G.add_edges_from(edges)
    
    return G

def create_ml_pipeline():
    G = nx.DiGraph()
    
    # Add nodes
    nodes = [
        'Data Collection', 'Data Validation', 'Data Preprocessing',
        'Feature Engineering', 'Model Selection', 'Hyperparameter Tuning',
        'Model Training', 'Model Evaluation', 'Model Deployment',
        'Performance Monitoring'
    ]
    G.add_nodes_from(nodes)
    
    # Add edges
    edges = [
        ('Data Collection', 'Data Validation'),
        ('Data Validation', 'Data Preprocessing'),
        ('Data Preprocessing', 'Feature Engineering'),
        ('Feature Engineering', 'Model Selection'),
        ('Model Selection', 'Hyperparameter Tuning'),
        ('Hyperparameter Tuning', 'Model Training'),
        ('Model Training', 'Model Evaluation'),
        ('Model Evaluation', 'Model Deployment'),
        ('Model Deployment', 'Performance Monitoring'),
        ('Performance Monitoring', 'Data Collection')  # Feedback loop
    ]
    G.add_edges_from(edges)
    
    return G

def create_ucd():
    G = nx.DiGraph()
    
    # Add nodes
    nodes = [
        'User Research', 'Persona Creation', 'User Stories',
        'Requirements Analysis', 'Design', 'Prototype',
        'Usability Testing', 'Implementation', 'User Feedback',
        'Iteration'
    ]
    G.add_nodes_from(nodes)
    
    # Add edges
    edges = [
        ('User Research', 'Persona Creation'),
        ('Persona Creation', 'User Stories'),
        ('User Stories', 'Requirements Analysis'),
        ('Requirements Analysis', 'Design'),
        ('Design', 'Prototype'),
        ('Prototype', 'Usability Testing'),
        ('Usability Testing', 'Implementation'),
        ('Implementation', 'User Feedback'),
        ('User Feedback', 'Iteration'),
        ('Iteration', 'User Research'),  # Full cycle
        ('Usability Testing', 'Design'),  # Quick feedback
        ('User Feedback', 'Design')  # Direct feedback
    ]
    G.add_edges_from(edges)
    
    return G

def create_activity():
    G = nx.DiGraph()
    
    # Add nodes with swimlane indicators
    nodes = [
        'User: Start', 'User: Select Mode', 'User: Provide Input',
        'System: Process Input', 'System: Detect Features',
        'System: Analyze Data', 'System: Generate Results',
        'User: View Results', 'User: End'
    ]
    G.add_nodes_from(nodes)
    
    # Add edges
    edges = [
        ('User: Start', 'User: Select Mode'),
        ('User: Select Mode', 'User: Provide Input'),
        ('User: Provide Input', 'System: Process Input'),
        ('System: Process Input', 'System: Detect Features'),
        ('System: Detect Features', 'System: Analyze Data'),
        ('System: Analyze Data', 'System: Generate Results'),
        ('System: Generate Results', 'User: View Results'),
        ('User: View Results', 'User: End')
    ]
    G.add_edges_from(edges)
    
    return G

def create_er_diagram():
    G = nx.DiGraph()
    
    # Add nodes with attributes
    nodes = [
        'USER\n(user_id: PK\nusername: VARCHAR\nemail: VARCHAR\ncreated_at: TIMESTAMP)',
        'EMOTION_RECORD\n(record_id: PK\nuser_id: FK\nemotion_type: VARCHAR\nconfidence: FLOAT\ntimestamp: TIMESTAMP)',
        'GESTURE_RECORD\n(record_id: PK\nuser_id: FK\ngesture_type: VARCHAR\nconfidence: FLOAT\ntimestamp: TIMESTAMP)',
        'SESSION\n(session_id: PK\nuser_id: FK\nstart_time: TIMESTAMP\nend_time: TIMESTAMP)'
    ]
    G.add_nodes_from(nodes)
    
    # Add edges with relationship types
    edges = [
        ('USER', 'EMOTION_RECORD', {'label': '1:N'}),
        ('USER', 'GESTURE_RECORD', {'label': '1:N'}),
        ('USER', 'SESSION', {'label': '1:N'})
    ]
    G.add_edges_from([(u, v) for u, v, _ in edges])
    
    return G

def draw_diagram(G, title, filename):
    plt.figure(figsize=(12, 8))
    
    # Use different layouts based on diagram type
    if 'er_diagram' in filename:
        pos = nx.spring_layout(G, k=2, iterations=100)
    else:
        pos = nx.spring_layout(G, k=1, iterations=50)
    
    # Draw nodes with different styles based on diagram type
    if 'er_diagram' in filename:
        # ER Diagram specific styling
        nx.draw_networkx_nodes(G, pos, node_color='lightblue', 
                             node_size=3000, alpha=0.7)
        nx.draw_networkx_edges(G, pos, edge_color='gray', 
                             arrows=True, arrowsize=20)
        nx.draw_networkx_labels(G, pos, font_size=8, 
                              font_family='monospace')
    elif 'activity' in filename:
        # Activity Diagram specific styling
        user_nodes = [n for n in G.nodes() if 'User:' in n]
        system_nodes = [n for n in G.nodes() if 'System:' in n]
        
        nx.draw_networkx_nodes(G, pos, nodelist=user_nodes,
                             node_color='lightgreen', node_size=2000)
        nx.draw_networkx_nodes(G, pos, nodelist=system_nodes,
                             node_color='lightblue', node_size=2000)
        nx.draw_networkx_edges(G, pos, edge_color='gray', 
                             arrows=True, arrowsize=20)
        nx.draw_networkx_labels(G, pos, font_size=10)
    else:
        # Default styling for other diagrams
        nx.draw_networkx_nodes(G, pos, node_color='lightblue', 
                             node_size=2000, alpha=0.7)
        nx.draw_networkx_edges(G, pos, edge_color='gray', 
                             arrows=True, arrowsize=20)
        nx.draw_networkx_labels(G, pos, font_size=10)
    
    plt.title(title, pad=20)
    plt.axis('off')
    
    # Save the figure
    output_dir = Path("diagrams/output")
    output_dir.mkdir(exist_ok=True)
    plt.savefig(output_dir / f"{filename}.png", dpi=300, bbox_inches='tight')
    plt.close()

def generate_diagrams():
    diagrams = [
        (create_flowchart(), "System Flowchart", "flowchart"),
        (create_ml_pipeline(), "ML Pipeline", "ml_pipeline"),
        (create_ucd(), "User-Centered Design", "ucd"),
        (create_activity(), "Activity Diagram", "activity"),
        (create_er_diagram(), "ER Diagram", "er_diagram")
    ]
    
    for G, title, filename in diagrams:
        draw_diagram(G, title, filename)
        print(f"Generated {filename}.png")

if __name__ == "__main__":
    generate_diagrams() 