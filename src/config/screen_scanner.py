import ast
import os

def extract_page_info(file_path):
    with open(file_path, 'r') as file:
        content = file.read()
        tree = ast.parse(content)
        
        title = None
        icon = None
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                target = node.targets[0]
                if isinstance(target, ast.Name):
                    if target.id == 'title':
                        title = node.value.s  # Directly access the string value
                    elif target.id == 'icon':
                        icon = node.value.s

        return title, icon

# Get and process files
def get_screens():
    screens = []
    
    for file in os.listdir("src/screens"):
        if file.endswith(".py") and file != "__init__.py":
            path = f"screens/{file}"
            title, icon = extract_page_info(f"src/{path}")
            screens.append({
                'path': path,
                'title': title,
                'icon': icon
            })
            
    return screens