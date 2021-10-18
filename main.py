from random import sample
from matplotlib import pyplot as plt
import numpy as np
import population_initialization
import os
import pickle


class DifferentialEvolution:
    def __init__(self, cost_function, bounds, max_iterations,
                 population_size, mutation, crossover, strategy, population_initialization_algorithm):
        self.cost_function = cost_function
        self.max_iterations = max_iterations
        self.population_size = population_size
        self.mutation = mutation
        self.crossover = crossover
        self.bounds = bounds
        self.population = []
        self.strategy = strategy
        self.generation = 0
        self.generation_best_individual = None
        self.generation_best_individual_idx = None
        self.best_individual_history = []
        self.generation_fitness = []
        self.initial_population = population_initialization_algorithm

    def initialize(self):
        if self.initial_population == "random":
            self.population = population_initialization.random_initialization(self.population_size, self.bounds)
        elif self.initial_population == "obl":
            self.population = population_initialization.obl_initialization(self.population_size,
                                                                           self.bounds, self.cost_function)
        elif self.initial_population == "tent":
            self.population = population_initialization.tent_initialization(self.population_size, self.bounds)
        elif self.initial_population == "qobl":
            self.population = population_initialization.qobl_initialization(self.population_size,
                                                                            self.bounds, self.cost_function)
        elif self.initial_population == "sobol":
            # # TODO various polynomials, various m numbers
            self.population = population_initialization.sobol_initialization(self.population_size, self.bounds)

    def evolve(self):
        self.generation = 0
        while self.generation < self.max_iterations:
            self.generation_fitness = []
            self.generation += 1
            self.get_best()
            self.best_individual_history.append(self.generation_best_individual)
            for idx, individual in enumerate(self.population):
                crossover_candidates = self.generate_crossover_candidates(idx)
                new_individual = []
                random_dimension = np.random.randint(0, len(individual))
                for dimension in range(len(individual)):
                    cr = np.random.uniform(0, 1)
                    if cr > self.crossover or random_dimension != dimension:
                        new_individual.append(individual[dimension])
                    else:
                        # check boundaries, if violation, random generate new one
                        new_individual.append(self.mutate(crossover_candidates, dimension))

                if self.cost_function(new_individual) < self.cost_function(individual):
                    self.population[idx] = new_individual
                self.generation_fitness.append(self.cost_function(self.population[idx]))
            if self.generation % 1000 == 0:
                print("generation: ", self.generation, ", best solution:", self.get_best())
            # measure diversity here?

    def generate_crossover_candidates(self, idx):
        crossover_candidates = [idx]
        while idx in crossover_candidates:
            crossover_candidates = sample(range(self.population_size - 1), 6)
        if self.strategy == "DE/rand/1":
            return crossover_candidates[:3]
        elif self.strategy == "DE/rand/2":
            return crossover_candidates
        elif self.strategy == "DE/best/1":
            crossover_candidates[0] = self.generation_best_individual_idx
            return crossover_candidates[:3]
        elif self.strategy == "DE/best/2":
            crossover_candidates[0] = self.generation_best_individual_idx
            return crossover_candidates
        elif self.strategy == "DE/current-to-best/1":
            crossover_candidates[0] = self.generation_best_individual_idx
            crossover_candidates[1] = idx
            return crossover_candidates[:4]
        elif self.strategy == "DE/current-to-best/2":
            crossover_candidates[0] = self.generation_best_individual_idx
            crossover_candidates[1] = idx
            return crossover_candidates
        elif self.strategy == "DE/current-to-rand/1":
            crossover_candidates[0] = idx
            return crossover_candidates[:4]
        elif self.strategy == "DE/current-to-rand/2":
            crossover_candidates[0] = idx
            return crossover_candidates[:6]

    def mutate(self, crossover_candidates, dimension):
        if self.strategy == "DE/rand/1" or self.strategy == "DE/best/1":
            return self.population[crossover_candidates[0]][dimension] + \
                   self.mutation[0] * (self.population[crossover_candidates[1]][dimension] -
                                       self.population[crossover_candidates[2]][dimension])
        elif self.strategy == "DE/rand/2" or self.strategy == "DE/best/2":
            return self.population[crossover_candidates[0]][dimension] + \
                   self.mutation[0] * (self.population[crossover_candidates[1]][dimension] -
                                       self.population[crossover_candidates[2]][dimension]) + \
                   self.mutation[0] * (self.population[crossover_candidates[3]][dimension] -
                                       self.population[crossover_candidates[4]][dimension])
        elif self.strategy == "DE/current-to-best/1":
            return self.population[crossover_candidates[1]][dimension] + \
                   self.mutation[0] * (self.population[crossover_candidates[0]][dimension] -
                                       self.population[crossover_candidates[1]][dimension]) +\
                   self.mutation[1] * (self.population[crossover_candidates[2]][dimension] -
                                       self.population[crossover_candidates[3]][dimension])
        elif self.strategy == "DE/current-to-best/2":
            return self.population[crossover_candidates[1]][dimension] + \
                   self.mutation[0] * (self.population[crossover_candidates[0]][dimension] -
                                       self.population[crossover_candidates[1]][dimension]) + \
                   self.mutation[1] * (self.population[crossover_candidates[2]][dimension] -
                                       self.population[crossover_candidates[3]][dimension]) + \
                   self.mutation[1] * (self.population[crossover_candidates[4]][dimension] -
                                       self.population[crossover_candidates[5]][dimension])
        elif self.strategy == "DE/current-to-rand/1":
            return self.population[crossover_candidates[0]][dimension] + \
                   self.mutation[0] * (self.population[crossover_candidates[1]][dimension] -
                                       self.population[crossover_candidates[0]][dimension]) + \
                   self.mutation[1] * (self.population[crossover_candidates[2]][dimension] -
                                       self.population[crossover_candidates[3]][dimension])
        elif self.strategy == "DE/current-to-rand/2":
            return self.population[crossover_candidates[0]][dimension] + \
                   self.mutation[0] * (self.population[crossover_candidates[1]][dimension] -
                                       self.population[crossover_candidates[0]][dimension]) + \
                   self.mutation[1] * (self.population[crossover_candidates[2]][dimension] -
                                       self.population[crossover_candidates[3]][dimension]) + \
                   self.mutation[1] * (self.population[crossover_candidates[4]][dimension] -
                                       self.population[crossover_candidates[5]][dimension])

    def get_best(self):
        best_cost = np.inf
        best = np.inf
        best_idx = np.inf
        for idx, individual in enumerate(self.population):
            cost = self.cost_function(individual)
            if cost < best_cost:
                best = individual
                best_cost = cost
                best_idx = idx
        self.generation_best_individual = best
        self.generation_best_individual_idx = best_idx
        return best

    def filter_history(self, dimension):
        solutions = [solution[dimension] for solution in self.best_individual_history]
        return solutions

    def measure_diversity(self, measure):
        if measure == "std-fitness":
            return np.std(self.generation_fitness)


