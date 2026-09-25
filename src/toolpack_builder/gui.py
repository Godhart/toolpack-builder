from __future__ import annotations
import json, queue, threading
from pathlib import Path
import traceback


def main() -> None:
    try:
        import customtkinter as ctk
    except ImportError as exc:
        raise SystemExit(
            "CustomTkinter could not be imported by this Python interpreter.\n"
            f"Python: {__import__('sys').executable}\n"
            "Install it into the same interpreter with:\n"
            f"  {__import__('sys').executable} -m pip install 'toolpack-builder[gui]'\n"
            f"Original error: {exc}"
        ) from exc
    try:
        import tkinter
        from tkinter import filedialog as tk_filedialog, messagebox as tk_messagebox
    except ImportError as exc:
        raise SystemExit(
            "Python tkinter is not available. It is an OS/Python component, not a pip extra.\n"
            "On Debian/Ubuntu install it with: sudo apt install python3-tk\n"
            f"Python: {__import__('sys').executable}\n"
            f"Original error: {exc}"
        ) from exc
    from .builder import BuildConfig, build_from_report, scan
    from .project import ProjectConfig, default_project_path, settings_path

    class App(ctk.CTk):
        def __init__(self):
            super().__init__(); self.title("ToolPack Builder 0.3.1"); self.geometry("1120x760"); self.minsize(900,650)
            self.q=queue.Queue(); self.report=None; self.scan_fp=None; self.payload=None; self.project_path=default_project_path()
            self.project=ProjectConfig.load(self.project_path) if self.project_path.exists() else ProjectConfig()
            self._ui(); self._load_settings(); self.after(100,self._poll); self.protocol("WM_DELETE_WINDOW",self._close)
        def _ui(self):
            self.grid_columnconfigure(0,weight=1); self.grid_rowconfigure(3,weight=1)
            src=ctk.CTkFrame(self); src.grid(row=0,column=0,padx=12,pady=(12,6),sticky="ew"); src.grid_columnconfigure(1,weight=1)
            self.source=self._row(src,0,"Scan path",self.project.source,self._browse_source)
            self.include=self._row(src,1,"Include",self.project.include)
            self.exclude=self._row(src,2,"Exclude (one per line)","; ".join(self.project.excludes))
            out=ctk.CTkFrame(self); out.grid(row=1,column=0,padx=12,pady=6,sticky="ew"); out.grid_columnconfigure(1,weight=1)
            self.output=self._row(out,0,"Output",self.project.output,self._browse_output)
            self.category=self._row(out,1,"Category",self.project.category_name)
            ctk.CTkLabel(out,text="Category mode").grid(row=2,column=0,padx=10,pady=8,sticky="w"); self.mode=ctk.CTkOptionMenu(out,values=["single","directories"],command=lambda _:self._dirty()); self.mode.set(self.project.category_mode); self.mode.grid(row=2,column=1,padx=10,pady=8,sticky="w")
            actions=ctk.CTkFrame(self,fg_color="transparent"); actions.grid(row=2,column=0,padx=12,pady=6,sticky="ew")
            self.scan_btn=ctk.CTkButton(actions,text="Scan",command=self._scan); self.scan_btn.pack(side="left")
            self.build_btn=ctk.CTkButton(actions,text="Build ToolPack",command=self._build,state="disabled"); self.build_btn.pack(side="left",padx=8)
            ctk.CTkButton(actions,text="Save project",command=self._save_project).pack(side="left",padx=8)
            self.progress=ctk.CTkProgressBar(actions); self.progress.set(0); self.progress.pack(side="right",fill="x",expand=True,padx=(30,0))
            self.tabs=ctk.CTkTabview(self); self.tabs.grid(row=3,column=0,padx=12,pady=6,sticky="nsew")
            for n in ("Tools","Report","ToolPack"): self.tabs.add(n)
            self.tools=ctk.CTkTextbox(self.tabs.tab("Tools")); self.tools.pack(fill="both",expand=True,padx=6,pady=6)
            self.report_box=ctk.CTkTextbox(self.tabs.tab("Report")); self.report_box.pack(fill="both",expand=True,padx=6,pady=6)
            self.pack_box=ctk.CTkTextbox(self.tabs.tab("ToolPack")); self.pack_box.pack(fill="both",expand=True,padx=6,pady=6)
            self.status=ctk.CTkLabel(self,text="Not scanned",anchor="w"); self.status.grid(row=4,column=0,padx=16,pady=(0,10),sticky="ew")
            for e in (self.source,self.include,self.exclude,self.output,self.category): e.bind("<KeyRelease>",lambda _e:self._dirty())
        def _row(self,parent,row,label,value,browse=None):
            ctk.CTkLabel(parent,text=label).grid(row=row,column=0,padx=10,pady=8,sticky="w"); e=ctk.CTkEntry(parent); e.insert(0,value); e.grid(row=row,column=1,padx=10,pady=8,sticky="ew")
            if browse: ctk.CTkButton(parent,text="…",width=40,command=browse).grid(row=row,column=2,padx=(0,10),pady=8)
            return e
        def _cfg(self):
            ex=tuple(x.strip() for x in self.exclude.get().replace("\n",";").split(";") if x.strip())
            return BuildConfig(Path(self.source.get()).expanduser(),self.include.get().strip() or "**/*.py",ex,category_name=self.category.get().strip() or None,category_mode=self.mode.get())
        def _dirty(self):
            try: fresh=self.scan_fp==self._cfg().fingerprint()
            except Exception: fresh=False
            self.build_btn.configure(state="normal" if self.report is not None and fresh else "disabled")
            if self.report is not None and not fresh: self.status.configure(text="⚠ Scan results are outdated — scan again")
        def _browse_source(self):
            v=tk_filedialog.askdirectory(initialdir=self.source.get() or None)
            if v: self.source.delete(0,"end"); self.source.insert(0,v); self._dirty()
        def _browse_output(self):
            v=tk_filedialog.asksaveasfilename(defaultextension=".toolpack",filetypes=[("ToolPack","*.toolpack"),("All files","*")])
            if v: self.output.delete(0,"end"); self.output.insert(0,v); self._dirty()
        def _event(self,e): self.q.put(("event",e))
        def _scan(self):
            try: cfg=self._cfg()
            except Exception as e: return tk_messagebox.showerror("Configuration",str(e))
            self.scan_btn.configure(state="disabled"); self.build_btn.configure(state="disabled"); self.status.configure(text="Scanning…"); self.progress.set(0)
            def work():
                try: self.q.put(("scan",scan(cfg,self._event),cfg.fingerprint()))
                except Exception as e: self.q.put(("error",e))
            threading.Thread(target=work,daemon=True).start()
        def _build(self):
            cfg=self._cfg(); out=Path(self.output.get()).expanduser()
            if not str(out): return tk_messagebox.showerror("Output","Choose output path")
            self.build_btn.configure(state="disabled"); self.status.configure(text="Building…")
            def work():
                try: self.q.put(("build",build_from_report(cfg,self.report,out,self._event)))
                except Exception as e: self.q.put(("error",e))
            threading.Thread(target=work,daemon=True).start()
        def _poll(self):
            try:
                while True:
                    m=self.q.get_nowait(); kind=m[0]
                    if kind=="event":
                        e=m[1]; self.status.configure(text=e.message or e.kind)
                        if e.total: self.progress.set(e.current/e.total)
                    elif kind=="scan":
                        self.report,self.scan_fp=m[1],m[2]; self.scan_btn.configure(state="normal"); self._render_report(); self._dirty()
                    elif kind=="build":
                        self.payload=m[1].payload; self.scan_btn.configure(state="normal"); self._render_pack(); self.status.configure(text=f"Built {self.output.get()}"); self._dirty()
                    elif kind=="error": self.scan_btn.configure(state="normal"); tk_messagebox.showerror("ToolPack Builder",str(m[1])); self._dirty()
            except queue.Empty: pass
            self.after(100,self._poll)
        def _render_report(self):
            self.tools.delete("1.0","end"); self.report_box.delete("1.0","end")
            for x in self.report.items:
                name=x.spec.declared_name if x.spec else "-"; rel=x.path.relative_to(self.report.root); self.tools.insert("end",f"{'✓' if x.status=='valid' else '✗'}  {name:24} {rel}  {x.message}\n")
            txt=f"Root: {self.report.root}\nFound: {len(self.report.items)}\nReady: {len(self.report.valid)}\nFailed: {len(self.report.failed)}\n\n"
            for x in self.report.failed: txt+=f"FAILED {x.path.relative_to(self.report.root)}\n{x.message}\n\n"
            self.report_box.insert("end",txt); self.status.configure(text=f"Scan complete: {len(self.report.valid)} ready, {len(self.report.failed)} failed")
        def _render_pack(self):
            self.pack_box.delete("1.0","end"); self.pack_box.insert("end",json.dumps(self.payload,ensure_ascii=False,indent=2)); self.tabs.set("ToolPack")
        def _save_project(self):
            self.project=ProjectConfig(self.source.get(),self.include.get(),[x.strip() for x in self.exclude.get().split(";") if x.strip()],self.output.get(),self.mode.get(),self.category.get()); self.project.save(self.project_path); self.status.configure(text=f"Project saved: {self.project_path}")
        def _load_settings(self):
            try:
                s=json.loads(settings_path().read_text()); ctk.set_appearance_mode(s.get("appearance","System")); self.geometry(s.get("geometry","1120x760"))
            except Exception: ctk.set_appearance_mode("System")
        def _close(self):
            self._save_project(); p=settings_path(); p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps({"appearance":"System","geometry":self.geometry()},indent=2)+"\n"); self.destroy()
    App().mainloop()

if __name__ == "__main__": main()
