# ---------------------------------------
# config section
# ---------------------------------------

##' *TODO* 
##' Check if config is correctly parsed

import yaml
import os

config_path = os.path.join('config', 'config.yaml')
with open(config_path, 'r') as file:
    config = yaml.safe_load(file)



# ---------------------------------------
# imports
# ---------------------------------------
import datetime
import tkinter as tk
from tkinter import filedialog, messagebox, ttk, Label, scrolledtext, Toplevel
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import seaborn as sns
from wordcloud import WordCloud
import subprocess
from PIL import Image, ImageTk
import pandas as pd
import os
import base64
from io import BytesIO
import threading
import re
import winreg
from collections import Counter


# ---------------------------------------
# (2) functionality section
# ---------------------------------------

def find_r_exe_from_registry():
    # find rscript path from registry
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\\R-Core\\R") as key:
            r_home, _ = winreg.QueryValueEx(key, "InstallPath")
            return os.path.join(r_home, "bin", "Rscript.exe")
    except FileNotFoundError:
        raise FileNotFoundError("r not installed or not found in registry.")


class ToolTip:
    # tooltip class
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tipwindow = None
        self.id = None
        widget.bind("<Enter>", self.enter)
        widget.bind("<Leave>", self.leave)

    def enter(self, event=None):
        self.schedule()

    def leave(self, event=None):
        self.unschedule()
        self.hidetip()

    def schedule(self):
        self.unschedule()
        self.id = self.widget.after(500, self.showtip)

    def unschedule(self):
        id_ = self.id
        self.id = None
        if id_:
            self.widget.after_cancel(id_)

    def showtip(self, event=None):
        x, y, cx, cy = self.widget.bbox("insert")
        x = x + self.widget.winfo_rootx() + 25
        y = y + cy + self.widget.winfo_rooty() + 25
        tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(1)
        tw.wm_geometry("+%d+%d" % (x, y))
        label = tk.Label(tw, text=self.text, justify='left',
                         background="#ffffe0", relief='solid', borderwidth=1,
                         font=("tahoma", "8", "normal"))
        label.pack(ipadx=1)
        self.tipwindow = tw

    def hidetip(self):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()


