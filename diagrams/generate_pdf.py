import os
import subprocess
from pathlib import Path

def generate_pdf():
    # Create output directory if it doesn't exist
    output_dir = Path("diagrams/output")
    output_dir.mkdir(exist_ok=True)
    
    # List of diagrams to convert
    diagrams = [
        "flowchart",
        "ml_pipeline",
        "ucd",
        "activity",
        "er_diagram"
    ]
    
    # Convert each diagram to PDF
    for diagram in diagrams:
        input_file = f"diagrams/{diagram}.mmd"
        output_file = f"diagrams/output/{diagram}.pdf"
        
        # Use mmdc (Mermaid CLI) to convert to PDF
        subprocess.run([
            "npx", "-p", "@mermaid-js/mermaid-cli", "mmdc",
            "-i", input_file,
            "-o", output_file,
            "-t", "default",
            "-b", "white"
        ])
    
    print("PDFs generated successfully in diagrams/output/")

if __name__ == "__main__":
    generate_pdf() 