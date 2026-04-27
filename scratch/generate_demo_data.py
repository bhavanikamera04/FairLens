import pandas as pd
import numpy as np

def generate_demo_data(n=200):
    np.random.seed(42)
    # Features: age, education_level, credit_score, gender
    genders = ['M', 'F']
    education_levels = ['High School', 'Bachelor', 'Master', 'PhD']
    
    data = []
    for _ in range(n):
        gender = np.random.choice(genders)
        education = np.random.choice(education_levels)
        age = np.random.randint(22, 65)
        
        # Base credit score influenced by age and education
        credit_score = 400 + (age * 5) + (education_levels.index(education) * 50) + np.random.randint(-50, 50)
        
        # Introduce some bias: Male candidates get a slight boost in 'approved' outcome
        # even if their credit score is similar, or gender is a proxy for something else
        # Or let's make it more interesting: 'Years at Job' is a proxy.
        years_at_job = max(0, age - 22 - np.random.randint(0, 5))
        
        # Outcome: 1 for Loan Approved, 0 for Rejected
        # Influence: Credit Score (high), Education (mid), Gender (bias factor)
        prob = 1 / (1 + np.exp(-( (credit_score - 650)/50 + (1 if gender == 'M' else -0.5) )))
        outcome = 1 if np.random.random() < prob else 0
        
        data.append({
            'gender': gender,
            'age': age,
            'education': education,
            'credit_score': credit_score,
            'years_at_job': years_at_job,
            'loan_approved': outcome
        })
    
    df = pd.DataFrame(data)
    df.to_csv('demo_data.csv', index=False)
    print("demo_data.csv generated with 200 rows.")

if __name__ == "__main__":
    generate_demo_data()
