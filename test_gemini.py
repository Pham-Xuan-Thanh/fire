"""
Test script for FIRE framework with Google Gemini 2.5 Flash model
Based on evaluator.ipynb
"""

import os
import json
import dataclasses
import tqdm
import time
from common.modeling import Model
from common.shared_config import google_api_key, serper_api_key
from eval.fire.verify_atomic_claim import verify_atomic_claim

# Set API keys
os.environ["GOOGLE_API_KEY"] = google_api_key
os.environ["SERPER_API_KEY"] = serper_api_key

# Configuration
model_name = 'google:gemini-3-flash'
benchmark = 'factcheckbench'
framework = 'fire'
num_samples = 3  # Test với 3 claims đầu tiên

print(f'=== FIRE Framework Test with Gemini 2.5 Flash ===')
print(f'Benchmark: {benchmark}')
print(f'Model: {model_name}')
print(f'Number of samples: {num_samples}')
print()

# Initialize model
print('Loading model...')
rater = Model(model_name, temperature=0.5, max_tokens=2048)
print('✅ Model loaded successfully!')
print()

# Track results
failed_cnt = 0
total_usage = {
    'input_tokens': 0,
    'output_tokens': 0,
}
results = []

# Read and process claims
print('Processing claims...')
data_file = f'datasets/{benchmark}/data.jsonl'
output_file = f'results/{framework}_{benchmark}_gemini-2.5-flash.jsonl'

with open(output_file, 'w') as fout:
    lines = open(data_file, 'r').readlines()[:num_samples]
    
    for i, line in enumerate(tqdm.tqdm(lines, desc="Verifying claims")):
        data = json.loads(line)
        claim = data['claim']
        label = data['label']
        
        print(f'\n[{i+1}/{num_samples}] Claim: {claim}')
        print(f'    Expected Label: {label}')
        
        # Run fact-checking
        result, searches, usage = verify_atomic_claim(claim, rater)
        
        # Track token usage
        if usage is not None:
            total_usage['input_tokens'] += usage['input_tokens']
            total_usage['output_tokens'] += usage['output_tokens']
        
        if result is None:
            print(f'    ❌ Failed to verify')
            failed_cnt += 1
            continue
        
        predicted = result.answer
        is_correct = predicted.lower() == label.lower()
        print(f'    Predicted: {predicted}')
        print(f'    Result: {"✅ Correct" if is_correct else "❌ Wrong"}')
        print(f'    Searches: {len(searches.get("google_searches", []))}')
        
        # Write result
        fout.write(json.dumps({
            'claim': claim,
            'label': label,
            'result': dataclasses.asdict(result),
            'searches': searches
        }) + '\n')
        time.sleep(30)

# Summary
print('\n' + '='*50)
print('SUMMARY')
print('='*50)
print(f'Total claims: {num_samples}')
print(f'Failed claims: {failed_cnt}')
print(f'Success rate: {(num_samples - failed_cnt) / num_samples * 100:.1f}%')
print()
print('Token Usage:')
print(f'  Input tokens: {total_usage["input_tokens"]}')
print(f'  Output tokens: {total_usage["output_tokens"]}')
print(f'  Total tokens: {total_usage["input_tokens"] + total_usage["output_tokens"]}')
print()
print(f'Results saved to: {output_file}')
