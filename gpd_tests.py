from scipy.stats import genpareto
import matplotlib.pyplot as plt
import pickle
import random
import os


def generate_data(shape_bounds, scale_bounds, sample_size, experiment):
    shape_param = random.uniform(shape_bounds[0], shape_bounds[1])
    scale_param = random.uniform(scale_bounds[0], scale_bounds[1])
    print(shape_param, scale_param)
    r = genpareto.rvs(shape_param, loc=0, scale=scale_param, size = sample_size)
    data_file = open("gpd_sample", "wb")
    pickle.dump(r, data_file)
    data_file.close()
    if not os.path.exists(os.path.join("gpd_datasets", str(sample_size))):
        os.makedirs(os.path.join("gpd_datasets", str(sample_size)))
    experiment_file = open(os.path.join("gpd_datasets", str(sample_size), "gpd_experiment{:0>4d}".format(experiment)), "ab")
    to_dump = {"gpd_data": r, "gpd_fit": genpareto.fit(r, floc=min(r)), "gpd_shape": shape_param, "gpd_scale": scale_param}
    pickle.dump(to_dump, experiment_file)
    experiment_file.close()
    print("scipy fit: ", genpareto.fit(r, floc=min(r)))
    print("true data min: ", min(r))


# fig, ax = plt.subplots(1, 1)
#
# c = 0.1
# r = genpareto.rvs(-1, loc=0, scale=1, size=1000)
#
# dbfile = open('gpd_sample', 'wb')
# pickle.dump(r, dbfile)
# dbfile.close()
#
# ax.hist(r, density=True, histtype='stepfilled', alpha=0.2)
# ax.legend(loc='best', frameon=False)
# plt.show()
#
# print(genpareto.fit(r))
