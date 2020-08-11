
import os, json

import pandas as pd
import seaborn as sns

from utils import io

def main(load_dir):
    pops = io.load_dir(load_dir)
    data = {'gen':[], 'score':[], 'distance':[]}
    for gen, (pop, fit) in pops:
        for i, f in zip(pop, fit):
            data['gen'].append(gen)
            data['score'].append(fit[0])
            data['distance'].append(fit[1])

    data = pd.DataFrame(data)
    plot = sns.lineplot(x='gen', y='score', data=data)
    plot.fig.savefig('plot.png')


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--load_dir', '-load', default='results')
    main(**vars(parser.parse_args()))