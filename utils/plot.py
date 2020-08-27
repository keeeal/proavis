
import os, json

import pandas as pd
import seaborn as sns

from utils import io

def plot(load_dir, filename='plot.png'):
    pops = io.load_dir(load_dir)
    data = {'gen':[], 'score':[], 'distance':[]}
    for gen, pop in pops:
        for i, f in pop:
            data['gen'].append(gen)
            data['score'].append(f[0])
            data['distance'].append(f[1])

    data = pd.DataFrame(data)
    plot = sns.lineplot(x='gen', y='score', data=data)
    fig = plot.get_figure()
    fig.savefig(filename)
    fig.clf()


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--load_dir', '-load', default='results')
    plot(**vars(parser.parse_args()))
