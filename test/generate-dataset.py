import requests
import argparse
import os
import random
from tqdm import tqdm

# set your lorem-markdown endpoint here
ENDPOINT_URL = "https://jaspervdj.be/lorem-markdownum/markdown.txt?num-blocks={nblocks}"

parser = argparse.ArgumentParser()
parser.add_argument("-o", help="Output directory", default="output")
parser.add_argument("-n", help="Count of files to generate", default=1, type=int)
parser.add_argument("--max_b", help="Number of blocks (max)", default=50, type=int)
parser.add_argument("--min_b", help="Number of blocks (min)", default=10, type=int)
args = parser.parse_args()

print("Output directory: ", args.o)


for index in tqdm(range(args.n)):
    n_blocks = random.randint(args.min_b, args.max_b)
    markdown_text = requests.get(ENDPOINT_URL.format(nblocks=n_blocks)).text
    file_path = os.path.join(args.o, str(index))
    if not os.path.exists(file_path):
        os.makedirs(file_path)
        
    with open(os.path.join(file_path, "origin.md"), "w") as f:
        f.write(markdown_text)
    with open(os.path.join(file_path, "copy.md"), "w") as f:
        f.write(markdown_text)
    # Create a random paragraph to insert
    insert_text = requests.get(ENDPOINT_URL.format(nblocks=1)).text

    # Choose random insertion position
    lines = markdown_text.split('\n')
    insert_pos = random.randint(0, len(lines))

    # Insert the paragraph and write to modified file
    lines.insert(insert_pos, insert_text)
    modified_text = '\n'.join(lines)

    with open(os.path.join(file_path, "modified_0.md"), "w") as f:
      f.write(modified_text)
      
    for i in range(1, 3):  # Add 2 more modified versions
      insert_text = requests.get(ENDPOINT_URL.format(nblocks=2)).text
      lines = markdown_text.split('\n')
      insert_pos = random.randint(0, len(lines))
      lines.insert(insert_pos, insert_text)
      modified_text = '\n'.join(lines)
      
      with open(os.path.join(file_path, f"modified_{i}.md"), "w") as f:
        f.write(modified_text)
    
    # Create modified_3.md with just a single sentence added
    lines = markdown_text.split('\n')
    # Find non-empty lines from the end
    for i in range(len(lines)-1, -1, -1):
      if lines[i].strip():
        insert_pos = i
        break
    insert_text = "Quick fox jump over lazy dog"
    lines[insert_pos] = lines[insert_pos] + " " + insert_text
    modified_text = '\n'.join(lines)
      
    with open(os.path.join(file_path, "modified_3.md"), "w") as f:
      f.write(modified_text)
        
    markdown_text = requests.get(ENDPOINT_URL.format(nblocks=n_blocks)).text
    with open(os.path.join(file_path, "another.md"), "w") as f:
        f.write(markdown_text)
        
    