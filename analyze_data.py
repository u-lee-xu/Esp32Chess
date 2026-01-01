import json

with open('chess_training_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f'Total samples: {len(data)}')
print(f'Samples with eval: {sum(1 for s in data if abs(s["eval"]) > 0.01)}')
print(f'Samples with only result: {sum(1 for s in data if abs(s["eval"]) <= 0.01)}')

evals = [s['eval'] for s in data if abs(s['eval']) > 0.01]
if evals:
    print(f'Eval range: {min(evals):.2f} to {max(evals):.2f}')
    print(f'Eval average: {sum(evals)/len(evals):.4f}')

results = [s['result'] for s in data]
print(f'Results - White wins: {results.count(1.0)}, Black wins: {results.count(-1.0)}, Draws: {results.count(0.0)}')