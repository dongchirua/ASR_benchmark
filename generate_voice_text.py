import pandas as pd
import numpy as np
import json
import codecs
from tqdm import tqdm
import random
import click
from string import Template
from typing import Tuple


def generate_text_voice(templates, finding: str) -> Tuple:
    prob_add, prob_del, prob_modify, prob_nothing = random.uniform(0, 1), \
                                                    random.uniform(0, 1), \
                                                    random.uniform(0, 1), \
                                                    random.uniform(0, 1)
    ind_case = np.argmax([prob_add, prob_del - 0.2, prob_modify, prob_nothing])
    if ind_case == 0:
        case = 'modify'
    elif ind_case == 1:
        case = 'delete'
    elif ind_case == 2:
        case = 'add'
    else:
        case = 'nothing'
    if templates.get(case, None) is not None:
        number = int(random.randint(1, 10))
        example = random.sample(templates[case]['sentences'], 1)[0]

        mapping_dict = {}
        for i in list(templates[case].keys()):
            mapping_dict[i] = random.sample(templates[case][i], 1)[0]
        mapping_dict['what'] = finding

        example = Template(example)
        text = example.substitute(mapping_dict)
        text = Template(text).substitute(number=number)
        return text, case, number
    else:
        return finding, None, None


@click.command()
@click.option('--template_path')
@click.option('--data_path')
@click.option('--n_samples')
def run(template_path, data_path, n_samples, save_path):
    templates = json.loads(codecs.open(template_path, 'r', 'UTF-8').read())
    database = pd.read_excel(data_path)
    database = database['refined'].tolist()
    records = []
    for finding in tqdm(database):
        tmp = []
        for j in range(n_samples):
            rec_ = generate_text_voice(templates, finding)
            tmp.append(rec_)
        tmp = list(set(tmp))
        records = records + tmp
    df = pd.DataFrame(records, columns=['sentence', 'action', 'location'], dtype=str)
    df.to_csv(save_path, index=False, encoding='UTF-8')


if __name__ == "__main__":
    run()
