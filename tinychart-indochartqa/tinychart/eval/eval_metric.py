import os
import json
import math
import copy
import argparse
import numpy as np
from rapidfuzz.distance import Levenshtein

def write_jsonl(data, filename):
    with open(filename, 'w') as f:
        for item in data:
            f.write(json.dumps(item) + '\n')

def RelaxedAccuracy(pred, gt):
    """
    Numeric answer  -> Relaxed Accuracy (±5%)
    Text answer     -> ANLS
    """

    try:
        gt = float(gt)
        pred = float(pred)

        if gt == 0.0:
            return 1.0 if pred == gt else 0.0

        return 1.0 if abs(pred - gt) / abs(gt) <= 0.05 else 0.0

    except (ValueError, TypeError):
        # Jika bukan angka, gunakan ANLS
        return ANLS(pred, gt)

def ANLS(pred, gt, threshold=0.5):
    pred = str(pred).strip().lower()
    gt = str(gt).strip().lower()

    if len(gt) == 0:
        return float(len(pred) == 0)

    dist = Levenshtein.distance(pred, gt)
    score = 1 - dist / max(len(pred), len(gt))

    if score < threshold:
        score = 0.0

    return score
    
def evaluate_cmds(cmds):
    env = {"np": np}

    for cmd in cmds:
        exec(cmd, env)

    answer = env["Answer"]

    if (isinstance(answer, list) or isinstance(answer, np.ndarray)) and len(answer) == 1:
        answer = answer[0]

    # if isinstance(answer, list) or isinstance(answer, np.ndarray):
    #     new_answer = answer[0]
    #     for i in range(1, len(answer)-1):
    #         new_answer = new_answer + ', ' + answer[i]
    #     new_answer += ' and ' + answer[-1]
    #     answer = new_answer

    if isinstance(answer, list) or isinstance(answer, np.ndarray):
        answer = [str(x) for x in answer]
        new_answer = answer[0]
        for i in range(1, len(answer)-1):
            new_answer = new_answer + ', ' + answer[i]
        new_answer += ' and ' + answer[-1]
        answer = new_answer

    if isinstance(answer, (bool, np.bool_)):
        answer = "Yes" if answer else "No"

    return answer

def parse_model_output(cmdstr):
    lines = cmdstr.split('\n')
    new_lines = []
    for line in lines:
        if '<step>' in line or '</step>' in line:
            line = line.replace('<step>', '').replace('</step>', '')
            new_lines.append(line)
    return new_lines

def chartqa_evaluator(data, key='final_model_answer'):
    score_sum = 0
    for item in data:
        try:
            float(item['gt_answer'].split('<pot_note>')[0])
            item["metric"] = "Relaxed Accuracy"
        except:
            item["metric"] = "ANLS"
        
        item["score"] = RelaxedAccuracy(
            item[key],
            item['gt_answer'].split('<pot_note>')[0]
        )
    
        item["relaxed_acc"] = item["score"]
        score_sum += item["score"]
    
    accuracy = score_sum / len(data)
    return data, accuracy

def chartqapot_evaluator(output_data):
    # correct_items = []
    # wrong_items = []
    error_items = []
    score_sum = 0
    output_data = copy.deepcopy(output_data)

    for item in output_data:

        # -------------------------
        # Execute model program
        # -------------------------
        try:
            pred_cmds = parse_model_output(item["model_answer"])
            pred_answer = evaluate_cmds(pred_cmds)
            item["final_model_answer"] = str(pred_answer)
        except Exception:
            item["final_model_answer"] = "Execute <error>"
            item["relaxed_acc"] = 0.0
            error_items.append(item)
            continue

        # -------------------------
        # Execute GT program
        # -------------------------
        try:
            gt_cmds = parse_model_output(item["gt_answer"])
            gt_answer = evaluate_cmds(gt_cmds)
        except Exception:
            gt_answer = item["gt_answer"]

        item["final_gt_answer"] = str(gt_answer)
        
        print("=" * 80)
        print("QUESTION:")
        print(item["question"])
        
        print("\nGT PROGRAM:")
        print(item["gt_answer"])
        print("GT ANSWER:", gt_answer)
        
        print("\nMODEL PROGRAM:")
        print(item["model_answer"])
        print("MODEL ANSWER:", pred_answer)
        
        print()
        # -------------------------
        # Compare
        # -------------------------
        try:
            float(gt_answer)
            item["metric"] = "Relaxed Accuracy"
        except:
            item["metric"] = "ANLS"
    
        item["score"] = RelaxedAccuracy(str(pred_answer), str(gt_answer))
        item["relaxed_acc"] = item["score"]
        
        score_sum += item["score"]

    total = len(output_data)

    accuracy = score_sum / total
    error_rate = len(error_items) / total

    return output_data, accuracy, error_rate

def rule_based_divider(question):
    calculate_words = [
        'sum', 'difference', 'times', 'summation', 'exceed', 
        'below', 'addition', 'fewer', 'subtract', ' mode ', 
        'ratio', 'division', 'average', 'mean', 'bigger', 
        'greater', ' less ', 'tallest', 'number', 'divide', 
        ' add ', 'absolute', 'dividing', 'differ', ' minus ', 
        'how many colors', 'lowest', 'what is the value', 'higher', 
        'longer', ' biggest ', 'lowest'
    ]
        
    for w in calculate_words:
        if w in question.lower():
            return 'pot'
    return 'direct'

def chartqa_rule_merger_evaluator(direct_data, pot_data):
    direct_data, _ = chartqa_evaluator(direct_data, key='model_answer')
    assert len(direct_data) == len(pot_data), 'direct and pot num inconsistent'
    acc_count = 0
    merged_data = []
    for datum1, datum2 in zip(direct_data, pot_data):
        if rule_based_divider(datum1['question']) == 'pot' and '<error>' not in datum2['final_model_answer'] and datum2['final_model_answer'] not in ['inf', '-inf', 'nan', 'np.nan', 'np.inf', '-np.inf']:
            acc_count += datum2['relaxed_acc']
            merged_data.append(datum2)
        else:
            acc_count += datum1['relaxed_acc']
            merged_data.append(datum1)
    accuracy = acc_count/len(direct_data)
    return merged_data, accuracy

def chartqa_oracle_merger_evaluator(direct_data, pot_data):
    direct_data, _ = chartqa_evaluator(direct_data, key='model_answer')   
    assert len(direct_data) == len(pot_data), 'direct and pot num inconsistent'
    acc_count = 0
    merged_data = []
    for datum1, datum2 in zip(direct_data, pot_data):
        if datum1['relaxed_acc'] != 1.0:
            acc_count += datum2['relaxed_acc']
            merged_data.append(datum2)
        else:
            acc_count += datum1['relaxed_acc']
            merged_data.append(datum1)
    accuracy = acc_count/len(direct_data)
    return merged_data, accuracy


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--direct', default='../eval_iter12000_0226/ChartQA_test_12000_pred.jsonl')
    parser.add_argument('--pot', default='../eval_iter12000_0226/ChartQA_test_pot_12000_eval.jsonl')
    parser.add_argument('--output', default='../eval_iter12000_0226/ChartQA_test_pot_12000_merged.jsonl')
    
    args = parser.parse_args()
    
    # merged = oracle_merger(args.direct, args.pot)
    # merged = rule_based_merger(args.direct, args.pot)
    
    # write_jsonl(merged, args.output)  