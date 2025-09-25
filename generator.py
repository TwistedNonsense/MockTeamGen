# generator.py

# Simple GUI to run teams/venues/users/events generators.

import os
import sys
import re
import threading
import queue
from pathlib import Path
import importlib.util
import subprocess
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

HERE = Path(__file__).resolve().parent
ROLES = ["Team Admin", "Coach", "Assistant Coach", "Venue Admin", "Event Admin","Other"]

def _try_import_module(mod_name: str, file_name: str):
    p = HERE / file_name
    if not p.exists():
        return None
    spec = importlib.util.spec_from_file_location(mod_name, str(p))
    if not spec or not spec.loader:
        return None
    mod = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(mod)  # type: ignore[attr-defined]
        return mod
    except Exception:
        return None

def _preferred_callable(mod, names):
    for n in names:
        fn = getattr(mod, n, None)
        if callable(fn):
            return fn
    return None

def _run_stream(cmd, on_line):
    proc = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1
    )
    for line in proc.stdout:  # type: ignore[union-attr]
        on_line(line.rstrip("\n"))
    return proc.wait()

def _humanize_log_line(line: str) -> str:
    s = line
    # Step starts
    s = re.sub(r"^\[teams] starting…$", "▶ Starting mock team generation…", s)
    s = re.sub(r"^\[venues] starting…$", "▶ Starting mock venue generation…", s)
    s = re.sub(r"^\[users] starting…$", "▶ Starting mock user generation…", s)
    s = re.sub(r"^\[events] starting…$", "▶ Starting mock event generation…", s)
    s = re.sub(r"^\[players] starting…$", "▶ Starting mock player generation…", s)
    # Generator summaries
    s = re.sub(r"^Wrote (\d+) teams to (.+)$", r"✔ Successfully generated \1 mock teams. Saved to \2", s)
    s = re.sub(r"^Wrote (\d+) venues to (.+)$", r"✔ Successfully generated \1 mock venues. Saved to \2", s)
    s = re.sub(r"^Wrote (\d+) users to (.+)$", r"✔ Successfully generated \1 mock users. Saved to \2", s)
    s = re.sub(r"^Wrote (\d+) events to (.+)$", r"✔ Successfully generated \1 mock events. Saved to \2", s)
    s = re.sub(r"^Wrote (\d+) event-team rows to (.+)$", r"Linked \1 teams to events. Join table saved to \2", s)
    s = re.sub(r"^Wrote (\d+) players to (.+)$", r"✔ Successfully generated \1 mock players. Saved to \2", s)
    if re.search(r"\berror\b", s, flags=re.I):
        s = f"❌ {s}"
    return s

# runners 
def run_teams(teams_count: int, output_dir: str, on_line):
    script = HERE / "generate_mock_teams.py"
    if not script.exists():
        on_line("[teams] ERROR: generate_mock_teams.py not found")
        return 1

    teams_out = str(Path(output_dir) / "mock_teams.csv")
    cmd = [
        sys.executable, str(script),
        "--num-teams", str(teams_count),
        "--out", teams_out,
    ]
    return _run_stream(cmd, on_line)

def run_users(output_dir: str, users_count: int | None, roles: list[str], include_passwords: bool = False, on_line=None):
    script = HERE / "generate_mock_users.py"
    if not script.exists():
        if on_line: on_line("[users] ERROR: generate_mock_users.py not found")
        return 1
    teams_csv = str(Path(output_dir) / "mock_teams.csv")
    out_csv = str(Path(output_dir) / "mock_users.csv")
    roles_arg = ",".join(roles)
    cmd = [
        sys.executable, str(script),
        "--teams-csv", teams_csv,
        "--out", out_csv,
        "--roles", roles_arg,
    ]
    if include_passwords:
        cmd.append("--include-passwords")
    return _run_stream(cmd, on_line or (lambda s: None))

