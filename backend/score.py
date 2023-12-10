import numpy as np
import os
import pandas as pd
from utils import *
import time
import psutil
from multiprocessing import Manager, Queue, Process

# feature: 1.number of weighted neighbors(all types) 2. rules for elimination
# 3.(possible) consider jumps and corresponding neighbors
# method: record and iterate scores
domain_weight = {
    'r_cert': 18,  # 很强
    'r_subdomain': 1,
    'r_request_jump': 2,
    'r_dns_a': 10,
    'r_whois_name': 0.1,  # 较强
    'r_whois_email': 0.1,
    'r_whois_phone': 0.1,
    'r_cert_chain': 0,  # 一般
    'r_cname': 0.02,
    'r_asn': 0,  # 较弱
    'r_cidr': 0
}
ip_weight = {
    'r_cert': 0,  # 很强
    'r_subdomain': 0,
    'r_request_jump': 0,
    'r_dns_a': 1,
    'r_whois_name': 0,  # 较强
    'r_whois_email': 0,
    'r_whois_phone': 0,
    'r_cert_chain': 0,  # 一般
    'r_cname': 0,
    'r_asn': 0.01,  # 较弱
    'r_cidr': 0.01
}
cert_weight = {
    'r_cert': 1,  # 很强
    'r_subdomain': 0,
    'r_request_jump': 0,
    'r_dns_a': 0,
    'r_whois_name': 0,  # 较强
    'r_whois_email': 0,
    'r_whois_phone': 0,
    'r_cert_chain': 0.1,  # 一般
    'r_cname': 0,
    'r_asn': 0,  # 较弱
    'r_cidr': 0
}


def mutil_run(input_list: list, link, domains: dict, scores_dict: dict, scores: dict):
    step=0
    for i, node_row in input_list:
        # if i==1000:
            # np.save('../data/score_1_fil.npy', scores)
            # np.save('../data/score_dict_fil.npy', dict(scores_dict))
            # np.save('../data/domains.npy', domains)
        step+=1
        print(step)
        score = 0
        ips = 0
        for j, link_row in link[(link['source'] == node_row['id']) | (link['target'] == node_row['id'])].iterrows():
            type = link_row['relation']
            if node_row['type'] == 'Domain':
                if type == 'r_dns_a':
                    ips += 1
                score += domain_weight[type]
            elif node_row['type'] == 'IP':
                score += ip_weight[type]
            elif node_row['type'] == 'Cert':
                score += cert_weight[type]
        if ips > 1:
            domains[node_row['Unnamed: 0']] = 1
        if score == 0:
            score = value[node_row['type']]
        scores[node_row['Unnamed: 0']] = score
        scores_dict[node_row['id']] = score

def mutil_run1(input_list: list, link,scores_dict: dict, scores: dict):
    step=0
    for i, node_row in input_list:
        step+=1
        print(step)
        score = 0
        if node_row['type'] == 'IP' or node_row['type'] == 'Cert':
            for j, link_row in link[link['target'] == node_row['id']].iterrows():
                score += scores_dict[link_row['source']] if link_row['source'] in scores_dict else 0
        elif node_row['type'] == 'Domain':
            for j, link_row in link[link['source'] == node_row['id']].iterrows():
                score += scores_dict[link_row['target']] if link_row['target'] in scores_dict else 0
        scores[node_row['Unnamed: 0']]=score


def process_data():
    # node = pd.read_csv('data/Nodefil.csv')
    # link = pd.read_csv('data/Linkfil.csv')
    node = pd.read_csv('data/Node.csv')
    link = pd.read_csv('data/Link.csv')
    # print(node,link)
    # select data without nan
    node = node.dropna()
    node = node.drop_duplicates('id', keep='first')
    link = link.dropna()
    link = link.drop_duplicates()
    # print(node)
    # print(link.shape,node)
    # time.sleep(100)
    # id = np.array(node.index.values)
    # type = np.array(type_value[node['type'][i]] for i in range(node.shape[0]))
    # industry = np.array(0 if node['industry'][i] == '[]' else 1 for i in range(node.shape[0]))

    scores = Manager().dict()
    scores_dict = Manager().dict()
    domains = Manager().dict()
    # np.save('data/score_1.npy', dict(scores))
    # np.save('data/score_dict.npy', dict(scores_dict))
    # np.save('data/domains.npy', dict(domains))

    new_node = node[(node['industry'] != '[]') |
                    (node['type'] != 'Domain')]
    t = time.time()
    input_list = list(new_node.iterrows())
    # print(input_list[10000][1]['Unnamed: 0'])
    # for i in input_list:
    #     print(i[1]['id'])
    # time.sleep(1000)
    # print([0][0])
    # print()
    # print(input_list[0][1])
    num_cpu = 16
    p_list = [Process(target=mutil_run, args=(
    input_list[i * len(input_list) // num_cpu:(i + 1) * len(input_list) // num_cpu], link, domains, scores_dict,
    scores)) for i in range(num_cpu)]
    for p in p_list:
        p.start()
    for p in p_list:
        p.join()
    print(time.time()-t)
    # for i, node_row in :
    #     input_list.append([i,node_row])
    # score = 0
    # ips = 0
    # print(i)
    # for j, link_row in link[(link['source'] == node_row['id']) | (link['target'] == node_row['id'])].iterrows():
    #     type = link_row['relation']
    #     if node_row['type'] == 'Domain':
    #         if type == 'r_dns_a':
    #             ips += 1
    #         score += domain_weight[type]
    #     elif node_row['type'] == 'IP':
    #         score += ip_weight[type]
    #     elif node_row['type'] == 'Cert':
    #         score += cert_weight[type]
    # if ips > 1:
    #     domains.append(i)
    # if scores == 0:
    #     scores = value[node_row['type']]
    # scores.append(score)
    # scores_dict[node_row['id']] = score
    # #print(scores)
    # if i % 5e4 == 0:
    #     print(i)
    #     print(time.time()-t)

    # np.save('../data/score_1.npy', dict(scores))
    # np.save('../data/score_dict.npy', dict(scores_dict))
    # np.save('../data/domains.npy', dict(domains))



    scores1 = Manager().dict()

    t = time.time()
    num_cpu = 16
    p_list = [Process(target=mutil_run1, args=(
    input_list[i * len(input_list) // num_cpu:(i + 1) * len(input_list) // num_cpu], link, scores_dict,
    scores1)) for i in range(num_cpu)]
    for p in p_list:
        p.start()
    for p in p_list:
        p.join()
    print(time.time()-t)

    np.save('data/score.npy', dict(scores1))



    # scores_2 = []
    # t = time.time()
    #
    # for i, node_row in new_node.iterrows():
    #     score = 0
    #     if node_row['type'] == 'IP' or node_row['type'] == 'Cert':
    #         for j, link_row in link[link['target'] == node_row['id']].iterrows():
    #             score += scores_dict[link_row['source']] if link_row['source'] in scores_dict else 0
    #     elif node_row['type'] == 'Domain':
    #         for j, link_row in link[link['source'] == node_row['id']].iterrows():
    #             score += scores_dict[link_row['target']] if link_row['target'] in scores_dict else 0
    #     scores_2.append(score)
    #     if i % 5e4 == 0:
    #         print(i)
    #         print(time.time() - t)
    # np.save('../data/score_2_fil.npy', np.array(scores_2))


if __name__ == '__main__':
    process_data()