def function_to_minimize(x):
    return x[0] ** 2 + x[1] ** 2


if __name__ == '__main__':
    from testing_functions import gpd_ll_function as sphere_function
    from gpd_tests import generate_data
    experiments = 1000
    total_runs = 100
    shape_bounds = [-2, 2]
    scale_bounds = [0, 2]
    max_iterations = 100
    population_size = 100
    mutation = [0.8, 0.8]
    crossover = 0.7
    strat = "DE/current-to-best/1"
    sample_size = 100
    if not os.path.exists(os.path.join("de_results", str(sample_size))):
        os.makedirs(os.path.join("de_results", str(sample_size)))
    for experiment in range(experiments):
        generate_data(shape_bounds, scale_bounds, sample_size, experiment)

        for single_run in range(total_runs):

            diff_evolution = DifferentialEvolution(sphere_function, bounds=[shape_bounds, scale_bounds], max_iterations=max_iterations,
                                               population_size=population_size,  mutation=mutation, crossover=crossover,
                                               strategy=strat, population_initialization_algorithm="random")
            diff_evolution.initialize()
            diff_evolution.evolve()
            de_results = open(os.path.join("de_results", str(sample_size), "gpd_experiment{:0>4d}".format(experiment)), "ab")
            to_dump = {"experiment": experiment,
                       "run": single_run,
                       "sample_size": sample_size,
                       "result": diff_evolution.get_best(),
                       "max_iterations": max_iterations,
                       "population_size": population_size,
                       "mutation": mutation,
                       "crossover": crossover,
                       "strategy": strat}
            pickle.dump(to_dump, de_results)
            de_results.close()
            print("experiment: ", experiment, "run: ", single_run, "the best solution: ", diff_evolution.get_best())