def run_venues(output_dir: str, on_line):
    script = HERE / "generate_mock_venues.py"
    if not script.exists():
        on_line("[venues] ERROR: generate_mock_venues.py not found"); return 1
    teams_csv = str(Path(output_dir)/"mock_teams.csv")
    venues_out = str(Path(output_dir)/"mock_venues.csv")
    cmd=[sys.executable,str(script),"--teams-csv",teams_csv,"--out",venues_out]
    return _run_stream(cmd,on_line or (lambda s: None))

def run_events(output_dir: str, events_count: int, teams_per_event: int, on_line=None):
    mod = _try_import_module("generate_mock_events", "generate_mock_events.py")
    fn = _preferred_callable(mod, ["generate", "main", "run"]) if mod else None
    if fn:
        try:
            if on_line: on_line("[events] callable detected; falling back to CLI to ensure file paths are honored")
        except Exception:
            pass  # we’ll use subprocess to guarantee filenames

    script = HERE / "generate_mock_events.py"
    if not script.exists():
        if on_line: on_line("[events] ERROR: generate_mock_events.py not found")
        return 1

    teams_csv = str(Path(output_dir) / "mock_teams.csv")
    venues_csv = str(Path(output_dir) / "mock_venues.csv")
    events_out = str(Path(output_dir) / "mock_events.csv")
    join_out = str(Path(output_dir) / "mock_events-teams.csv")

    cmd = [
        sys.executable, str(script),
        "--teams-csv", teams_csv,
        "--venues-csv", venues_csv,
        "--events-out", events_out,
        "--join-out", join_out,
        "--num-events", str(events_count),
        "--teams-per-event", str(teams_per_event),
    ]
    return _run_stream(cmd, on_line or (lambda s: None))

def run_players(output_dir: str, players_per_team: int, age_min: int, age_max: int, on_line=None):
    script = HERE / "generate_mock_players.py"
    if not script.exists():
        if on_line: on_line("[players] ERROR: generate_mock_players.py not found")
        return 1
    teams_csv = str(Path(output_dir) / "mock_teams.csv")
    out_csv = str(Path(output_dir) / "mock_players.csv")
    cmd = [
        sys.executable, str(script),
        "--teams-csv", teams_csv,
        "--out", out_csv,
        "--players-per-team", str(players_per_team),
        "--age-min", str(age_min),
        "--age-max", str(age_max),
        "--start-id", "7001",
    ]
    return _run_stream(cmd, on_line or (lambda s: None))

# GUI 
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Mock Team Data Generator")
        self.geometry("600x850")
        self.minsize(600, 800)  # Minimum size to ensure all elements are visible

        # state
        self.output_dir = tk.StringVar(value=str(HERE))
        self.teams_count = tk.IntVar(value=50)
        self.users_count = tk.IntVar(value=200)  # not used by CLI but kept for parity
        self.events_count = tk.IntVar(value=20)
        self.teams_per_event = tk.IntVar(value=2)
        self.players_per_team = tk.IntVar(value=20)
        self.role_vars = {role: tk.BooleanVar(value=True) for role in ROLES}
        self.include_passwords = tk.BooleanVar(value=False)  

        self.run_teams_var = tk.BooleanVar(value=True)
        self.run_users_var = tk.BooleanVar(value=True)
        self.run_events_var = tk.BooleanVar(value=True)
        self.run_venues_var = tk.BooleanVar(value=True)
        self.run_players_var = tk.BooleanVar(value=True)

        self.age_min = tk.IntVar(value=18)
        self.age_max = tk.IntVar(value=22)

        self._build_ui()

        self.log_queue = queue.Queue()
        self.after(50, self._drain_log)

    # UI build 
    def _build_ui(self):
        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True, padx=10, pady=10)
        style = ttk.Style(self)
        style.configure("Compact.TSpinbox", padding=(2, 1, 2, 1))  # left, top, right, bottom

        options = ttk.Frame(nb)
        logtab = ttk.Frame(nb)
        nb.add(options, text="Options")
        nb.add(logtab, text="Log")

        # Options tab
        self._build_options(options)

        # Log tab
        lf = ttk.LabelFrame(logtab, text="Run log")
        lf.pack(fill="both", expand=True, padx=12, pady=12)
        self.log = tk.Text(lf, height=20, wrap="word", state="disabled")
        self.log.pack(fill="both", expand=True, padx=8, pady=8)

    def _build_options(self, parent):
        # Output dir
        outf = ttk.LabelFrame(parent, text="Output")
        outf.pack(fill="x", padx=12, pady=(12, 8))
        e = ttk.Entry(outf, textvariable=self.output_dir)
        e.pack(side="left", fill="x", expand=True, padx=(12, 6), pady=12)
        ttk.Button(outf, text="Browse…", command=self._pick_folder).pack(side="left", padx=(6, 12), pady=12)

        # Teams (always generated, no checkbox)
        tf = ttk.LabelFrame(parent, text="Teams")
        tf.pack(fill="x", padx=12, pady=8)
        ttk.Label(tf, text="Number of teams to generate:").grid(row=0, column=0, sticky="w", padx=12, pady=(10, 6))
        self.sb_teams = ttk.Spinbox(tf, from_=1, to=9999, textvariable=self.teams_count, width=6)
        self.sb_teams.grid(row=0, column=1, sticky="w", padx=(0, 12), pady=(10, 6))

        tf.grid_columnconfigure(3, weight=1)

        # Venues
        vf = ttk.LabelFrame(parent, text="Venues")
        vf.pack(fill="x", padx=12, pady=8)
        ttk.Checkbutton(vf,text="Generate venues",variable=self.run_venues_var,command=self._toggle_states)\
            .grid(row=0,column=0,sticky="w",padx=12,pady=(10,6))
