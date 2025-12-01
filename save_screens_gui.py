import os
import sys
import json
import threading
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(SCRIPT_DIR, 'save_screens_setup.json')

def load_config():
    try:
        with open(CONFIG_PATH, 'r') as f:
            return json.load(f)
    except Exception:
        return {}

def save_config(cfg):
    with open(CONFIG_PATH, 'w') as f:
        json.dump(cfg, f)

class SaveScreensGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Save Screens - GUI')
        self.geometry('640x420')

        self.config_data = load_config()

        # Top frame: folder and image id
        top = ttk.Frame(self)
        top.pack(fill='x', padx=8, pady=6)

        ttk.Label(top, text='Save folder:').grid(row=0, column=0, sticky='w')
        self.folder_var = tk.StringVar(value=self.config_data.get('folder', ''))
        folder_entry = ttk.Entry(top, textvariable=self.folder_var, width=50)
        folder_entry.grid(row=0, column=1, padx=6)
        ttk.Button(top, text='Browse', command=self.browse_folder).grid(row=0, column=2)
        ttk.Button(top, text='Open', command=self.open_folder).grid(row=0, column=3, padx=4)

        ttk.Label(top, text='Filename pattern:').grid(row=1, column=0, sticky='w', pady=(6,0))
        self.pattern_var = tk.StringVar(value=self.config_data.get('pattern', '{id}'))
        pattern_entry = ttk.Entry(top, textvariable=self.pattern_var, width=50)
        pattern_entry.grid(row=1, column=1, padx=6)
        ttk.Button(top, text='Save Pattern', command=self.save_pattern).grid(row=1, column=2)
        ttk.Label(top, text='Use {id} and {timestamp}').grid(row=1, column=3, padx=4)

        ttk.Label(top, text='Image ID:').grid(row=2, column=0, sticky='w', pady=(6,0))
        self.id_var = tk.StringVar(value=str(self.config_data.get('image_id', 'N/A')))
        ttk.Label(top, textvariable=self.id_var).grid(row=2, column=1, sticky='w', pady=(6,0))

        # Buttons
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill='x', padx=8, pady=6)

        ttk.Button(btn_frame, text='Save Clipboard', command=self.run_save).pack(side='left')
        ttk.Button(btn_frame, text='Refresh Counter', command=self.run_refresh).pack(side='left', padx=6)
        ttk.Button(btn_frame, text='Reload Config', command=self.reload_config).pack(side='left')

        # Status and log
        status_frame = ttk.Frame(self)
        status_frame.pack(fill='both', expand=True, padx=8, pady=6)

        ttk.Label(status_frame, text='Status / Output:').pack(anchor='w')
        self.log = ScrolledText(status_frame, height=12)
        self.log.pack(fill='both', expand=True)

        self.protocol('WM_DELETE_WINDOW', self.on_close)

    def browse_folder(self):
        path = filedialog.askdirectory(initialdir=self.folder_var.get() or SCRIPT_DIR)
        if path:
            self.folder_var.set(path)
            # update config
            cfg = load_config()
            cfg['folder'] = path
            # also persist current pattern if present
            if self.pattern_var.get():
                cfg['pattern'] = self.pattern_var.get()
            save_config(cfg)
            self.config_data = cfg
            self.id_var.set(str(cfg.get('image_id', 'N/A')))
            self.append_log(f'Folder set to: {path}\n')

    def save_pattern(self):
        pattern = self.pattern_var.get().strip()
        if not pattern:
            messagebox.showerror('Error', 'Pattern cannot be empty')
            return
        cfg = load_config()
        cfg['pattern'] = pattern
        # ensure image_id exists
        cfg.setdefault('image_id', 1)
        save_config(cfg)
        self.config_data = cfg
        self.append_log(f'Pattern saved: {pattern}\n')

    def open_folder(self):
        path = self.folder_var.get() or SCRIPT_DIR
        if not os.path.exists(path):
            messagebox.showerror('Error', f'Folder does not exist:\n{path}')
            return
        if sys.platform.startswith('win'):
            subprocess.Popen(['explorer', path])
        else:
            subprocess.Popen(['xdg-open', path])

    def append_log(self, text):
        self.log.insert('end', text)
        self.log.see('end')

    def run_in_thread(self, target, *args, **kwargs):
        thread = threading.Thread(target=target, args=args, kwargs=kwargs)
        thread.daemon = True
        thread.start()

    def run_save(self):
        self.run_in_thread(self._run_script, 'save_screens_to_folder.py')

    def run_refresh(self):
        self.run_in_thread(self._run_script, 'save_screens_refresh.py')

    def _run_script(self, script_name):
        self.append_log(f'Running: {script_name}\n')
        script_path = os.path.join(SCRIPT_DIR, script_name)
        if not os.path.exists(script_path):
            self.append_log(f'ERROR: Script not found: {script_path}\n')
            return

        try:
            # Use same Python executable
            proc = subprocess.run([sys.executable, script_path], cwd=SCRIPT_DIR, capture_output=True, text=True, timeout=60)
            if proc.stdout:
                self.append_log(proc.stdout)
            if proc.stderr:
                self.append_log(proc.stderr)
            self.append_log(f'Process exited with code {proc.returncode}\n')
        except subprocess.TimeoutExpired:
            self.append_log('ERROR: Process timed out.\n')
        except Exception as e:
            self.append_log(f'ERROR: {e}\n')

        # reload config to update image id
        try:
            cfg = load_config()
            self.config_data = cfg
            self.id_var.set(str(cfg.get('image_id', 'N/A')))
        except Exception:
            pass

    def reload_config(self):
        cfg = load_config()
        self.config_data = cfg
        self.folder_var.set(cfg.get('folder', ''))
        self.id_var.set(str(cfg.get('image_id', 'N/A')))
        self.append_log('Config reloaded.\n')

    def on_close(self):
        self.destroy()

if __name__ == '__main__':
    app = SaveScreensGUI()
    app.mainloop()