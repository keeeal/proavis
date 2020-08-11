
import os, json

def save(root, population, gen=0):
    fitness = [i.fitness.values for i in population]
    save_file = os.path.join(root, '{}.json'.format(gen))
    with open(save_file, 'w') as f:
        json.dump({'population': population, 'fitness': fitness}, f)

def load(root, gen=0, ind_class=None):
    save_file = os.path.join(root, '{}.json'.format(gen))
    with open(save_file) as f:
        data = json.load(f)

    pop, fit = data['population'], data['fitness']
    if ind_class:
        pop_fit = []
        for i, f in zip(pop, fit):
            pop_fit.append(ind_class(i))
            pop_fit[-1].fitness.values = fit
            pop_fit[-1].fitness.valid = True

        return pop_fit

    return list(zip(pop, fit))

def load_dir(root, ind_class=None):
    past_gens = []
    for item in os.listdir(root):
        if item.endswith('.json'):
            gen = int(os.path.splitext(item)[0])
            pop = load(root, ind_class, gen)
            past_gens.append((gen, pop))

    return sorted(past_gens)