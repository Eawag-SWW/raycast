from core import run_all
import numpy as np

neighborhood_size_list = np.arange(0.05, 0.3, 0.05)
min_samples_list = range(5, 30, 5)

# ugly loops
for size in neighborhood_size_list:
    for count in min_samples_list:
        print('######################## MIN SIZE: {}    MIN COUNT: {}'.format(size, count))
        # create custom settings
        settings_extra = {
            "clustering_3d": {
                "neighborhood_size": size,
                "min_samples": count
            }
        }
        # run clustering and evaluation
        run_all(settings_custom=settings_extra)
