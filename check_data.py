import json

# 加载数据
with open('chess_training_data_with_eval.json', 'r') as f:
    data = json.load(f)

print(f"Total samples: {len(data)}")
print(f"\nFirst sample keys: {list(data[0].keys())}")
print(f"Sample eval: {data[0]['eval']}")
print(f"Sample result: {data[0]['result']}")
print(f"Sample move: {data[0]['move']}")

# 统计评估值分布
evals = [s['eval'] for s in data]
print(f"\nEvaluation statistics:")
print(f"  Min: {min(evals):.3f}")
print(f"  Max: {max(evals):.3f}")
print(f"  Avg: {sum(evals)/len(evals):.3f}")

# 统计结果分布
results = [s['result'] for s in data]
print(f"\nResult distribution:")
print(f"  White wins: {results.count(1.0)}")
print(f"  Black wins: {results.count(-1.0)}")
print(f"  Draws: {results.count(0.0)}")