import os
from bayes_opt import BayesianOptimization
from bayes_opt import UtilityFunction
from sklearn.gaussian_process.kernels import Matern, DotProduct
from sklearn.gaussian_process import GaussianProcessRegressor

# Below we use the suggest-evaluate-register paradigm
RANDOM_STATE_SEED = 1783

def black_box_function(x, y):
	return -x ** 2 - (y - 1) ** 2 + 1

# Bounded region of parameter space
pbounds = {'x': (2, 4), 'y': (-3, 3)}

# NOTE: Increase the alpha parameter with a noisy space
# Default kernel: Matern 2.5
optim = BayesianOptimization(
    f=None,
    pbounds=pbounds,
		random_state=RANDOM_STATE_SEED
)

# Acquisition Function = Utility Function
# ucb = Upper Confidence Bound
# ei = Expected Improvement
# pi = Probability of Improvement
util = UtilityFunction(kind="ucb", kappa=2.5, xi=0.0)

next_point_to_probe = optim.suggest(util)
print("Next point to probe is:", next_point_to_probe)

target = black_box_function(**next_point_to_probe)
print("Found the target value to be:", target)

# Add the new sampled point to the known data of the model
optim.register(
    params=next_point_to_probe,
    target=target,
)


# Let's change the kernel
print(optim._gp.get_params())
optim.set_gp_params(kernel=Matern(nu=3.3))
print(optim._gp.get_params())
optim.set_gp_params(kernel=DotProduct())
print(optim._gp.get_params())

# Possible covariance kernels:
# Matern (RBF generalization -- can control smoothness with nu)
# RBF (aka: square exponential kernel)
# DotProduct
# Quadratic
# WhiteKernel
# ConstantKernel
# RotationalQuadratic
# ExpSineSquared





