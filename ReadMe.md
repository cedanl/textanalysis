<p align="center"><img src="src/assets/npuls_logo.png" alt="CEDA"></p>

<h1 align="center">Npuls-CEDA | Text Analysis</h1>

<div align="center"> <strong>🔍 Advanced Text Analysis Tool 📊</strong>
    <br> Powerful R-based topic modeling with a user-friendly Python Streamlit interface.<br> 
    <sub>Ideal for long responses and short surveys with word cloud visualization.</sub> </div> 

<br>

<div align="center">
  <h3>
    <a href="https://community-data-ai.npuls.nl/groups/view/44d20066-53a8-48c2-b4e9-be348e05d273/project-center-for-educational-data-analytics-ceda">
      Website
    </a>
    <span> | </span>
    <a href="https://github.com/cedanl/textanalysis#features">
      Features
    </a>
    <span> | </span>
    <a href="https://github.com/cedanl/textanalysis#download-and-installation">
      Downloads
    </a>
    <span> | </span>
    <a href="https://github.com/cedanl/textanalysis#development">
      Development
    </a>
    <span> | </span>
    <a href="https://github.com/cedanl/textanalysis#contribution">
      Contribution
    </a>
  </h3>
</div>

<div align="center">
  <sub>The ultimate text analysis tool. Built with ❤︎ by
    <a href="https://github.com/cedanl">CEDA</a> and
    <a href="https://github.com/cedanl/textanalysis/graphs/contributors">
      contributors
    </a>
    .
  </sub>
</div>

<br />


# Running the Application

Start the Streamlit app:

```
uv run streamlit run src/main.py
```


This will open the application in your default web browser.

## Using the Application

- Use the Word Cloud option for visualizing key terms in shorter surveys.
    
- Use the Topic Modeling option for detailed analysis of more complex text data.
    
- Results are automatically saved as an Excel file in the same directory as the script.


# Topic Modeling Tool

This tool is designed to perform topic modeling and other various text analysis on textual data using R for core analysis and a Python-based user interface (UI) built with the Tkinter library. It is particularly effective with long textual responses and provides visual aids through word clouds for shorter surveys.

# Very quick steps
```
python setup_env.py
venv\Scripts\activate
python topic_modeling_app.py
```

# Quick steps
  1. First, run the following script: setup_env.py
  2. Second, activate your virtual environment with the following command: venv\Scripts\activate
  3. Third, run the last script: topic_modeling_app.py

# Execution Policy Issues?
Are you running to any issues regarding Execution Policy? You can temporarily bypass the restriction for the current PowerShell session by running the following command in your terminal: 

```
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Afterwards, try activating the virtual environment again: 

```
venv\Scripts\activate
```

## Features

- **Topic Modeling:** Ideal for analyzing extensive text data.
- **Word Cloud:** Visualizes the most frequent terms in datasets, best suited for shorter surveys.
- **More to follow**

## Further prerequisites

Before using this tool, please ensure the following steps are completed to set up your environment:

### Install and Set Up Required Libraries

1. **R and Python:** Ensure both R and Python are installed on your computer. Download them from their official websites if necessary.
2. **Library Installation:**
   - **R Libraries:** Open your R console, navigate to the directory containing `requirements.R`, and execute `source('requirements.R')`.
   - **Python Libraries:** Open a command prompt or terminal, navigate to the directory containing `requirements.txt`, and execute `pip install -r requirements.txt`.

### Update Script Paths

- Verify that the TreeTagger tool is correctly installed and its path is appropriately set in **both** R scripts for text processing. Search for the term "teamIR" in the scripts to identify and update these paths.

## How to Run the Tool

### Starting the Application

- Open `topic_modeling_app.py` in your Python IDE (like IDLE or PyCharm) using the file browser.

### Using the Application

- The UI is designed to be user-friendly:
  - Use the **Word Cloud** option for shorter surveys to visualize key terms.
  - Use the **Topic Modeling** option for detailed analysis of more complex text data.
- Once the analysis is complete, the tool automatically saves the results in an Excel file in the same directory as the script.


## Contributors

Thank you to all the people who have already contributed to textanalysis[[contributors](https://github.com/cedanl/textanalysis/graphs/contributors)].

Special thanks to @[radboudir](https://github.com/radboudir) who started the project.

[![](https://github.com/asewnandan.png?size=50)](https://github.com/asewnandan)
[![](https://github.com/radboudir.png?size=50)](https://github.com/radboudir)
[![](https://github.com/tin900.png?size=50)](https://github.com/tin900)
[![](https://github.com/Tomeriko96.png?size=50)](https://github.com/Tomeriko96)


## Getting Help

If you encounter any issues or need further assistance, please feel free to contact amir.khodaie@ru.nl




