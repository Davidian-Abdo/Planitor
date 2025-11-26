import pandas as pd
from collections import defaultdict, deque
from typing import List



class CPMAnalyzer:
    """
    Critical Path Method analyzer for project scheduling.
    """
    
    def __init__(self, tasks, durations=None, dependencies=None):
        """
        Initialize CPM analyzer with tasks and dependencies.
        
        Args:
            tasks: List of tasks or task IDs
            durations: Dictionary of task durations (if tasks are IDs)
            dependencies: Dictionary of task dependencies (if tasks are IDs)
        """
        # Case A: List of Task objects
        if durations is None and dependencies is None and tasks and hasattr(tasks[0], "id"):
            self.tasks = tasks
            self.task_by_id = {t.id: t for t in tasks}
            self.durations = {t.id: t.base_duration for t in tasks}
            self.dependencies = {t.id: t.predecessors for t in tasks}
        # Case B: Raw IDs with dictionaries
        else:
            self.tasks = tasks
            self.task_by_id = {tid: None for tid in tasks}
            self.durations = durations
            self.dependencies = dependencies

        # Graph structures
        self.adj = defaultdict(list)      # Successors
        self.rev_adj = defaultdict(list)  # Predecessors  
        self.indeg = defaultdict(int)     # In-degree
        self.outdeg = defaultdict(int)    # Out-degree

        # CPM results
        self.ES, self.EF = {}, {}  # Earliest Start/Finish
        self.LS, self.LF = {}, {}  # Latest Start/Finish  
        self.float = {}            # Float/Slack
        self.project_duration = 0

    def build_graph(self):
        """Build task dependency graph."""
        for tid in self.tasks:
            preds = self.dependencies.get(tid, [])
            for pred in preds:
                self.adj[pred].append(tid)
                self.rev_adj[tid].append(pred)
                self.indeg[tid] += 1
                self.outdeg[pred] += 1

    def forward_pass(self):
        """Compute earliest start and finish times."""
        queue = deque([tid for tid in self.tasks if self.indeg[tid] == 0])
        
        while queue:
            current = queue.popleft()
            preds = self.dependencies.get(current, [])
            
            # Earliest start is max of predecessor finishes
            self.ES[current] = max((self.EF[p] for p in preds), default=0)
            self.EF[current] = self.ES[current] + self.durations[current]
            
            # Update successors
            for successor in self.adj[current]:
                self.indeg[successor] -= 1
                if self.indeg[successor] == 0:
                    queue.append(successor)
                    
        self.project_duration = max(self.EF.values()) if self.EF else 0

    def backward_pass(self):
        """Compute latest start and finish times."""
        if not self.EF:
            raise ValueError("Must run forward pass before backward pass")
            
        queue = deque([tid for tid in self.tasks if self.outdeg[tid] == 0])
        
        for tid in queue:
            self.LF[tid] = self.project_duration
            self.LS[tid] = self.LF[tid] - self.durations[tid]

        while queue:
            current = queue.popleft()
            for predecessor in self.rev_adj[current]:
                if predecessor not in self.LF:
                    self.LF[predecessor] = self.LS[current]
                else:
                    self.LF[predecessor] = min(self.LF[predecessor], self.LS[current])
                    
                self.LS[predecessor] = self.LF[predecessor] - self.durations[predecessor]
                self.outdeg[predecessor] -= 1
                
                if self.outdeg[predecessor] == 0:
                    queue.append(predecessor)

    def calculate_float(self):
        """Calculate float/slack for all tasks."""
        for tid in self.tasks:
            self.float[tid] = self.LS[tid] - self.ES[tid]

    def analyze(self):
        """Run full CPM analysis."""
        self.build_graph()
        self.forward_pass()
        self.backward_pass()
        self.calculate_float()
        return self.project_duration

    def get_critical_tasks(self) -> List[str]:
        """Get list of critical task IDs (zero float)."""
        return [tid for tid in self.tasks if self.float.get(tid, 0) == 0]

    def get_critical_paths(self) -> List[List[str]]:
        """Find all critical paths in the project."""
        critical_paths = []

        def depth_first_search(path: List[str]):
            """Recursive DFS to find critical paths."""
            last_task = path[-1]
            extended = False
            
            for successor in self.adj[last_task]:
                if self.float.get(successor, 0) == 0:
                    depth_first_search(path + [successor])
                    extended = True
                    
            if not extended:
                critical_paths.append(path)

        # Start from tasks with no predecessors that are critical
        for tid in self.tasks:
            if not self.dependencies.get(tid) and self.float.get(tid, 0) == 0:
                depth_first_search([tid])

        return critical_paths

    def run(self):
        """Convenience method to run full analysis."""
        self.analyze()
        return self