# ---------------------------------------
# (1) ui section
# ---------------------------------------
class TopicModelingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Topic Modeling Tool")
        self.root.geometry("600x600")

        self.data = None
        self.file_directory = None
        self.file_name = None
        self.iteration_count = 0  # track how many times modeling is run

        self.default_number_of_topics = 0
        self.popups = []

        self.setup_ui()
        self.show_initial_popup()

    def show_initial_popup(self):
        # show initial guidance popup
        msg = config["initial_popup_text"]
        popup = Toplevel(self.root)
        popup.title("Guidance")
        Label(popup, text=msg, justify='left').pack(padx=10, pady=10)
        tk.Button(popup, text="OK", command=popup.destroy).pack(pady=10)

    def setup_ui(self):
        # main frame
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(expand=True)

        # load file button
        self.load_button = tk.Button(self.main_frame, text="Load Data File", command=self.load_data, width=30)
        self.load_button.pack(pady=10)

        # sheet dropdown
        self.sheet_label = tk.Label(self.main_frame, text="Choose a Sheet:")
        self.sheet_label.pack()
        self.sheet_dropdown = ttk.Combobox(self.main_frame, state='disabled', width=28)
        self.sheet_dropdown.pack()
        self.sheet_dropdown.bind("<<ComboboxSelected>>", self.select_sheet)

        # column dropdown
        self.column_label = tk.Label(self.main_frame, text="Select a Column:")
        self.column_label.pack()
        self.column_dropdown = ttk.Combobox(self.main_frame, state='disabled', width=28)
        self.column_dropdown.pack()
        self.column_dropdown.bind("<<ComboboxSelected>>", self.select_column)

        # run topic modeling
        self.analysis_button = tk.Button(self.main_frame, text="Run Topic Modeling",
                                         state='disabled', width=30,
                                         command=self.run_analysis)
        self.analysis_button.pack(pady=10)

        # create wordcloud
        self.wordcloud_button = tk.Button(self.main_frame, text="Create Wordcloud",
                                          state='disabled', width=30,
                                          command=self.create_wordcloud)
        self.wordcloud_button.pack(pady=5)

        # number of topics scale
        self.topics_label = tk.Label(self.main_frame, text="Number of Topics:")
        self.topics_label.pack()
        ToolTip(self.topics_label, text="set the number of topics")
        self.topics_scale = tk.Scale(self.main_frame, from_=0, to=config["max_topics_scale"], orient='horizontal', state='disabled')
        self.topics_scale.pack()

        # filter words button
        self.filter_button = tk.Button(self.main_frame, text="Edit Filter Words", state='disabled', command=self.open_filter_words_window)
        self.filter_button.pack()

        # sentiment analysis placeholder
        self.sentiment_button = tk.Button(self.main_frame, text="Add Sentiment Analysis*",
                                          state='disabled', command=self.sentiment_analysis_placeholder)
        self.sentiment_button.pack(pady=5)

        # iteration count label
        self.iteration_label = tk.Label(self.main_frame, text="Iteration Count: 0")
        self.iteration_label.pack(pady=5)

        # export button
        self.export_button = tk.Button(self.main_frame, text="Export Analysis", state='disabled', width=30, command=self.export_analysis)
        self.export_button.pack(pady=10)

        # new analysis
        self.new_analysis_button = tk.Button(self.main_frame, text="New Analysis", width=30, command=self.new_analysis)
        self.new_analysis_button.pack(pady=20)

    def sentiment_analysis_placeholder(self):
        # placeholder sentiment analysis
        messagebox.showinfo("Info", config["placeholder_sentiment_text"])

    def load_data(self):
        # load data file
        file_path = filedialog.askopenfilename(filetypes=config["allowed_filetypes"])
        if file_path:
            # if a file is loaded, iteration should go back to zero
            self.iteration_count = 0
            self.iteration_label.config(text="Iteration Count: 0")

            self.reset_ui()
            file_ext = os.path.splitext(file_path)[1].lower()
            self.file_directory = os.path.dirname(file_path)
            self.file_name = os.path.basename(file_path)

            try:
                # only xls and xlsx
                if file_ext in [".xlsx", ".xls"]:
                    self.data = pd.ExcelFile(file_path)
                    sheets = self.data.sheet_names
                    self.sheet_dropdown['values'] = sheets
                    self.sheet_dropdown['state'] = 'readonly'
                else:
                    messagebox.showerror("Error", "Only Excel files (.xls, .xlsx) are supported.")
                    return
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load file: {e}")

    def select_sheet(self, event=None):
        # sheet selection
        self.column_dropdown['values'] = list(self.data.parse(self.sheet_dropdown.get()).columns)
        self.column_dropdown['state'] = 'readonly'

    def select_column(self, event=None):
        # column selection
        self.activate_analysis_button()
        self.topics_scale.set(0)

    def activate_analysis_button(self, event=None):
        # enable analysis, wordcloud, sentiment
        self.analysis_button['state'] = 'normal'
        self.wordcloud_button['state'] = 'normal'
        self.sentiment_button['state'] = 'normal'

    def run_analysis(self):
        # run topic modeling
        self.save_filter_words_if_not_exist()
        self.destroy_popups()

        if not self.file_directory or not self.file_name:
            messagebox.showerror("Error", "No file selected.")
            return

        sheet_name = self.sheet_dropdown.get()
        column_name = self.column_dropdown.get()
        number_of_topics = self.topics_scale.get() or self.default_number_of_topics

        prefix_title = config["filter_file_prefix"]
        filter_words_file = f"{prefix_title}_{column_name[:10].replace(' ', '_')}_{datetime.datetime.now().strftime('%Y-%m-%d')}.txt"
        filter_words_file_path = os.path.join(self.file_directory, filter_words_file)

        if not os.path.exists(filter_words_file_path):
            with open(filter_words_file_path, 'w') as file:
                file.write("")

        try:
            r_exe_path = find_r_exe_from_registry()
        except FileNotFoundError as e:
            messagebox.showerror("Error", str(e))
            return

        script_dir = os.path.dirname(os.path.abspath(__file__))
        r_script_path = os.path.join(script_dir, 'TM Single file Viz.R')
        if not os.path.exists(r_script_path):
            messagebox.showerror("Error", f"R script not found at {r_script_path}")
            return

        sheet_name = sheet_name if sheet_name else ""
        command = [
            r_exe_path, r_script_path,
            self.file_directory, self.file_name, sheet_name, column_name, str(number_of_topics), filter_words_file
        ]

        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, stderr = process.communicate()
        
        # print outputs
        print("Standard Output:")
        print(stdout)

        print("Standard Error:")
        print(stderr)

        if process.returncode == 0:
            self.display_output(stdout)
            self.topics_scale['state'] = 'normal'
            self.filter_button['state'] = 'normal'
            self.export_button['state'] = 'normal'
            self.iteration_count += 1
            self.iteration_label.config(text=f"Iteration Count: {self.iteration_count}")
        else:
            messagebox.showerror("Process Failed", f"R script exit code {process.returncode}")

    def display_output(self, output):
        # show r script output
        image_match = re.search(r"TYPE:IMAGE\n(.+?)\nENDOFIMAGE", output, re.DOTALL)
        if image_match:
            base64_data = image_match.group(1).strip()
            self.display_image(base64_data)

        terms_match = re.search(r"TYPE:TOP_TERMS\n(.+?)\nENDOFTERMS", output, re.DOTALL)
        if terms_match:
            json_data = terms_match.group(1).strip()
            self.process_top_terms(json_data)

        text_match = re.search(r"TYPE:TEXT\n(.+?)\nENDOF_TEXT", output, re.DOTALL)
        if text_match:
            text_data = text_match.group(1).strip()
            self.display_text(text_data)

    def process_top_terms(self, json_data):
        # process top terms
        try:
            top_terms_df = pd.read_json(json_data)
            self.visualize_top_terms_bar_chart(top_terms_df)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def visualize_top_terms_bar_chart(self, top_terms_df):
        # bar chart of top terms
        try:
            chart_window = Toplevel(self.root)
            chart_window.title("Top Terms")
            self.popups.append(chart_window)

            topics = sorted(top_terms_df['topic'].unique())
            num_topics = len(topics)
            num_cols = 2
            num_rows = (num_topics + num_cols - 1) // num_cols

            fig, axes = plt.subplots(nrows=num_rows, ncols=num_cols, figsize=(12, 4 * num_rows))
            axes = axes.flatten()
            colors = sns.color_palette(config["bar_chart_colors"], num_topics)

            for idx, topic in enumerate(topics):
                ax = axes[idx]
                topic_terms = top_terms_df[top_terms_df['topic'] == topic].copy()
                topic_terms = topic_terms.sort_values('beta', ascending=False)
                color = colors[idx % len(colors)]
                sns.barplot(data=topic_terms, x='beta', y='term', ax=ax, color=color)
                ax.set_title(f'Topic {topic}')
                ax.set_xlabel('Beta')
                ax.set_ylabel('Term')
                ax.tick_params(axis='y', labelsize=10)

            for idx in range(len(topics), len(axes)):
                fig.delaxes(axes[idx])

            plt.tight_layout()
            canvas = FigureCanvasTkAgg(fig, master=chart_window)
            canvas.draw()
            canvas.get_tk_widget().pack(fill='both', expand=True)

        except Exception as e:
            messagebox.showerror("Error in Bar Chart", str(e))

    def display_image(self, base64_data):
        # display image from base64
        try:
            base64_data += "=" * ((4 - len(base64_data) % 4) % 4)
            image_data = base64.b64decode(base64_data)
            image = Image.open(BytesIO(image_data))
            photo = ImageTk.PhotoImage(image)
            output_window = Toplevel(self.root)
            output_window.title("Image Output")
            self.popups.append(output_window)
            label = Label(output_window, image=photo)
            label.image = photo
            label.pack()
        except Exception as e:
            messagebox.showerror("Image Error", str(e))

    def display_text(self, text_data):
        # display text data
        output_window = Toplevel(self.root)
        output_window.title("Text Output")
        self.popups.append(output_window)
        text_area = scrolledtext.ScrolledText(output_window)
        text_area.pack(fill='both', expand=True)
        text_area.insert('1.0', text_data)
        text_area.config(state='disabled')

    def export_analysis(self):
        # export results
        sheet_name = self.sheet_dropdown.get()
        column_name = self.column_dropdown.get()
        number_of_topics = self.topics_scale.get() or self.default_number_of_topics

        prefix_title = config["filter_file_prefix"]
        filter_words_file = f"{prefix_title}_{column_name[:10].replace(' ', '_')}_{datetime.datetime.now().strftime('%Y-%m-%d')}.txt"
        filter_words_file_path = os.path.join(self.file_directory, filter_words_file)

        if not os.path.exists(filter_words_file_path):
            with open(filter_words_file_path, 'w') as file:
                file.write("")

        try:
            r_exe_path = find_r_exe_from_registry()
        except FileNotFoundError as e:
            messagebox.showerror("Error", str(e))
            return

        script_dir = os.path.dirname(os.path.abspath(__file__))
        export_r_script_path = os.path.join(script_dir, 'TM Single file Export.R')

        if not os.path.exists(export_r_script_path):
            messagebox.showerror("Error", f"R script not found at {export_r_script_path}.")
            return

        sheet_name = sheet_name if sheet_name else ""
        command = [
            r_exe_path, export_r_script_path,
            self.file_directory, self.file_name, sheet_name, column_name, str(number_of_topics),
            filter_words_file
        ]

        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, stderr = process.communicate()
        
        print("Standard Output:")
        print(stdout)

        print("Standard Error:")
        print(stderr)

        if process.returncode == 0:
            messagebox.showinfo("Success", "File saved in the same directory.")
        else:
            messagebox.showerror("Export Failed", f"R script exit code {process.returncode}")

    def open_filter_words_window(self):
        # open filter words window (iterative)
        column_name = self.column_dropdown.get()
        prefix_title = config["filter_file_prefix"]
        file_name = f"{prefix_title}_{column_name[:10].replace(' ', '_')}_{datetime.datetime.now().strftime('%Y-%m-%d')}.txt"
        full_path = os.path.join(self.file_directory, file_name)

        if os.path.exists(full_path):
            with open(full_path, 'r') as file:
                existing_filter_words = [w.strip() for w in file.read().splitlines() if w.strip()]
        else:
            existing_filter_words = []

        # create window
        edit_window = Toplevel(self.root)
        edit_window.title("Edit Filter Words")
        self.popups.append(edit_window)

        # frame
        main_frame = tk.Frame(edit_window)
        main_frame.pack(fill='both', expand=True)

        # filter words area
        text_area_frame = tk.Frame(main_frame)
        text_area_frame.pack(side='left', fill='both', expand=True)

        text_area_label = tk.Label(text_area_frame, text="Filter Words:")
        text_area_label.pack()

        text_area = scrolledtext.ScrolledText(text_area_frame, width=40, height=20)
        text_area.pack(fill='both', expand=True)
        text_area.insert('1.0', "\n".join(existing_filter_words))

        # top words frame
        top_words_frame = tk.Frame(main_frame)
        top_words_frame.pack(side='right', fill='both', expand=True)

        top_words_label = tk.Label(top_words_frame, text="Top Words Not in Filter:")
        top_words_label.pack()

        listbox = tk.Listbox(top_words_frame, selectmode=tk.MULTIPLE, width=30)
        listbox.pack(fill='both', expand=True)

        def get_top_words_not_filtered():
            selected_sheet = self.sheet_dropdown.get()
            selected_column = self.column_dropdown.get()
            try:
                if selected_sheet and selected_sheet in (self.data.sheet_names if hasattr(self.data, 'sheet_names') else []):
                    df = self.data.parse(selected_sheet)
                else:
                    df = self.data

                col_data = df[selected_column].dropna().astype(str)
                text = ' '.join(col_data.tolist())
                words = re.findall(r'\b\w+\b', text.lower())
                all_counts = Counter(words)

                current_filters = [w.strip().lower() for w in text_area.get("1.0", 'end-1c').split('\n') if w.strip()]
                filtered_counts = [(w, c) for w, c in all_counts.most_common() if w not in current_filters]
                return filtered_counts
            except Exception as e:
                messagebox.showerror("Error", f"Error processing top words: {e}")
                return []

        def refresh_top_words():
            listbox.delete(0, tk.END)
            filtered_counts = get_top_words_not_filtered()
            top_n = config["top_words_to_show"]
            top_slice = filtered_counts[:top_n]
            for w, c in top_slice:
                listbox.insert(tk.END, f"{w} ({c})")

        refresh_top_words()

        def add_selected_words():
            filtered_counts = get_top_words_not_filtered()
            top_n = config["top_words_to_show"]
            top_slice = filtered_counts[:top_n]
            selected_indices = listbox.curselection()
            selected_words = [top_slice[i][0] for i in selected_indices]
            existing_text = text_area.get("1.0", 'end-1c')
            existing_words = [w.strip() for w in existing_text.split('\n') if w.strip()]
            updated_words = set(existing_words + selected_words)
            text_area.delete("1.0", tk.END)
            text_area.insert('1.0', "\n".join(updated_words))
            refresh_top_words()

        add_button = tk.Button(top_words_frame, text="Add Selected Words", command=add_selected_words)
        add_button.pack(pady=10)

        def save_changes():
            updated_filter_words = [w.strip() for w in text_area.get("1.0", 'end-1c').split('\n') if w.strip()]
            with open(full_path, 'w') as file:
                file.write("\n".join(updated_filter_words) + '\n')
            messagebox.showinfo("Info", f"Filter words saved to {file_name}")
            edit_window.destroy()

        save_button = tk.Button(edit_window, text="Save", command=save_changes)
        save_button.pack(pady=10)

    def save_filter_words_if_not_exist(self):
        # ensure filter file exists if not
        column_name = self.column_dropdown.get()
        if not column_name:
            return
        prefix_title = config["filter_file_prefix"]
        file_name = f"{prefix_title}_{column_name[:10].replace(' ', '_')}_{datetime.datetime.now().strftime('%Y-%m-%d')}.txt"
        full_path = os.path.join(self.file_directory, file_name)
        if not os.path.exists(full_path):
            with open(full_path, 'w') as file:
                file.write("")

    def new_analysis(self):
        # reset ui for new analysis
        self.reset_ui()
        self.iteration_count = 0
        self.iteration_label.config(text="Iteration Count: 0")

    def reset_ui(self):
        # reset ui states
        self.sheet_dropdown.set('')
        self.sheet_dropdown['state'] = 'disabled'
        self.column_dropdown.set('')
        self.column_dropdown['state'] = 'disabled'
        self.analysis_button['state'] = 'disabled'
        self.wordcloud_button['state'] = 'disabled'
        self.sentiment_button['state'] = 'disabled'
        self.topics_scale.set(0)
        self.topics_scale['state'] = 'disabled'
        self.filter_button['state'] = 'disabled'
        self.export_button['state'] = 'disabled'

    def create_wordcloud(self):
        # create wordcloud
        selected_sheet = self.sheet_dropdown.get()
        selected_column = self.column_dropdown.get()

        try:
            if hasattr(self.data, 'sheet_names') and selected_sheet in self.data.sheet_names:
                data_frame = self.data.parse(selected_sheet)
            else:
                data_frame = self.data

            column_data = data_frame[selected_column].dropna().astype(str)
            text = ' '.join(column_data.tolist())

            prefix_title = config["filter_file_prefix"]
            file_name = f"{prefix_title}_{selected_column[:10].replace(' ', '_')}_{datetime.datetime.now().strftime('%Y-%m-%d')}.txt"
            full_path = os.path.join(self.file_directory, file_name)

            if os.path.exists(full_path):
                with open(full_path, 'r') as file:
                    filter_words = [w.strip().lower() for w in file.read().splitlines() if w.strip()]
            else:
                filter_words = []

            words = re.findall(r'\b\w+\b', text.lower())
            filtered_words = [word for word in words if word not in filter_words]
            filtered_text = ' '.join(filtered_words)

            wordcloud = WordCloud(width=800, height=400, background_color='white').generate(filtered_text)

            output_window = Toplevel(self.root)
            output_window.title("Wordcloud")
            self.popups.append(output_window)

            image = wordcloud.to_image()
            photo = ImageTk.PhotoImage(image)

            label = Label(output_window, image=photo)
            label.image = photo
            label.pack()

            def save_wordcloud():
                file_path = filedialog.asksaveasfilename(defaultextension=".png",
                                                         filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("All files", "*.*")])
                if file_path:
                    image.save(file_path)
                    messagebox.showinfo("Success", f"Wordcloud saved to {file_path}")

            save_button = tk.Button(output_window, text="Save Wordcloud", command=save_wordcloud)
            save_button.pack(pady=10)

        except Exception as e:
            messagebox.showerror("Wordcloud Error", f"Error generating wordcloud: {e}")

    def destroy_popups(self):
        # destroy all popups
        for popup in self.popups:
            popup.destroy()
        self.popups = []


def main():
    root = tk.Tk()
    app = TopicModelingApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()