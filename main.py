import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox
import math
import copy

# Project imports
from base_model import Graph

ctk.set_appearance_mode("Dark")  
ctk.set_default_color_theme("blue")  

class ModernGraphSearchApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("AI Search Visualizer")
        self.geometry("1300x750")

        self.nodes = {}       
        self.edges = {}       
        self.heuristics = {}  
        self.node_counter = 0
        
        self.mode = "Add Node"
        self.start_node = None
        self.goal_nodes = set()
        self.selected_node = None 
        self.history = [] 
        
        self.setup_ui()

    def setup_ui(self):
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1) 

        self.sidebar = ctk.CTkFrame(self, width=250, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(11, weight=1) 

        ctk.CTkLabel(self.sidebar, text="Tools", font=ctk.CTkFont(size=20, weight="bold")).grid(row=0, column=0, padx=20, pady=(20, 10))

        self.radio_var = tk.StringVar(value="Add Node")
        modes = ["Add Node", "Add Edge", "Set Start", "Set Goal"]
        
        for i, mode in enumerate(modes):
            rb = ctk.CTkRadioButton(self.sidebar, text=mode, variable=self.radio_var, value=mode, command=self.update_mode)
            rb.grid(row=i+1, column=0, pady=10, padx=20, sticky="w")

        self.heuristic_rb = ctk.CTkRadioButton(self.sidebar, text="Set Heuristic", variable=self.radio_var, value="Set Heuristic", command=self.update_mode)

        ctk.CTkLabel(self.sidebar, text="Algorithm", font=ctk.CTkFont(size=16, weight="bold")).grid(row=6, column=0, padx=20, pady=(30, 10))
        
        self.algo_dropdown = ctk.CTkOptionMenu(self.sidebar, dynamic_resizing=False,
                                               values=["DFS (Depth-First)", "BFS (Breadth-First)", "UCS (Uniform Cost)", "A* Search", "Greedy BFS"],
                                               command=self.on_algo_change)
        self.algo_dropdown.grid(row=7, column=0, padx=20, pady=10)

        self.undo_btn = ctk.CTkButton(self.sidebar, text="↶ Undo", fg_color="#F59E0B", hover_color="#D97706", command=self.undo_action)
        self.undo_btn.grid(row=8, column=0, padx=20, pady=(20, 10), sticky="s")

        self.run_btn = ctk.CTkButton(self.sidebar, text="▶ Run Search", fg_color="#2FA572", hover_color="#107C41", command=self.run_algorithm)
        self.run_btn.grid(row=9, column=0, padx=20, pady=(10, 10), sticky="s")

        self.clear_btn = ctk.CTkButton(self.sidebar, text="Clear Canvas", fg_color="#D32F2F", hover_color="#B71C1C", command=self.clear_graph)
        self.clear_btn.grid(row=10, column=0, padx=20, pady=(0, 20), sticky="s")

        self.canvas_frame = ctk.CTkFrame(self)
        self.canvas_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        
        self.canvas = tk.Canvas(self.canvas_frame, bg="#2B2B2B", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        self.canvas.bind("<Button-1>", self.on_canvas_click)

        self.state_panel = ctk.CTkFrame(self, width=250, corner_radius=0, fg_color="#1E1E1E")
        self.state_panel.grid(row=0, column=2, sticky="nsew")
        
        self.state_panel.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(self.state_panel, text="Visited Nodes", font=ctk.CTkFont(size=16, weight="bold"), text_color="#A78BFA").grid(row=0, column=0, pady=(20, 5))
        self.visited_scroll = ctk.CTkScrollableFrame(self.state_panel, fg_color="#2B2B2B", width=200)
        self.visited_scroll.grid(row=1, column=0, padx=15, pady=(5, 20), sticky="nsew")

    def on_algo_change(self, choice):
        if choice.startswith("A*") or choice.startswith("Greedy"):
            self.heuristic_rb.grid(row=5, column=0, pady=10, padx=20, sticky="w")
        else:
            self.heuristic_rb.grid_forget()
            if self.radio_var.get() == "Set Heuristic":
                self.radio_var.set("Add Node")
                self.update_mode()

    def update_mode(self):
        self.mode = self.radio_var.get()
        self.selected_node = None 
        self.draw_graph()

    def save_state(self):
        state = {
            'nodes': copy.deepcopy(self.nodes),
            'edges': copy.deepcopy(self.edges),
            'heuristics': copy.deepcopy(self.heuristics),
            'node_counter': self.node_counter,
            'start_node': self.start_node,
            'goal_nodes': copy.deepcopy(self.goal_nodes)
        }
        self.history.append(state)
        if len(self.history) > 50:
            self.history.pop(0)

    def undo_action(self):
        if not self.history: return
        last_state = self.history.pop()
        self.nodes = last_state['nodes']
        self.edges = last_state['edges']
        self.heuristics = last_state.get('heuristics', {})
        self.node_counter = last_state['node_counter']
        self.start_node = last_state['start_node']
        self.goal_nodes = last_state['goal_nodes']
        self.selected_node = None 
        self.draw_graph()

    # --- NEW HELPER: Converts 1, 2, 3 into A, B, C ---
    def get_alpha_label(self, index):
        label = ""
        while index > 0:
            index -= 1
            label = chr(65 + (index % 26)) + label
            index //= 26
        return label

    def on_canvas_click(self, event):
        x, y = event.x, event.y
        clicked_node = self.get_node_at(x, y)

        if self.mode == "Add Node" and not clicked_node:
            self.save_state() 
            self.node_counter += 1
            
            # --- UPDATED: Use letters instead of numbers ---
            node_label = self.get_alpha_label(self.node_counter)
            self.nodes[node_label] = (x, y)
            self.edges[node_label] = {}
            # -----------------------------------------------
            
            self.draw_graph()

        elif self.mode == "Add Edge" and clicked_node:
            if not self.selected_node:
                self.selected_node = clicked_node
                self.draw_graph() 
            elif self.selected_node != clicked_node:
                
                ux, uy = self.nodes[self.selected_node]
                vx, vy = self.nodes[clicked_node]
                phys_dist = round(math.hypot(vx - ux, vy - uy) / 10.0, 1)

                dialog = ctk.CTkInputDialog(text=f"Enter edge weight (Default: {phys_dist}):", title="Edge Cost")
                weight_str = dialog.get_input()
                
                try:
                    weight = float(weight_str) if weight_str else phys_dist
                except ValueError:
                    weight = phys_dist 
                
                self.save_state() 
                self.edges[self.selected_node][clicked_node] = weight
                self.edges[clicked_node][self.selected_node] = weight
                self.selected_node = None
                self.draw_graph()

        elif self.mode == "Set Start" and clicked_node:
            self.save_state() 
            self.start_node = clicked_node
            self.draw_graph()

        elif self.mode == "Set Goal" and clicked_node:
            self.save_state() 
            if clicked_node in self.goal_nodes:
                self.goal_nodes.remove(clicked_node)
            else:
                self.goal_nodes.add(clicked_node)
            self.draw_graph()
            
        elif self.mode == "Set Heuristic" and clicked_node:
            dialog = ctk.CTkInputDialog(text=f"Enter Heuristic (h) for Node {clicked_node}:", title="Set Heuristic")
            h_str = dialog.get_input()
            
            try:
                if h_str is not None and h_str.strip() != "":
                    h_val = float(h_str)
                    self.save_state()
                    self.heuristics[clicked_node] = h_val
                    self.draw_graph()
            except ValueError:
                messagebox.showerror("Invalid Input", "Please enter a valid number.")

    def get_node_at(self, x, y, radius=18):
        for node_id, (nx, ny) in self.nodes.items():
            if math.hypot(nx - x, ny - y) <= radius:
                return node_id
        return None

    def draw_graph(self):
        self.canvas.delete("all")
        
        for u, neighbors in self.edges.items():
            ux, uy = self.nodes[u]
            for v, weight in neighbors.items(): 
                vx, vy = self.nodes[v]
                self.canvas.create_line(ux, uy, vx, vy, fill="#666666", width=2, tags="edge")
                
                mid_x = (ux + vx) / 2
                mid_y = (uy + vy) / 2
                
                self.canvas.create_rectangle(mid_x-10, mid_y-8, mid_x+10, mid_y+8, fill="#2B2B2B", outline="")
                self.canvas.create_text(mid_x, mid_y, text=str(weight), font=("Roboto", 10, "bold"), fill="#A78BFA")

        for node_id, (x, y) in self.nodes.items():
            fill_color = "#3B82F6" 
            outline_color = "#1D4ED8"
            
            if node_id == self.start_node:
                fill_color = "#10B981" 
                outline_color = "#047857"
            elif node_id in self.goal_nodes:
                fill_color = "#EF4444" 
                outline_color = "#B91C1C"
            elif node_id == self.selected_node:
                fill_color = "#F59E0B" 
                outline_color = "#B45309"
            
            self.canvas.create_oval(x-18, y-18, x+18, y+18, fill=fill_color, outline=outline_color, width=2)
            self.canvas.create_text(x, y, text=str(node_id), font=("Roboto", 12, "bold"), fill="white")
            
            if node_id in self.heuristics:
                h_val = self.heuristics[node_id]
                self.canvas.create_rectangle(x-18, y-38, x+18, y-22, fill="#1E1E1E", outline="#FCA5A5")
                self.canvas.create_text(x, y-30, text=f"h={h_val}", font=("Roboto", 10, "bold"), fill="#FCA5A5")

    def update_side_panels(self, visited):
        for widget in self.visited_scroll.winfo_children():
            widget.destroy()
            
        for node in visited:
            ctk.CTkLabel(self.visited_scroll, text=f"Node {node}", fg_color="#6D28D9", text_color="white", corner_radius=5).pack(pady=2, fill="x", padx=5)

    def clear_side_panels(self):
        self.update_side_panels([])

    def run_algorithm(self):
        if not self.start_node or not self.goal_nodes:
            messagebox.showwarning("Incomplete Graph", "Please define a Start node and at least one Goal node.")
            return

        algo = self.algo_dropdown.get()
        self.draw_graph() 
        self.clear_side_panels()

        graph = Graph()
        
        for node_id, pos in self.nodes.items():
            h_cost = 0.0
            
            if node_id in self.heuristics:
                h_cost = self.heuristics[node_id]
            elif self.goal_nodes:
                min_dist = min(math.hypot(self.nodes[g][0] - pos[0], self.nodes[g][1] - pos[1]) for g in self.goal_nodes)
                h_cost = round(min_dist / 10.0, 1)
                
            graph.add_node(str(node_id), pos, heuristic=h_cost)
        
        added_edges = set()
        for u, neighbors_dict in self.edges.items():
            for v, weight in neighbors_dict.items():
                edge_pair = tuple(sorted([str(u), str(v)]))
                if edge_pair not in added_edges:
                    graph.add_edge(str(u), str(v), weight, directed=False)
                    added_edges.add(edge_pair)

        start_str = str(self.start_node)
        goals_str = [str(g) for g in self.goal_nodes]

        if algo.startswith("DFS"):
            from algorithms.dfs import run_dfs
            result = run_dfs(graph, start_str, goals_str)
            
        elif algo.startswith("BFS"):
            from algorithms.bfs import run_bfs
            result = run_bfs(graph, start_str, goals_str)
            
        elif algo.startswith("UCS"):
            from algorithms.ucs import run_ucs
            result = run_ucs(graph, start_str, goals_str)
            
        elif algo.startswith("A*"):
            from algorithms.a_star import run_a_star
            result = run_a_star(graph, start_str, goals_str)
            
        elif algo.startswith("Greedy"):
            from algorithms.gbfs import run_gbfs
            result = run_gbfs(graph, start_str, goals_str)
            
        else:
            messagebox.showinfo("Unknown Algorithm", f"Could not find a match for {algo}.")
            return

        # --- UPDATED: Leave the node IDs as strings (A, B, C) instead of forcing them to integers ---
        exploration_order = result.get("exploration_order", [])
        final_path = result.get("final_path", [])
        # --------------------------------------------------------------------------------------------
        
        self.visualize(exploration_order, final_path)

    def visualize(self, exploration_order, path, index=0, visited_so_far=None):
        if visited_so_far is None:
            visited_so_far = []

        if index < len(exploration_order):
            node = exploration_order[index]
            visited_so_far.append(node)
            
            if node != self.start_node and node not in self.goal_nodes:
                x, y = self.nodes[node]
                self.canvas.create_oval(x-18, y-18, x+18, y+18, fill="#8B5CF6", outline="#6D28D9", width=2) 
                self.canvas.create_text(x, y, text=str(node), font=("Roboto", 12, "bold"), fill="white")
            
            self.update_side_panels(visited_so_far)
            
            self.after(500, self.visualize, exploration_order, path, index + 1, visited_so_far)
        
        elif path:
            for i in range(len(path) - 1):
                u, v = path[i], path[i+1]
                ux, uy = self.nodes[u]
                vx, vy = self.nodes[v]
                self.canvas.create_line(ux, uy, vx, vy, fill="#F59E0B", width=5, tags="path") 
            
            for node_id in path:
                x, y = self.nodes[node_id]
                fill_color = "#F59E0B" if node_id not in [self.start_node] + list(self.goal_nodes) else ("#10B981" if node_id == self.start_node else "#EF4444")
                self.canvas.create_oval(x-18, y-18, x+18, y+18, fill=fill_color, outline="white", width=2)
                self.canvas.create_text(x, y, text=str(node_id), font=("Roboto", 12, "bold"), fill="white")

    def clear_graph(self):
        self.save_state() 
        self.nodes.clear()
        self.edges.clear()
        self.heuristics.clear()
        self.node_counter = 0
        self.start_node = None
        self.goal_nodes.clear()
        self.draw_graph()
        self.clear_side_panels()

if __name__ == "__main__":
    app = ModernGraphSearchApp()
    app.mainloop()