#        ttk.Label(vf,text="(Each team will get a venue)").grid(row=1,column=0,sticky="w",padx=12,pady=(0,8))
        
        # Users
        uf = ttk.LabelFrame(parent, text="Users")
        uf.pack(fill="x", padx=12, pady=8, ipady=5)
        
        # Configure grid weights for even column distribution
        for i in range(3):
            uf.columnconfigure(i, weight=1, uniform='role_cols')
        
        # First row - Generate users checkbox
        ttk.Checkbutton(uf, text="Generate users", variable=self.run_users_var, 
                       command=self._toggle_states).grid(row=0, column=0, columnspan=3, 
                                                      sticky="w", padx=12, pady=(5, 2))
        
        # Second row - Password checkbox
        ttk.Checkbutton(uf, text="Include passwords (with bcrypt hashes)",
                       variable=self.include_passwords).grid(row=1, column=0, columnspan=3, 
                                                          sticky="w", padx=24, pady=2)
        
        # Third row - Roles label
        ttk.Label(uf, text="Select roles to generate:").grid(row=2, column=0, columnspan=3, 
                                                           sticky="w", padx=12, pady=(5, 5))
        
        # Role checkboxes in 3 columns with even spacing
        for i, role in enumerate(ROLES):
            row = 3 + (i // 3)
            col = i % 3
            ttk.Checkbutton(uf, text=role, variable=self.role_vars[role], 
                           command=self._toggle_states).grid(
                               row=row, column=col, 
                               sticky="w", padx=12, pady=2)

        # Events
        ef = ttk.LabelFrame(parent, text="Events")
        ef.pack(fill="x", padx=12, pady=8)
        ttk.Checkbutton(ef, text="Generate events", variable=self.run_events_var, command=self._toggle_states)\
            .grid(row=0, column=0, sticky="w", padx=12, pady=(10, 6))
        ttk.Label(ef, text="Number of events:").grid(row=1, column=0, sticky="w", padx=(12, 6), pady=(0,8))
        self.sb_events = ttk.Spinbox(ef, from_=1, to=9999, textvariable=self.events_count,
                                    width=6, style="Compact.TSpinbox")
        self.sb_events.grid(row=1, column=1, sticky="w", padx=(0, 20), pady=(0,8))
        ttk.Label(ef, text="Teams per event:").grid(row=1, column=2, sticky="w", padx=(12, 6), pady=(0,8))
        self.sb_tpe = ttk.Spinbox(ef, from_=1, to=64, textvariable=self.teams_per_event,
                                width=6, style="Compact.TSpinbox")
        self.sb_tpe.grid(row=1, column=3, sticky="w", padx=(0, 12), pady=(0,8))
        ef.grid_columnconfigure(4, weight=1)

        # Players
        pf = ttk.LabelFrame(parent, text="Players")
        pf.pack(fill="x", padx=12, pady=8)
        self.run_players_var = tk.BooleanVar(value=True)
        self.players_per_team = tk.IntVar(value=20)
        self.age_min = tk.IntVar(value=18)
        self.age_max = tk.IntVar(value=22)
        ttk.Checkbutton(pf, text="Generate players", variable=self.run_players_var,
                        command=self._toggle_states).grid(row=0, column=0, sticky="w", padx=12, pady=(10, 6))
        
        ttk.Label(pf, text="Players per team:").grid(row=1, column=0, sticky="w", padx=(12, 6), pady=2)
        self.sb_ppt = ttk.Spinbox(pf, from_=0, to=200, textvariable=self.players_per_team,
                                width=6, style="Compact.TSpinbox")
        self.sb_ppt.grid(row=1, column=1, sticky="w", padx=(0, 20), pady=2)
        
        ttk.Label(pf, text="Age min:").grid(row=2, column=0, sticky="w", padx=(12, 6), pady=2)
        self.sb_age_min = ttk.Spinbox(pf, from_=10, to=60, textvariable=self.age_min,
                                    width=6, style="Compact.TSpinbox")
        self.sb_age_min.grid(row=2, column=1, sticky="w", padx=(0, 20), pady=2)
        
        ttk.Label(pf, text="Age max:").grid(row=2, column=2, sticky="w", padx=(12, 6), pady=2)
        self.sb_age_max = ttk.Spinbox(pf, from_=10, to=60, textvariable=self.age_max,
                                    width=6, style="Compact.TSpinbox")
        self.sb_age_max.grid(row=2, column=3, sticky="w", padx=(0, 12), pady=2)
        pf.grid_columnconfigure(4, weight=1)

        # Run button at bottom
        runbar = ttk.Frame(parent)
        runbar.pack(fill="x", padx=12, pady=(10, 14))
        self.run_btn = ttk.Button(runbar, text="Run selected", command=self._on_run)
        self.run_btn.pack(side="left")
        ttk.Button(runbar, text="Open output folder", command=self._open_output).pack(side="left", padx=8)

        # Status
        self.status_label = ttk.Label(parent, text="", anchor="w", font=("TkDefaultFont", 10, "bold"))
        self.status_label.pack(fill="x", padx=12, pady=(0, 8))
        
        self._toggle_states()

    # state helpers 
    def _toggle_states(self):
        # Enable/disable inputs based on checkboxes
        for w, flag in [
            (self.sb_teams, self.run_teams_var.get()),
            (self.sb_events, self.run_events_var.get()),
            (self.sb_tpe, self.run_events_var.get()),
            (getattr(self, "sb_ppt", None), getattr(self, "run_players_var", tk.BooleanVar(value=True)).get()),
            (getattr(self, "sb_age_min", None), getattr(self, "run_players_var", tk.BooleanVar(value=True)).get()),
            (getattr(self, "sb_age_max", None), getattr(self, "run_players_var", tk.BooleanVar(value=True)).get()),
        ]:
            if w:
                try: w.configure(state=("normal" if flag else "disabled"))
                except tk.TclError: pass

    def _pick_folder(self):
        path = filedialog.askdirectory(initialdir=self.output_dir.get() or str(HERE))
        if path:
            self.output_dir.set(path)

    # logging 
    def _append_log(self, line: str):
        """UI-thread writer. Do not call directly; use _enqueue_log."""
        self.log.configure(state="normal")
        self.log.insert("end", line + "\n")
        self.log.see("end")
        self.log.configure(state="disabled")

    def _enqueue_log(self, line: str):
        self.log_queue.put(_humanize_log_line(line))

    def _drain_log(self):
        try:
            while True:
                self._append_log(self.log_queue.get_nowait())
        except queue.Empty:
            pass
        self.after(50, self._drain_log)

    # actions 
    def _on_run(self):
        outdir = Path(self.output_dir.get()).expanduser().resolve()
        try:
            outdir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            messagebox.showerror("Error", f"Cannot create output directory:\n{e}")
            return

        plan = [
            ("teams", run_teams, dict(teams_count=self.teams_count.get(),
                                     output_dir=str(outdir)))
        ]
        if getattr(self, "run_venues_var", tk.BooleanVar(value=True)).get():
            plan.append(("venues", run_venues, dict(output_dir=str(outdir))))

        if self.run_users_var.get():
            selected_roles = [role for role, var in self.role_vars.items() if var.get()]
            plan.append(("users", run_users, dict(output_dir=str(outdir),
                                          users_count=self.users_count.get(),
                                          roles=selected_roles,
                                          include_passwords=self.include_passwords.get())))
        if self.run_events_var.get():
            plan.append(("events", run_events, dict(output_dir=str(outdir),
                                                    events_count=self.events_count.get(),
                                                    teams_per_event=self.teams_per_event.get())))

        if self.run_players_var.get():
            plan.append(("players", run_players, dict(
                output_dir=str(outdir),
                players_per_team=self.players_per_team.get(),
                age_min=self.age_min.get(),
                age_max=self.age_max.get(),
            )))

        if not plan:
            messagebox.showinfo("Nothing to run", "Select at least one generator.")
            return

        self.run_btn.configure(state="disabled")
        self._enqueue_log("╔══════════════════════════════════════╗")
        self._enqueue_log("║     Mock data generation started     ║")
        self._enqueue_log("╚══════════════════════════════════════╝")

        def worker():
            rc_total = 0

            friendly_name = {
                "teams": "teams",
                "venues": "venues",
                "users": "users",
                "events": "events",
                "players": "players",
            }
            start_msg = {
                "teams":  "┣━━━ Starting mock team generation  ━━━┫",
                "venues": "┣━━━ Starting mock venue generation ━━━┫",
                "users":  "┣━━━ Starting mock user generation  ━━━┫",
                "events": "┣━━━ Starting mock event generation ━━━┫",
                "players": "┣━━━ Starting mock player generation ━━━┫",
            }

            for name, fn, kwargs in plan:
                self._enqueue_log(start_msg.get(name, f"▶ Starting {friendly_name.get(name, name)}…"))

                def on_line(s): self._enqueue_log(s)

                try:
                    rc = fn(on_line=on_line, **kwargs)
                except TypeError:
                    rc = fn(**kwargs)  # fallback if runner lacks on_line

                if (rc or 0) == 0:
                    self._enqueue_log(f"✔ Finished {friendly_name.get(name, name)}.")
                else:
                    self._enqueue_log(f"❌ {friendly_name.get(name, name).capitalize()} failed. Exit code {rc}")
                rc_total |= (rc or 0)

            # Summary block
            ok = (rc_total == 0)
            self._enqueue_log("╔══════════════════════════════════════╗")
            self._enqueue_log(("║   All tasks completed successfully   ║" if ok
                        else   "║         Finished with errors         ║"))
            self._enqueue_log("╚══════════════════════════════════════╝")
            
            result_text = "Generation completed successfully" if rc_total == 0 else "Generation finished with errors"
            color = "green" if rc_total == 0 else "red"
            self.status_label.after(0, lambda: self.status_label.configure(text=result_text, foreground=color))
            self.run_btn.configure(state="normal")

        threading.Thread(target=worker, daemon=True).start()

    def _open_output(self):
        outdir = Path(self.output_dir.get()).expanduser().resolve()
        if sys.platform.startswith("darwin"):
            subprocess.call(["open", str(outdir)])
        elif os.name == "nt":
            os.startfile(str(outdir))  # type: ignore[attr-defined]
        else:
            subprocess.call(["xdg-open", str(outdir)])

if __name__ == "__main__":
    App().mainloop()
