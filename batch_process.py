"""
Batch process multiple mortgage applications from JSON file
"""

import json
import sys
from main import run_mortgage_validation

def process_json_file(filename):
    """Process mortgage applications from JSON file"""
    
    try:
        with open(filename, 'r') as f:
            applications = json.load(f)
            
        if not isinstance(applications, list):
            applications = [applications]
            
        print("BATCH MORTGAGE VALIDATION")
        print("=" * 80)
        
        results = []
        
        for i, app in enumerate(applications, 1):
            print(f"\n{i}. Processing: {app['applicant_name']}")
            print("-" * 40)
            
            try:
                result = run_mortgage_validation(app)
                
                print(f"Decision: {result['final_decision']}")
                print(f"Confidence: {result['confidence_score']:.1f}%")
                print(f"Reason: {result['decision_reason']}")
                
                results.append({
                    'applicant': app['applicant_name'],
                    'decision': result['final_decision'],
                    'confidence': result['confidence_score'],
                    'reason': result['decision_reason']
                })
                
            except Exception as e:
                print(f"Error processing {app['applicant_name']}: {e}")
                results.append({
                    'applicant': app['applicant_name'],
                    'error': str(e)
                })
        
        print("\n" + "=" * 80)
        print("SUMMARY")
        print("=" * 80)
        
        approved = sum(1 for r in results if r.get('decision') == 'APPROVED')
        rejected = sum(1 for r in results if r.get('decision') == 'REJECTED')
        pending = sum(1 for r in results if r.get('decision') == 'PENDING_REVIEW')
        errors = sum(1 for r in results if 'error' in r)
        
        print(f"Approved: {approved}")
        print(f"Rejected: {rejected}")
        print(f"Pending Review: {pending}")
        print(f"Errors: {errors}")
        print(f"Total Processed: {len(results)}")
        
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found")
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in file '{filename}': {e}")
    except Exception as e:
        print(f"Error: {e}")

def main():
    if len(sys.argv) != 2:
        print("Usage: python batch_process.py <json_file>")
        print("Example: python batch_process.py sample_applications.json")
        sys.exit(1)
    
    filename = sys.argv[1]
    process_json_file(filename)

if __name__ == "__main__":
    main()