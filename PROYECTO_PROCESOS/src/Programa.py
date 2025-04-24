import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.patches as patches
from matplotlib.animation import FuncAnimation
import json
import numpy as np
from collections import deque

# Configuración para evitar errores de icono
mpl.rcParams['toolbar'] = 'None'

class EnhancedProcessSchedulingSimulator:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulador de Planificación de Procesos")
        self.root.geometry("1400x900")
        
        self.processes = []
        self.current_id = 1
        self.algorithm = "FCFS"
        self.quantum = 2
        self.animation = None
        self.animation_running = False
        
        self.setup_ui()
        
    def setup_ui(self):
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        left_panel = ttk.Frame(main_frame, width=450)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        
        right_panel = ttk.Frame(main_frame)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.setup_input_panel(left_panel)
        self.setup_output_panel(right_panel)
    
    def setup_input_panel(self, parent):
        process_frame = ttk.LabelFrame(parent, text="Entrada de Procesos")
        process_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(process_frame, text="ID:").grid(row=0, column=0, padx=5, pady=2, sticky=tk.W)
        self.id_entry = ttk.Entry(process_frame, width=10)
        self.id_entry.grid(row=0, column=1, padx=5, pady=2, sticky=tk.W)
        self.id_entry.insert(0, "1")
        
        ttk.Label(process_frame, text="Tiempo de llegada:").grid(row=1, column=0, padx=5, pady=2, sticky=tk.W)
        self.arrival_entry = ttk.Entry(process_frame, width=10)
        self.arrival_entry.grid(row=1, column=1, padx=5, pady=2, sticky=tk.W)
        
        ttk.Label(process_frame, text="Tiempo de ráfaga:").grid(row=2, column=0, padx=5, pady=2, sticky=tk.W)
        self.burst_entry = ttk.Entry(process_frame, width=10)
        self.burst_entry.grid(row=2, column=1, padx=5, pady=2, sticky=tk.W)
        
        ttk.Label(process_frame, text="Prioridad:").grid(row=3, column=0, padx=5, pady=2, sticky=tk.W)
        self.priority_entry = ttk.Entry(process_frame, width=10)
        self.priority_entry.grid(row=3, column=1, padx=5, pady=2, sticky=tk.W)
        ttk.Label(process_frame, text="(menor = mayor prioridad)").grid(row=3, column=2, padx=5, pady=2, sticky=tk.W)
        
        button_frame = ttk.Frame(process_frame)
        button_frame.grid(row=4, column=0, columnspan=3, pady=5)
        
        ttk.Button(button_frame, text="Agregar", command=self.add_process).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Editar", command=self.edit_process).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Eliminar", command=self.delete_process).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Limpiar", command=self.clear_processes).pack(side=tk.LEFT, padx=2)
        
        self.process_tree = ttk.Treeview(parent, columns=("ID", "Arrival", "Burst", "Priority"), show="headings", height=12)
        self.process_tree.heading("ID", text="ID")
        self.process_tree.heading("Arrival", text="T. Llegada")
        self.process_tree.heading("Burst", text="T. Ráfaga")
        self.process_tree.heading("Priority", text="Prioridad")
        self.process_tree.column("ID", width=50, anchor=tk.CENTER)
        self.process_tree.column("Arrival", width=80, anchor=tk.CENTER)
        self.process_tree.column("Burst", width=80, anchor=tk.CENTER)
        self.process_tree.column("Priority", width=80, anchor=tk.CENTER)
        self.process_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        config_frame = ttk.LabelFrame(parent, text="Configuración del Algoritmo")
        config_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(config_frame, text="Algoritmo:").grid(row=0, column=0, padx=5, pady=2, sticky=tk.W)
        self.algorithm_var = tk.StringVar(value="FCFS")
        algorithms = ["FCFS", "SJF", "Round Robin", "Prioridades"]
        self.algorithm_menu = ttk.Combobox(config_frame, textvariable=self.algorithm_var, values=algorithms, state="readonly", width=15)
        self.algorithm_menu.grid(row=0, column=1, padx=5, pady=2, sticky=tk.W)
        self.algorithm_menu.bind("<<ComboboxSelected>>", self.update_algorithm_settings)
        
        ttk.Label(config_frame, text="Quantum:").grid(row=1, column=0, padx=5, pady=2, sticky=tk.W)
        self.quantum_entry = ttk.Entry(config_frame, width=10)
        self.quantum_entry.grid(row=1, column=1, padx=5, pady=2, sticky=tk.W)
        self.quantum_entry.insert(0, "2")
        self.quantum_label = ttk.Label(config_frame, text="(Solo para Round Robin)")
        self.quantum_label.grid(row=1, column=2, padx=5, pady=2, sticky=tk.W)
        
        control_frame = ttk.Frame(parent)
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(control_frame, text="Ejecutar Simulación", command=self.run_simulation).pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
        ttk.Button(control_frame, text="Comparar Algoritmos", command=self.run_benchmark).pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
        ttk.Button(control_frame, text="Animación", command=self.toggle_animation).pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
        
        file_frame = ttk.Frame(parent)
        file_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(file_frame, text="Guardar Procesos", command=self.save_processes).pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
        ttk.Button(file_frame, text="Cargar Procesos", command=self.load_processes).pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
    
    def setup_output_panel(self, parent):
        notebook = ttk.Notebook(parent)
        notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        sim_tab = ttk.Frame(notebook)
        notebook.add(sim_tab, text="Simulación")
        
        self.gantt_frame = ttk.Frame(sim_tab)
        self.gantt_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        metrics_frame = ttk.LabelFrame(sim_tab, text="Métricas")
        metrics_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.metrics_text = tk.Text(metrics_frame, height=8, state=tk.DISABLED)
        scrollbar = ttk.Scrollbar(metrics_frame, orient="vertical", command=self.metrics_text.yview)
        self.metrics_text.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.metrics_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.compare_tab = ttk.Frame(notebook)
        notebook.add(self.compare_tab, text="Comparación", state="normal")
        
        self.metrics_tab = ttk.Frame(notebook)
        notebook.add(self.metrics_tab, text="Métricas Visuales", state="normal")
    
    def update_algorithm_settings(self, event=None):
        algorithm = self.algorithm_var.get()
        if algorithm == "Round Robin":
            self.quantum_entry.config(state="normal")
            self.quantum_label.config(foreground="black")
        else:
            self.quantum_entry.config(state="disabled")
            self.quantum_label.config(foreground="gray")
    
    def add_process(self):
        try:
            pid = self.id_entry.get()
            arrival = int(self.arrival_entry.get())
            burst = int(self.burst_entry.get())
            priority = self.priority_entry.get()
            
            if not pid:
                messagebox.showerror("Error", "El ID del proceso no puede estar vacío")
                return
                
            if burst <= 0:
                messagebox.showerror("Error", "El tiempo de ráfaga debe ser mayor que 0")
                return
                
            if arrival < 0:
                messagebox.showerror("Error", "El tiempo de llegada no puede ser negativo")
                return
                
            priority = int(priority) if priority else 0
            
            for item in self.process_tree.get_children():
                if self.process_tree.item(item, "values")[0] == pid:
                    messagebox.showerror("Error", f"El proceso con ID {pid} ya existe")
                    return
            
            self.process_tree.insert("", tk.END, values=(pid, arrival, burst, priority))
            self.processes.append({"id": pid, "arrival": arrival, "burst": burst, "priority": priority})
            
            try:
                next_id = max(int(pid) for pid in [p["id"] for p in self.processes] if pid.isdigit()) + 1
                self.current_id = next_id
            except:
                self.current_id += 1
            self.id_entry.delete(0, tk.END)
            self.id_entry.insert(0, str(self.current_id))
            
            self.arrival_entry.delete(0, tk.END)
            self.burst_entry.delete(0, tk.END)
            self.priority_entry.delete(0, tk.END)
            
        except ValueError:
            messagebox.showerror("Error", "Por favor ingrese valores numéricos válidos")
    
    def edit_process(self):
        selected = self.process_tree.selection()
        if not selected:
            messagebox.showerror("Error", "Por favor seleccione un proceso para editar")
            return
            
        item = selected[0]
        values = self.process_tree.item(item, "values")
        
        self.id_entry.delete(0, tk.END)
        self.id_entry.insert(0, values[0])
        self.arrival_entry.delete(0, tk.END)
        self.arrival_entry.insert(0, values[1])
        self.burst_entry.delete(0, tk.END)
        self.burst_entry.insert(0, values[2])
        self.priority_entry.delete(0, tk.END)
        self.priority_entry.insert(0, values[3])
        
        self.delete_process()
    
    def delete_process(self):
        selected = self.process_tree.selection()
        if not selected:
            messagebox.showerror("Error", "Por favor seleccione un proceso para eliminar")
            return
            
        for item in selected:
            pid = self.process_tree.item(item, "values")[0]
            self.process_tree.delete(item)
            self.processes = [p for p in self.processes if p["id"] != pid]
    
    def clear_processes(self):
        self.process_tree.delete(*self.process_tree.get_children())
        self.processes = []
        self.current_id = 1
        self.id_entry.delete(0, tk.END)
        self.id_entry.insert(0, "1")
        self.arrival_entry.delete(0, tk.END)
        self.burst_entry.delete(0, tk.END)
        self.priority_entry.delete(0, tk.END)
    
    def save_processes(self):
        if not self.processes:
            messagebox.showerror("Error", "No hay procesos para guardar")
            return
            
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, "w") as f:
                    json.dump(self.processes, f, indent=4)
                messagebox.showinfo("Éxito", "Procesos guardados correctamente")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar el archivo: {str(e)}")
    
    def load_processes(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, "r") as f:
                    new_processes = json.load(f)
                
                valid = True
                for p in new_processes:
                    if not all(key in p for key in ["id", "arrival", "burst"]):
                        valid = False
                        break
                    if "priority" not in p:
                        p["priority"] = 0
                
                if not valid:
                    messagebox.showerror("Error", "El archivo no contiene datos válidos de procesos")
                    return
                
                self.clear_processes()
                for p in new_processes:
                    self.process_tree.insert("", tk.END, values=(p["id"], p["arrival"], p["burst"], p["priority"]))
                self.processes = new_processes
                
                try:
                    next_id = max(int(pid) for pid in [p["id"] for p in self.processes] if str(pid).isdigit()) + 1
                    self.current_id = next_id
                except:
                    self.current_id = len(self.processes) + 1
                self.id_entry.delete(0, tk.END)
                self.id_entry.insert(0, str(self.current_id))
                
                messagebox.showinfo("Éxito", "Procesos cargados correctamente")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo cargar el archivo: {str(e)}")
    
    def run_simulation(self):
        if not self.processes:
            messagebox.showerror("Error", "No hay procesos para simular")
            return
            
        try:
            self.quantum = int(self.quantum_entry.get())
            if self.quantum <= 0:
                raise ValueError("El quantum debe ser mayor que 0")
        except ValueError:
            messagebox.showerror("Error", "Por favor ingrese un valor de quantum válido")
            return
            
        algorithm = self.algorithm_var.get()
        
        for widget in self.gantt_frame.winfo_children():
            widget.destroy()
        
        self.metrics_text.config(state=tk.NORMAL)
        self.metrics_text.delete(1.0, tk.END)
        self.metrics_text.config(state=tk.DISABLED)
        
        if algorithm == "FCFS":
            results = self.fcfs_algorithm()
        elif algorithm == "SJF":
            results = self.sjf_algorithm()
        elif algorithm == "Round Robin":
            results = self.round_robin_algorithm()
        elif algorithm == "Prioridades":
            results = self.priority_algorithm()
        else:
            messagebox.showerror("Error", "Algoritmo no implementado")
            return
        
        self.display_results(results)
    
    def run_algorithm(self):
        algorithm = self.algorithm_var.get()
        
        if algorithm == "FCFS":
            return self.fcfs_algorithm()
        elif algorithm == "SJF":
            return self.sjf_algorithm()
        elif algorithm == "Round Robin":
            return self.round_robin_algorithm()
        elif algorithm == "Prioridades":
            return self.priority_algorithm()
        else:
            return []
    
    def fcfs_algorithm(self):
        processes = sorted(self.processes.copy(), key=lambda x: x["arrival"])
        timeline = []
        current_time = 0
        
        for p in processes:
            if current_time < p["arrival"]:
                current_time = p["arrival"]
            
            timeline.append({
                "process": p["id"],
                "start": current_time,
                "end": current_time + p["burst"],
                "arrival": p["arrival"],
                "burst": p["burst"],
                "priority": p["priority"]
            })
            
            current_time += p["burst"]
        
        return timeline
    
    def sjf_algorithm(self):
        processes = sorted(self.processes.copy(), key=lambda x: (x["arrival"], x["burst"]))
        timeline = []
        current_time = 0
        ready_queue = []
        process_index = 0
        
        while process_index < len(processes) or ready_queue:
            while process_index < len(processes) and processes[process_index]["arrival"] <= current_time:
                ready_queue.append(processes[process_index])
                process_index += 1
            
            if not ready_queue:
                if process_index < len(processes):
                    current_time = processes[process_index]["arrival"]
                    continue
                else:
                    break
            
            ready_queue.sort(key=lambda x: x["burst"])
            current_process = ready_queue.pop(0)
            
            timeline.append({
                "process": current_process["id"],
                "start": current_time,
                "end": current_time + current_process["burst"],
                "arrival": current_process["arrival"],
                "burst": current_process["burst"],
                "priority": current_process["priority"]
            })
            
            current_time += current_process["burst"]
        
        return timeline
    
    def round_robin_algorithm(self):
        processes = sorted(self.processes.copy(), key=lambda x: x["arrival"])
        timeline = []
        current_time = 0
        ready_queue = deque()
        process_index = 0
        remaining_burst = {p["id"]: p["burst"] for p in processes}
        process_info = {p["id"]: p for p in processes}
        
        while process_index < len(processes) or ready_queue:
            while process_index < len(processes) and processes[process_index]["arrival"] <= current_time:
                ready_queue.append(processes[process_index]["id"])
                process_index += 1
            
            if not ready_queue:
                if process_index < len(processes):
                    current_time = processes[process_index]["arrival"]
                    continue
                else:
                    break
            
            current_pid = ready_queue.popleft()
            burst_time = remaining_burst[current_pid]
            
            exec_time = min(self.quantum, burst_time)
            
            timeline.append({
                "process": current_pid,
                "start": current_time,
                "end": current_time + exec_time,
                "arrival": process_info[current_pid]["arrival"],
                "burst": process_info[current_pid]["burst"],
                "priority": process_info[current_pid]["priority"]
            })
            
            current_time += exec_time
            remaining_burst[current_pid] -= exec_time
            
            while process_index < len(processes) and processes[process_index]["arrival"] <= current_time:
                ready_queue.append(processes[process_index]["id"])
                process_index += 1
            
            if remaining_burst[current_pid] > 0:
                ready_queue.append(current_pid)
        
        return timeline
    
    def priority_algorithm(self):
        processes = sorted(self.processes.copy(), key=lambda x: x["arrival"])
        timeline = []
        current_time = 0
        ready_queue = []
        process_index = 0
        current_process = None
        remaining_burst = {p["id"]: p["burst"] for p in processes}

        while process_index < len(processes) or ready_queue or current_process:
            # Agregar procesos que han llegado al sistema
            while process_index < len(processes) and processes[process_index]["arrival"] <= current_time:
                ready_queue.append(processes[process_index])
                process_index += 1

            # Ordenar por prioridad (menor número = mayor prioridad)
            ready_queue.sort(key=lambda x: x["priority"])

            # Seleccionar el proceso con mayor prioridad (si hay uno)
            if ready_queue:
                next_process = ready_queue[0]
                if current_process is None or next_process["priority"] < current_process["priority"]:
                    if current_process:
                        # Interrumpir el proceso actual y guardar su progreso
                        timeline.append({
                            "process": current_process["id"],
                            "start": start_time,
                            "end": current_time,
                            "arrival": current_process["arrival"],
                            "burst": current_process["burst"],
                            "priority": current_process["priority"]
                        })
                        remaining_burst[current_process["id"]] -= (current_time - start_time)
                        ready_queue.append(current_process)
                    # Tomar el nuevo proceso de mayor prioridad
                    current_process = next_process
                    ready_queue.remove(next_process)
                    start_time = current_time

            # Si no hay proceso en ejecución, avanzar el tiempo
            if current_process is None:
                current_time += 1
                continue

            # Ejecutar el proceso actual por 1 unidad de tiempo
            current_time += 1
            remaining_burst[current_process["id"]] -= 1

            # Si el proceso actual termina
            if remaining_burst[current_process["id"]] == 0:
                timeline.append({
                    "process": current_process["id"],
                    "start": start_time,
                    "end": current_time,
                    "arrival": current_process["arrival"],
                    "burst": current_process["burst"],
                    "priority": current_process["priority"]
                })
                current_process = None

        return timeline

    
    def display_results(self, timeline):
        if not timeline:
            messagebox.showerror("Error", "No se generó una línea de tiempo válida")
            return
        
        metrics = self.calculate_metrics(timeline)
        
        self.metrics_text.config(state=tk.NORMAL)
        self.metrics_text.delete(1.0, tk.END)
        
        self.metrics_text.insert(tk.END, "Métricas de desempeño:\n\n")
        self.metrics_text.insert(tk.END, f"Algoritmo utilizado: {self.algorithm_var.get()}\n")
        if self.algorithm_var.get() == "Round Robin":
            self.metrics_text.insert(tk.END, f"Quantum: {self.quantum}\n")
        
        self.metrics_text.insert(tk.END, "\nTiempos por proceso:\n")
        for pid, data in metrics["process_metrics"].items():
            self.metrics_text.insert(tk.END, 
                f"Proceso {pid}: Espera={data['wait_time']}, Respuesta={data['response_time']}, Retorno={data['turnaround_time']}\n")
        
        self.metrics_text.insert(tk.END, "\nMétricas promedio:\n")
        self.metrics_text.insert(tk.END, f"Tiempo de espera promedio: {metrics['avg_wait_time']:.2f}\n")
        self.metrics_text.insert(tk.END, f"Tiempo de respuesta promedio: {metrics['avg_response_time']:.2f}\n")
        self.metrics_text.insert(tk.END, f"Tiempo de retorno promedio: {metrics['avg_turnaround_time']:.2f}\n")
        self.metrics_text.insert(tk.END, f"Uso de CPU: {metrics['cpu_usage']:.2f}%\n")
        
        self.metrics_text.config(state=tk.DISABLED)
        
        self.plot_enhanced_gantt_chart(timeline)
    
    def calculate_metrics(self, timeline):
        process_info = {p["id"]: p for p in self.processes}
        process_metrics = {}
        
        for pid in process_info:
            process_metrics[pid] = {
                "first_run": None,
                "last_run": None,
                "burst_time": process_info[pid]["burst"],
                "arrival_time": process_info[pid]["arrival"]
            }
        
        for event in timeline:
            pid = event["process"]
            if process_metrics[pid]["first_run"] is None:
                process_metrics[pid]["first_run"] = event["start"]
            process_metrics[pid]["last_run"] = event["end"]
        
        total_wait_time = 0
        total_response_time = 0
        total_turnaround_time = 0
        total_cpu_time = 0
        
        for pid, metrics in process_metrics.items():
            if metrics["first_run"] is None:
                continue
            
            metrics["response_time"] = metrics["first_run"] - metrics["arrival_time"]
            metrics["turnaround_time"] = metrics["last_run"] - metrics["arrival_time"]
            metrics["wait_time"] = metrics["turnaround_time"] - metrics["burst_time"]
            
            total_wait_time += metrics["wait_time"]
            total_response_time += metrics["response_time"]
            total_turnaround_time += metrics["turnaround_time"]
            total_cpu_time += metrics["burst_time"]
        
        num_processes = len(process_metrics)
        avg_wait_time = total_wait_time / num_processes
        avg_response_time = total_response_time / num_processes
        avg_turnaround_time = total_turnaround_time / num_processes
        
        total_time = max(event["end"] for event in timeline) if timeline else 0
        cpu_usage = (total_cpu_time / total_time) * 100 if total_time > 0 else 0
        
        return {
            "process_metrics": {pid: {
                "wait_time": data["wait_time"],
                "response_time": data["response_time"],
                "turnaround_time": data["turnaround_time"]
            } for pid, data in process_metrics.items()},
            "avg_wait_time": avg_wait_time,
            "avg_response_time": avg_response_time,
            "avg_turnaround_time": avg_turnaround_time,
            "cpu_usage": cpu_usage
        }
    
    def plot_enhanced_gantt_chart(self, timeline):
        for widget in self.gantt_frame.winfo_children():
            widget.destroy()
        
        if not timeline:
            return
        
        fig, ax = plt.subplots(figsize=(12, 5))
        algorithm = self.algorithm_var.get()
        algorithm_styles = {
            "FCFS": {"color": "tab:blue", "hatch": None, "alpha": 0.7},
            "SJF": {"color": "tab:green", "hatch": "//", "alpha": 0.7},
            "Round Robin": {"color": "tab:orange", "hatch": "xx", "alpha": 0.7},
            "Prioridades": {"color": "tab:purple", "hatch": "..", "alpha": 0.7}
        }
        style = algorithm_styles.get(algorithm, {"color": "tab:blue", "hatch": None, "alpha": 0.7})
        
        unique_processes = list(set(event["process"] for event in timeline))
        color_map = plt.get_cmap('tab20', len(unique_processes))
        
        ax.set_title(f"Diagrama de Gantt - Algoritmo {algorithm}", pad=20)
        ax.set_xlabel('Tiempo')
        ax.set_yticks([1])
        ax.set_yticklabels(['CPU'])
        ax.grid(True, axis='x', linestyle='--', alpha=0.6)
        
        for i, event in enumerate(timeline):
            pid = event["process"]
            start = event["start"]
            duration = event["end"] - start
            color_idx = unique_processes.index(pid)
            
            rect = patches.Rectangle(
                (start, 0), duration, 1,
                facecolor=color_map(color_idx),
                edgecolor='black',
                linewidth=1,
                label=pid,
                alpha=style["alpha"],
                hatch=style["hatch"]
            )
            ax.add_patch(rect)
            
            ax.text(start + duration/2, 0.5, pid, 
                   ha='center', va='center', color='white', weight='bold', fontsize=10)
            
            if i < len(timeline) - 1:
                ax.axvline(x=event["end"], color='gray', linestyle=':', linewidth=1, alpha=0.5)
            
            if "arrival" in event and event["arrival"] < start:
                ax.axvline(x=event["arrival"], color='red', linestyle='--', linewidth=1, alpha=0.7)
                ax.text(event["arrival"], 1.1, f"Llegada {pid}", 
                       ha='center', va='bottom', color='red', fontsize=8)
        
        for p in self.processes:
            first_run = next((e["start"] for e in timeline if e["process"] == p["id"]), None)
            if first_run and first_run > p["arrival"]:
                ax.axvspan(p["arrival"], first_run, color='gray', alpha=0.2, hatch='//')
                ax.text((p["arrival"] + first_run)/2, 0.3, f"Espera {p['id']}", 
                       ha='center', va='center', color='black', fontsize=8)
        
        max_time = max(event["end"] for event in timeline)
        ax.set_xlim(0, max_time * 1.05)
        ax.set_ylim(0, 1.2)
        
        handles = []
        for i, pid in enumerate(unique_processes):
            handles.append(patches.Patch(
                facecolor=color_map(i),
                edgecolor='black',
                label=f"Proceso {pid}",
                alpha=style["alpha"],
                hatch=style["hatch"]
            ))
        
        legend = ax.legend(
            handles=handles, 
            title="Procesos", 
            bbox_to_anchor=(1.05, 1), 
            loc='upper left',
            fontsize=8
        )
        
        ax.text(
            0.98, 1.08, 
            f"Algoritmo: {algorithm}\nQuantum: {self.quantum if algorithm == 'Round Robin' else 'N/A'}", 
            transform=ax.transAxes,
            ha='right',
            va='top',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.8)
        )
        
        def on_hover(event):
            if event.inaxes == ax:
                for patch in ax.patches:
                    if isinstance(patch, patches.Rectangle):
                        contains, _ = patch.contains(event)
                        if contains:
                            pid = patch.get_label()
                            process = next(p for p in self.processes if p["id"] == pid)
                            patch.set_edgecolor('yellow')
                            patch.set_linewidth(2)
                            
                            ax.annotate(
                                f"Proceso {pid}\n"
                                f"Llegada: {process['arrival']}\n"
                                f"Ráfaga: {process['burst']}\n"
                                f"Prioridad: {process.get('priority', 'N/A')}",
                                xy=(patch.get_x() + patch.get_width()/2, 1.1),
                                xytext=(10, 10),
                                textcoords='offset points',
                                bbox=dict(boxstyle='round', facecolor='white', alpha=0.9),
                                arrowprops=dict(arrowstyle='->')
                            )
                        else:
                            patch.set_edgecolor('black')
                            patch.set_linewidth(1)
                fig.canvas.draw_idle()
        
        fig.canvas.mpl_connect('motion_notify_event', on_hover)
        
        plt.tight_layout()
        
        canvas = FigureCanvasTkAgg(fig, master=self.gantt_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        toolbar = NavigationToolbar2Tk(canvas, self.gantt_frame)
        toolbar.update()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        self.current_fig = fig
        self.current_ax = ax
        self.current_canvas = canvas
    
    def run_benchmark(self):
        if not self.processes:
            messagebox.showerror("Error", "No hay procesos para comparar")
            return
            
        for widget in self.compare_tab.winfo_children():
            widget.destroy()
        
        try:
            fig, axs = plt.subplots(4, 1, figsize=(12, 12))
            algorithms = ["FCFS", "SJF", "Round Robin", "Prioridades"]
            
            for i, algo in enumerate(algorithms):
                self.algorithm_var.set(algo)
                timeline = self.run_algorithm()
                self.plot_comparison_gantt(axs[i], timeline, algo)
            
            plt.tight_layout()
            
            canvas = FigureCanvasTkAgg(fig, master=self.compare_tab)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            
            toolbar = NavigationToolbar2Tk(canvas, self.compare_tab)
            toolbar.update()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            
            self.plot_metrics_comparison()
        except Exception as e:
            messagebox.showerror("Error", f"Error en comparación: {str(e)}")

            
    
    def plot_comparison_gantt(self, ax, timeline, title):
        if not timeline:
            return
        
        algorithm_styles = {
            "FCFS": {"color": "tab:blue", "hatch": None, "alpha": 0.7},
            "SJF": {"color": "tab:green", "hatch": "//", "alpha": 0.7},
            "Round Robin": {"color": "tab:orange", "hatch": "xx", "alpha": 0.7},
            "Prioridades": {"color": "tab:purple", "hatch": "..", "alpha": 0.7}
        }
        style = algorithm_styles.get(title, {"color": "tab:blue", "hatch": None, "alpha": 0.7})
        
        unique_processes = list(set(event["process"] for event in timeline))
        color_map = plt.get_cmap('tab20', len(unique_processes))
        
        ax.set_title(title, pad=10)
        ax.set_yticks([1])
        ax.set_yticklabels(['CPU'])
        ax.grid(True, axis='x', linestyle='--', alpha=0.6)
        
        for i, event in enumerate(timeline):
            pid = event["process"]
            start = event["start"]
            duration = event["end"] - start
            color_idx = unique_processes.index(pid)
            
            rect = patches.Rectangle(
                (start, 0), duration, 1,
                facecolor=color_map(color_idx),
                edgecolor='black',
                linewidth=1,
                alpha=style["alpha"],
                hatch=style["hatch"]
            )
            ax.add_patch(rect)
            
            if duration >= 2:
                ax.text(start + duration/2, 0.5, pid, 
                       ha='center', va='center', color='white', weight='bold', fontsize=8)
            
            if i < len(timeline) - 1:
                ax.axvline(x=event["end"], color='gray', linestyle=':', linewidth=1, alpha=0.5)
        
        max_time = max(event["end"] for event in timeline)
        ax.set_xlim(0, max_time * 1.05)
        ax.set_ylim(0, 1.2)
    
    def plot_metrics_comparison(self):
        if not self.processes:
            return
            
        for widget in self.metrics_tab.winfo_children():
            widget.destroy()
        
        algorithms = ["FCFS", "SJF", "Round Robin", "Prioridades"]
        metrics = {'wait': [], 'response': [], 'turnaround': [], 'cpu_usage': []}
        
        for algo in algorithms:
            self.algorithm_var.set(algo)
            timeline = self.run_algorithm()
            m = self.calculate_metrics(timeline)
            metrics['wait'].append(m['avg_wait_time'])
            metrics['response'].append(m['avg_response_time'])
            metrics['turnaround'].append(m['avg_turnaround_time'])
            metrics['cpu_usage'].append(m['cpu_usage'])
        
        try:
            fig, ax = plt.subplots(figsize=(10, 6))
            x = np.arange(len(algorithms))
            width = 0.2
            
            rects1 = ax.bar(x - width*1.5, metrics['wait'], width, label='Espera Promedio')
            rects2 = ax.bar(x - width/2, metrics['response'], width, label='Respuesta Promedio')
            rects3 = ax.bar(x + width/2, metrics['turnaround'], width, label='Retorno Promedio')
            rects4 = ax.bar(x + width*1.5, metrics['cpu_usage'], width, label='Uso CPU (%)')
            
            ax.set_ylabel('Tiempo')
            ax.set_title('Comparación de Métricas por Algoritmo')
            ax.set_xticks(x)
            ax.set_xticklabels(algorithms)
            ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
            
            def autolabel(rects):
                for rect in rects:
                    height = rect.get_height()
                    ax.annotate(f'{height:.1f}',
                                xy=(rect.get_x() + rect.get_width() / 2, height),
                                xytext=(0, 3),
                                textcoords="offset points",
                                ha='center', va='bottom')
            
            autolabel(rects1)
            autolabel(rects2)
            autolabel(rects3)
            autolabel(rects4)
            
            plt.tight_layout()
            
            canvas = FigureCanvasTkAgg(fig, master=self.metrics_tab)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            
            toolbar = NavigationToolbar2Tk(canvas, self.metrics_tab)
            toolbar.update()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        except Exception as e:
            messagebox.showerror("Error", f"Error en métricas: {str(e)}")
    
    def toggle_animation(self):
        if not self.processes:
            messagebox.showerror("Error", "No hay procesos para animar")
            return
            
        if self.animation_running:
            if self.animation and self.animation.event_source:
                self.animation.event_source.stop()
                self.animation = None
            self.animation_running = False
            for widget in self.gantt_frame.winfo_children():
                widget.destroy()
            return
            
        for widget in self.gantt_frame.winfo_children():
            widget.destroy()
        
        timeline = self.run_algorithm()
        if not timeline:
            return
        
        fig, ax = plt.subplots(figsize=(12, 5))
        ax.set_title(f"Animación - Algoritmo {self.algorithm_var.get()}", pad=20)
        ax.set_xlabel('Tiempo')
        ax.set_yticks([1])
        ax.set_yticklabels(['CPU'])
        ax.grid(True, axis='x', linestyle='--', alpha=0.6)
        
        max_time = max(event["end"] for event in timeline) if timeline else 10
        ax.set_xlim(0, max_time * 1.05)
        ax.set_ylim(0, 1.2)
        
        rects = []
        for event in timeline:
            pid = event["process"]
            start = event["start"]
            duration = event["end"] - start
            
            rect = patches.Rectangle(
                (start, 0), duration, 1,
                facecolor='gray',
                edgecolor='black',
                alpha=0.3
            )
            ax.add_patch(rect)
            rects.append(rect)
        
        def init():
            for rect in rects:
                rect.set_width(0)
            return rects
        
        def animate(i):
            for j, rect in enumerate(rects):
                if j <= i:
                    event = timeline[j]
                    pid = event["process"]
                    start = event["start"]
                    duration = event["end"] - start
                    
                    rect.set_width(duration)
                    rect.set_x(start)
                    rect.set_facecolor(plt.get_cmap('tab20')(j % 20))
                    
                    if j == i:
                        ax.text(start + duration/2, 0.5, pid, 
                               ha='center', va='center', color='white', weight='bold')
            return rects
        
        self.animation = FuncAnimation(
            fig, animate, frames=len(timeline),
            init_func=init, blit=True, interval=500, repeat=False
        )
        
        canvas = FigureCanvasTkAgg(fig, master=self.gantt_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        self.animation_running = True

if __name__ == "__main__":
    root = tk.Tk()
    app = EnhancedProcessSchedulingSimulator(root)
    root.mainloop()