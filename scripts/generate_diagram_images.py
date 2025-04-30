import os
import re
from pathlib import Path
import requests
import base64
import json

def extract_mermaid_blocks(markdown_file):
    """Extract Mermaid code blocks from markdown file."""
    with open(markdown_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find all Mermaid code blocks
    pattern = r'```mermaid\n(.*?)\n```'
    blocks = re.findall(pattern, content, re.DOTALL)
    
    return blocks

def generate_diagram_image(mermaid_code, output_path):
    """Generate image from Mermaid code using Mermaid Live API."""
    # Encode the Mermaid code
    encoded_code = base64.b64encode(mermaid_code.encode()).decode()
    
    # Prepare the request
    url = "https://mermaid.ink/img"
    params = {
        "type": "png",
        "code": encoded_code
    }
    
    # Make the request
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        # Save the image
        with open(output_path, 'wb') as f:
            f.write(response.content)
        return True
    else:
        print(f"Error generating diagram: {response.status_code}")
        return False

def main():
    # Create output directory
    output_dir = Path("docs/diagrams")
    output_dir.mkdir(exist_ok=True)
    
    # Path to the markdown file
    markdown_file = "docs/low_level_design.md"
    
    # Extract Mermaid blocks
    mermaid_blocks = extract_mermaid_blocks(markdown_file)
    
    # Generate images for each block
    for i, block in enumerate(mermaid_blocks):
        # Determine diagram type from the first line
        first_line = block.split('\n')[0].strip().lower()
        if 'classdiagram' in first_line:
            diagram_type = 'class'
        elif 'sequencediagram' in first_line:
            diagram_type = 'sequence'
        elif 'statediagram' in first_line:
            diagram_type = 'state'
        elif 'flowchart' in first_line:
            diagram_type = 'flow'
        else:
            diagram_type = 'diagram'
        
        # Generate output filename
        output_file = output_dir / f"{diagram_type}_diagram_{i+1}.png"
        
        # Generate the image
        print(f"Generating {output_file}...")
        if generate_diagram_image(block, output_file):
            print(f"Successfully generated {output_file}")
        else:
            print(f"Failed to generate {output_file}")

if __name__ == "__main__":
    main() 