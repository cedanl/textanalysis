import ast
import os

def extract_page_info(file_path):
    with open(file_path, 'r') as file:
        tree = ast.parse(file.read())
        title = None
        icon = None
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        if target.id == 'title' and isinstance(node.value, ast.Str):
                            title = node.value.s
                        elif target.id == 'icon' and isinstance(node.value, ast.Str):
                            icon = node.value.s
                            
        return title, icon

def get_screens():
    screens = []
    base_dir = "src/screens"
    
    for root, _, files in os.walk(base_dir):
        if root.count(os.sep) - base_dir.count(os.sep) <= 1:  # Only go one level deep
            for file in files:
                if file.endswith(".py") and file != "__init__.py":
                    full_path = os.path.join(root, file)
                    title, icon = extract_page_info(full_path)
                    subdirectory = os.path.basename(root) if root != base_dir else None
                    
                    screens.append({
                        'path': os.path.relpath(full_path, 'src').replace('\\', '/'),
                        'title': title,
                        'icon': icon,
                        'subdirectory': subdirectory
                    })
    
    return screens