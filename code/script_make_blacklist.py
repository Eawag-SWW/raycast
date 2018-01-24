'''
certain objects are not visible in certain pictures. These cases are identified in the training thumbnails
and placed in a folder.

This script reads the files in the folder and creates a list of image-inlet combinations to be excluded when
creating training thumbnails
'''

import default_settings as s
import pandas as pd
import os.path as op
from glob import glob

def main():
    blacklist_folder = 'C:/temp/raycast/adliswil_new/preparations/s04__extract_initial_samples/positives_blacklist'

    image_paths = glob(op.join(blacklist_folder, '*.jpg'))

    gt_ids = [get_id_from_path(p) for p in image_paths]
    gt_imgs = [get_img_from_path(p) for p in image_paths]

    df = pd.DataFrame({
        "id": gt_ids,
        "img": gt_imgs
    })

    df.to_csv('Q:/Abteilungsprojekte/eng/SWWData/Matthew/Workspace/raycast/demo_data/ground_truth_blacklist.csv', index=False)

    return df

def get_id_from_path(path):
    bn = op.basename(path)
    return bn.split('_')[0]

def get_img_from_path(path):
    bn = op.basename(path)
    return '_'.join(bn.split('_')[1:3])

main()