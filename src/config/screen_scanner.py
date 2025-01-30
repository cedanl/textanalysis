import ast
import os
import streamlit as st


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

def group_pages_by_subdirectory(pages):
    pages_by_subdirectory = {}
    
    for page in pages:
        subdirectory = page.get('subdirectory') or ""  # Use empty string if subdirectory is None
        if subdirectory not in pages_by_subdirectory:
            pages_by_subdirectory[subdirectory] = []
        
        # Create st.Page object for each item
        page_obj = st.Page(
            page['path'],
            title=page['title'],
            icon=page['icon']
        )
        pages_by_subdirectory[subdirectory].append(page_obj)
    
    return pages_by_subdirectory