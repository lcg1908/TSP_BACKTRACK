# src/algorithms/aco_solver.py
import time
import random
import math
from .base_solver import BaseSolver 

class ACOSolver(BaseSolver):

    def __init__(self, tsp_problem):
        super().__init__(tsp_problem)

        self.num_ants = 20
        self.max_iterations = 100
        
        self.alpha = 1.0  
        self.beta = 2.0   
        self.rho = 0.5    
        self.Q = 100      
        
        self.pheromone_matrix = []
        self.heuristic_matrix = [] 

    def solve(self, update_callback=None, finish_callback=None, sleep_time=0.05):

        self.is_running = True
        self.start_timer()

        matrix = self.tsp_problem.dist_matrix
        num_cities = self.tsp_problem.num_cities

        if num_cities == 0:
            self.stop_timer()
            if finish_callback:
                finish_callback(self.best_path, self.min_cost, self.runtime)
            return

        self._initialize_matrices(num_cities, matrix)
        
        print("Bắt đầu chạy ACO...")

        try:
            for iteration in range(self.max_iterations):

                if not self.is_running:
                    print("ACO bị dừng.")
                    break
                
                all_ant_paths = self._construct_ant_solutions(num_cities, matrix)

                self._update_pheromones(all_ant_paths)

                if sleep_time > 0:
                    time.sleep(sleep_time)

        except Exception as e:
            print(f"Lỗi xảy ra trong ACO: {e}")
        
        self.stop_timer()
        if finish_callback:
            finish_callback(self.best_path, self.min_cost, self.runtime)
        
        print(f"ACO hoàn thành. Chi phí: {self.min_cost}, Thời gian: {self.runtime:.4f}s")

    def _initialize_matrices(self, num_cities, matrix):

        self.pheromone_matrix = [[1.0] * num_cities for _ in range(num_cities)]
        
        self.heuristic_matrix = [[0.0] * num_cities for _ in range(num_cities)]
        for i in range(num_cities):
            for j in range(num_cities):
                if i != j and matrix[i][j] > 0:
                    self.heuristic_matrix[i][j] = 1.0 / matrix[i][j]
                else:
                    self.heuristic_matrix[i][j] = 0.0

    def _construct_ant_solutions(self, num_cities, matrix):
        all_ant_paths = []
        
        for _ in range(self.num_ants):

            if not self.is_running:
                break

            path, cost = self._build_single_ant_path(num_cities, matrix)
            all_ant_paths.append((path, cost))

            if cost < self.min_cost:
                self.min_cost = cost
                self.best_path = path

        return all_ant_paths

    def _calculate_probabilities(self, current_city, visited, num_cities):
        probabilities = [0.0] * num_cities
        total_prob = 0.0
        
        for next_city in range(num_cities):
            if not visited[next_city] and self.heuristic_matrix[current_city][next_city] > 0:

                pher = self.pheromone_matrix[current_city][next_city] ** self.alpha
                heu = self.heuristic_matrix[current_city][next_city] ** self.beta

                probabilities[next_city] = pher * heu
                total_prob += probabilities[next_city]

        if total_prob > 0:
            for city in range(num_cities):
                probabilities[city] /= total_prob

        return probabilities
        
    def _build_single_ant_path(self, num_cities, matrix):

        start_city = random.randint(0, num_cities - 1)

        path = [start_city]
        visited = [False] * num_cities
        visited[start_city] = True

        for _ in range(num_cities - 1):

            if not self.is_running:
                break

            current = path[-1]
            probs = self._calculate_probabilities(current, visited, num_cities)

            next_city = self._roulette_select(probs)

            path.append(next_city)
            visited[next_city] = True

        path.append(start_city)

        cost = self.tsp_problem.get_path_cost(path)

        return (path, cost)

    def _roulette_select(self, probabilities):
        r = random.random()
        cumulative = 0.0

        for city, prob in enumerate(probabilities):
            cumulative += prob
            if r <= cumulative:
                return city

        return probabilities.index(max(probabilities))

    def _update_pheromones(self, all_ant_paths):
        num_cities = self.tsp_problem.num_cities

        for i in range(num_cities):
            for j in range(num_cities):
                self.pheromone_matrix[i][j] *= (1.0 - self.rho)

        for path, cost in all_ant_paths:
            if cost <= 0:
                continue 

            pheromone_delta = self.Q / cost

            for k in range(len(path) - 1):
                i = path[k]
                j = path[k+1]

                self.pheromone_matrix[i][j] += pheromone_delta
                self.pheromone_matrix[j][i] += pheromone_delta
