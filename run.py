import argparse
from src.generator import generate_dataset
from src.validation import validate_dataset
from src.config import DATA_DIR

p=argparse.ArgumentParser(description="Generate and validate YottaFlex synthetic CRM dataset")
p.add_argument("--seed",type=int,default=20261022)
p.add_argument("--reps",type=int,default=2000)
p.add_argument("--accounts",type=int,default=2000)
p.add_argument("--opportunities",type=int,default=20000)
p.add_argument("--quarters",type=int,default=8)
p.add_argument("--output",default=str(DATA_DIR))
a=p.parse_args()
print(generate_dataset(a.output,a.seed,a.reps,a.accounts,a.opportunities,a.quarters))
print(validate_dataset(a.output))
