import pickle

# Safe model: Simple Python object without dangerous code execution
safe_model = {"model_type": "safe", "weights": [0.1, 0.2, 0.3]}
with open("safe_model.pkl", "wb") as safe_file:
    pickle.dump(safe_model, safe_file)

print("File created: 'safe_model.pkl'")

