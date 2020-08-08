
import os, time, json
from itertools import count
from random import random as rand
from random import randint

import pyautogui as gui
from deap import base, creator, tools, algorithms

retry_pos = 1160, 780  # location of the retry button
click_pos = 1240, 780  # somewhere else inside the game window
click_delay = 0.01     # delay added between actions

# path to where the game stores high scores and death logs
root = '/home/j/.wine/drive_c/users/j/Local Settings/Application Data/Chicken_Wings_2020_test_ver_easy/'
hiscores = os.path.join(root, 'hiscores.txt')
deathlog = os.path.join(root, 'deathlog.txt')

# path to where results will be stored
results_dir = 'results'
bot_hiscores = os.path.join(results_dir, 'bot_hiscores.txt')
bot_deathlog = os.path.join(results_dir, 'bot_deathlog.txt')


# evaluate an individual by playing the game once
def evaluate(individual):

    # clear the game files and get ready
    open(hiscores, 'w').close()
    open(deathlog, 'w').close()
    gui.moveTo(*retry_pos, duration=1)
    time.sleep(4)

    # start the game
    for _ in range(3):
        gui.mouseDown()
        time.sleep(.01)
        gui.mouseUp()
        time.sleep(.01)

    gui.moveTo(*click_pos)

    for i in count():
        with open(hiscores) as f:
            hiscores_line = f.readline()

        # check if the game is over
        if hiscores_line:
            with open(deathlog) as f:
                deathlog_line = f.readline()

            # save bot hiscores and deathlog
            with open(bot_hiscores, 'a+') as f:
                f.write(hiscores_line)
            with open(bot_deathlog, 'a+') as f:
                f.write(deathlog_line)

            # update individual and fitness
            individual = individual[:i]
            score = int(hiscores_line.split(',')[1])
            dist = int(deathlog_line.split(',')[3])
            return score, dist

        # -1: release, 0: wait, 1: click
        if i >= len(individual):
            individual.append(randint(-1, 1))
        if individual[i]:
            gui.mouseUp(click_pos)
            if 0 < individual[i]:
                gui.mouseDown(click_pos)

        # add delay
        time.sleep(click_delay)


# mutate attributes starting from a randomly chosen point
def mutUniformIntAfterPt(individual, low, up, indpb):
    size = len(individual)
    start = randint(0, size - 1)

    for i in range(start, size):
        if rand() < indpb:
            individual[i] = randint(low, up)

    return individual,


# save the population and print statistics
class Results:
    def __init__(self, save_dir):
        self.save_dir = save_dir
        self.gen = 0

    def update(self, population):
        fitness = [i.fitness.values for i in population]
        scores, dists = list(zip(*fitness))

        # save population and fitness
        save_file = '{}.json'.format(self.gen)
        save_file = os.path.join(self.save_dir, save_file)
        with open(save_file, 'w') as f:
            json.dump({'population': population, 'fitness': fitness}, f)

        # print statistics
        print('== GEN {} =='.format(self.gen))
        print('max score:\t{}'.format(int(max(scores))))
        print('avg score:\t{}'.format(int(sum(scores)/len(scores))))
        print('max dist:\t{}'.format(int(max(dists))))
        print('avg dist:\t{}'.format(int(sum(dists)/len(dists))))
        self.gen += 1


def main(p_cross, p_mutate, p_flip, n_pop, n_gen, init_pop):

    # define fitness
    creator.create('Fitness', base.Fitness, weights=(1., 1.))
    creator.create('Individual', list, fitness=creator.Fitness)

    # register an individual and a population
    t = base.Toolbox()
    t.register('individual', tools.initRepeat, creator.Individual, 0, n=0)
    t.register('population', tools.initRepeat, list, t.individual, n=n_pop)

    # register evolutionary operators
    t.register("mate", tools.cxOnePoint)
    t.register("mutate", mutUniformIntAfterPt, low=-1, up=1, indpb=p_flip)
    t.register("select", tools.selTournament, tournsize=3)
    t.register("evaluate", evaluate)

    # create folder to save results
    if not os.path.isdir(results_dir):
        os.mkdir(results_dir)
    open(bot_hiscores, 'w').close()
    open(bot_deathlog, 'w').close()
    res = Results(results_dir)

    # initialise the algorithm
    alg = algorithms.eaSimple
    if not init_pop:
        init_pop = t.population()

    # begin training
    alg(init_pop, t, p_cross, p_mutate, n_gen, None, res, False)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--p-cross', '-px', type=float, default=.5)
    parser.add_argument('--p-mutate', '-pm', type=float, default=.2)
    parser.add_argument('--p-flip', '-pf', type=float, default=.1)
    parser.add_argument('--n-pop', '-n', type=int, default=64)
    parser.add_argument('--n-gen', '-g', type=int, default=1000)
    parser.add_argument('--init-pop', '-init')
    main(**vars(parser.parse_args()))
