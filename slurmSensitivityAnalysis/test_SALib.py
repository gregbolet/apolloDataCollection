from SALib.sample import saltelli
from SALib.analyze import sobol
from SALib.test_functions import Ishigami
import numpy as np

# Define the model inputs
problem = {
    'num_vars': 3,
    'names': ['x1', 'x2', 'x3'],
    'bounds': [[-3.14159265359, 3.14159265359],
               [-3.14159265359, 3.14159265359],
               [-3.14159265359, 3.14159265359]]
}

# Generate samples
#param_values = saltelli.sample(problem, 1024)
param_values = saltelli.sample(problem, 8)
print('points to sample', param_values)

# Run model (example)
print('sampling model...')
Y = Ishigami.evaluate(param_values)

# Perform analysis
print('doing analysis:')
Si = sobol.analyze(problem, Y, print_to_console=True)

print('results:')
# Print the first-order sensitivity indices
print(Si['S1'])