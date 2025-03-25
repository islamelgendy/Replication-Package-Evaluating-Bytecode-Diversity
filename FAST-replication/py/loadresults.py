import pickle

# Load the saved pickle file
# output/math_v0/prioritized/FAST-pw-bbox-2.pickle
# results/prioritized_per_subject/math_v0/FAST-pw-bbox-2.pickle
# /home/islam/MyWork/Code/FAST-replication/input/math_v0/fault_matrix.pickle
with open("output/compress_v16/prioritized/FAST-pw-bbox-5.pickle", "rb") as f:
    loaded_prioritization = pickle.load(f)

print(loaded_prioritization)