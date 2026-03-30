import os
import json
import pandas as pd

def get_latest_neurons():
    neurons = []
    path = os.path.expanduser("~/ARK_CORE/Forever_Learning")
    if not os.path.exists(path): return pd.DataFrame()
    for f in os.listdir(path):
        if f.startswith("aetheric_neuron") or f.startswith("spatial_neuron"):
            with open(os.path.join(path, f), "r") as j:
                data = json.load(j)
                neurons.append(data)
    return pd.DataFrame(neurons)
