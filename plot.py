
import os, json

import pandas as pd
import seaborn as sns

def main():

    root, pops = 'results', {}
    for item in os.listdir(root):
        if item.endswith('.json'):
            with open(os.path.join(root, item)) as f:
                pops[int(os.path.splitext(item)[0])] = json.load(f)

    data = {'gen':[], 'score':[], 'distance':[]}
    for gen, pop in pops.items():
        for fit in pop['fitness']:
            data['gen'].append(gen)
            data['score'].append(fit[0])
            data['distance'].append(fit[1])

    data = pd.DataFrame(data)
    plot = sns.lineplot(x='gen', y='score', data=data)
    plot.fig.savefig('plot.png')


if __name__ == '__main__':
    main()