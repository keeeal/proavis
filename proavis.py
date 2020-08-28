
import os, time
from itertools import count
from functools import partial
from random import random, randint, choices
from threading import Thread
from subprocess import call

import pyautogui as gui
from deap import base, creator, tools, algorithms

from utils.io import save, load_all


# start the game
def start_game(exe_path):
    call(['wine', exe_path])


# evaluate an individual by playing the game once
def evaluate(individual, click_delay, click_pos, retry_pos,
             hiscores, deathlog, bot_hiscores, bot_deathlog):

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


# crossover at a random point biased towards the end
def cxOnePointBiased(ind1, ind2, bias):
    n = min(len(ind1), len(ind2))
    p = choices(range(n), map(lambda x: (1-bias)**(n-x), range(n)))[0]
    ind1[p:], ind2[p:] = ind2[p:], ind1[p:]

    return ind1, ind2


# mutate attributes randomly with a bias towards the end
def mutUniformIntBiased(ind, low, up, indpb, bias):
    n = len(ind)
    p = choices(range(n), map(lambda x: (1-bias)**(n-x), range(n)))[0]
    for i in range(p, n):
        if random() < indpb:
            ind[i] = randint(low, up)

    return ind,


# print the fitness statistics of a population
def print_stats(population, generation=None):
    fitnesses = [i.fitness.values for i in population]
    scores, dists = list(zip(*fitnesses))

    if generation is not None:
        print('== GEN {} =='.format(generation))
    print('max score:\t{}'.format(int(max(scores))))
    print('avg score:\t{}'.format(int(sum(scores)/len(scores))))
    print('max dist:\t{}'.format(int(max(dists))))
    print('avg dist:\t{}'.format(int(sum(dists)/len(dists))))


# save the population and print statistics
class Results:
    def __init__(self, save_dir):
        self.save_dir = save_dir
        self.gen = 0

    def update(self, population):
        save(self.save_dir, population, self.gen)
        print_stats(population, self.gen)
        self.gen += 1


def main(difficulty, p_cross, p_mutate, p_flip, bias,
         n_pop, n_gen, load_dir=None):

    retry_pos = 3080, 780  # location of the retry button
    click_pos = 3160, 780  # somewhere else inside the game window
    click_delay = 0.01     # delay added between actions

    # path to where the game stores high scores and death logs
    root = '/home/j/.wine/drive_c/users/j/Local Settings/Application Data/'
    root += 'Chicken_Wings_2020_test_ver_{}/'.format(difficulty)
    hiscores = os.path.join(root, 'hiscores.txt')
    deathlog = os.path.join(root, 'deathlog.txt')

    # path to where results will be stored
    results_dir = 'results'
    bot_hiscores = os.path.join(results_dir, 'bot_hiscores.txt')
    bot_deathlog = os.path.join(results_dir, 'bot_deathlog.txt')

    # define fitness
    creator.create('Fitness', base.Fitness, weights=(1., 1.))
    creator.create('Individual', list, fitness=creator.Fitness)

    # register an individual and a population
    t = base.Toolbox()
    t.register('individual', tools.initRepeat, creator.Individual, 0, n=0)
    t.register('population', tools.initRepeat, list, t.individual, n=n_pop)

    # register evolutionary operators
    t.register("mate", cxOnePointBiased, bias=bias)
    t.register("mutate", mutUniformIntBiased,
        low=-1, up=1, indpb=p_flip, bias=bias)
    t.register("select", tools.selTournament, tournsize=3)
    t.register("evaluate",
        partial(evaluate, click_delay=click_delay, click_pos=click_pos,
            retry_pos=retry_pos, hiscores=hiscores, deathlog=deathlog,
            bot_hiscores=bot_hiscores, bot_deathlog=bot_deathlog)
    )

    # create folder to save results
    if not os.path.isdir(results_dir):
        os.mkdir(results_dir)
    open(bot_hiscores, 'w').close()
    open(bot_deathlog, 'w').close()
    res = Results(results_dir)

    # initialise the algorithm
    if load_dir:
        history = load_all(load_dir, creator.Individual)
        res.gen, init_pop = history[-1]
        for gen, pop in history:
            print_stats(pop, gen)
    else:
        init_pop = t.population()

    # start the game
    exe_path = os.path.join('/home/j/chicken_wings/{}.exe'.format(difficulty))
    game = Thread(target=start_game, args=(exe_path,), daemon=True)
    game.start()
    time.sleep(10)

    # begin training
    ea = algorithms.eaMuPlusLambda
    ea(init_pop, t, n_gen, n_gen, p_cross, p_mutate, n_gen, None, res, False)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--difficulty', '-d',
        choices=['easy', 'medium', 'hard'], default='easy')
    parser.add_argument('--p-cross', '-px', type=float, default=.5)
    parser.add_argument('--p-mutate', '-pm', type=float, default=.2)
    parser.add_argument('--p-flip', '-pf', type=float, default=.1)
    parser.add_argument('--bias', '-b', type=float, default=.05)
    parser.add_argument('--n-pop', '-n', type=int, default=64)
    parser.add_argument('--n-gen', '-g', type=int, default=1000)
    parser.add_argument('--load_dir', '-load')
    main(**vars(parser.parse_args()))
