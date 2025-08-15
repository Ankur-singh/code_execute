# Test script for the Python execution service

# Test 1: Simple return value
def main():
    return {"message": "Hello, World!", "value": 42}

# Test 2: With stdout (should not appear in result)
def main():
    print("This is stdout")
    print("This is also stdout")
    return {"result": "success"}

# Test 3: With numpy
def main():
    import numpy as np
    arr = np.array([1, 2, 3, 4, 5])
    return {"sum": int(np.sum(arr)), "mean": float(np.mean(arr))}

# Test 4: With pandas
def main():
    import pandas as pd
    df = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})
    return df.to_dict()

# Test 5: Error case
def main():
    raise ValueError("This is a test error")