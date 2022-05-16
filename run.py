from quick_start import create_single_data, predict_joints, predict_skeleton, predict_skinning, tranfer_to_ori_mesh

from models.GCN import JOINTNET_MASKNET_MEANSHIFT as JOINTNET
from models.ROOT_GCN import ROOTNET
from models.PairCls_GCN import PairCls as BONENET
from models.SKINNING import SKINNET

import torch

import os
import sys
import glob

def delete_normalized_files(base_path):
    data_path = os.path.join(os.getcwd(), base_path)
    normalized_files = glob.glob(os.path.join(data_path, '*_normalized.*')) + glob.glob(os.path.join(data_path, '*_normalized_simplified.*'))

    for normalized_file in normalized_files:
        try:
            os.remove(normalized_file)
        except Exception as err:
            print(f'Failed to delete file "{normalized_file}". Reason: {err}')

if __name__ == '__main__':
    global device

    if len(sys.argv) < 3:
        print('At least two arguments are required')
        sys.exit(-1)

    input_folder = 'data'

    # Comment this call if you want to keep intermediate files produced by a previous run.
    delete_normalized_files(input_folder)

    high_res_model_filename = sys.argv[1]
    low_res_model_filename = sys.argv[2]

    bandwidth = 0.0429
    threshold = 1e-6

    if len(sys.argv) > 3:
        bandwidth = float(sys.argv[3])
        if len(sys.argv) > 4:
            threshold = float(sys.argv[4])

    print('running with:')
    print(f'- high res model: "{high_res_model_filename}"')
    print(f'- low res model:  "{low_res_model_filename}"')
    print(f'- bandwidth:      "{bandwidth}"')
    print(f'- threshold:      "{threshold}"')

    # downsample_skinning is used to speed up the calculation of volumetric geodesic distance
    # and to save cpu memory in skinning calculation.
    # Change to False to be more accurate but less efficient.
    downsample_skinning = True

    device_name = 'cuda:0' if torch.cuda.is_available() else 'cpu'
    print(f'running with device "{device_name}"')
    device = torch.device(device_name)

    # load all weights
    print('loading all networks...')

    jointNet = JOINTNET()
    jointNet.to(device)
    jointNet.eval()
    jointNet_checkpoint = torch.load('checkpoints/gcn_meanshift/model_best.pth.tar')
    jointNet.load_state_dict(jointNet_checkpoint['state_dict'])
    print('     joint prediction network loaded.')

    rootNet = ROOTNET()
    rootNet.to(device)
    rootNet.eval()
    rootNet_checkpoint = torch.load('checkpoints/rootnet/model_best.pth.tar')
    rootNet.load_state_dict(rootNet_checkpoint['state_dict'])
    print('     root prediction network loaded.')

    boneNet = BONENET()
    boneNet.to(device)
    boneNet.eval()
    boneNet_checkpoint = torch.load('checkpoints/bonenet/model_best.pth.tar')
    boneNet.load_state_dict(boneNet_checkpoint['state_dict'])
    print('     connection prediction network loaded.')

    skinNet = SKINNET(nearest_bone=5, use_Dg=True, use_Lf=True)
    skinNet_checkpoint = torch.load('checkpoints/skinnet/model_best.pth.tar')
    skinNet.load_state_dict(skinNet_checkpoint['state_dict'])
    skinNet.to(device)
    skinNet.eval()
    print('     skinning prediction network loaded.')

    # create data used for inferece
    print(f'creating data for model {low_res_model_filename}')
    mesh_filename = os.path.join(input_folder, low_res_model_filename)
    data, vox, surface_geodesic, translation_normalize, scale_normalize = create_single_data(mesh_filename)
    data.to(device)

    print('predicting joints')
    data = predict_joints(data, vox, jointNet, threshold, bandwidth=bandwidth,
                          mesh_filename=mesh_filename.replace('.obj', '_normalized.obj'))
    data.to(device)
    print('predicting connectivity')
    pred_skeleton = predict_skeleton(data, vox, rootNet, boneNet,
                                     mesh_filename=mesh_filename.replace('.obj', '_normalized.obj'))
    print('predicting skinning')
    pred_rig = predict_skinning(device, data, pred_skeleton, skinNet, surface_geodesic,
                                mesh_filename.replace('.obj', '_normalized.obj'),
                                subsampling=downsample_skinning)

    # here we reverse the normalization to the original scale and position
    pred_rig.normalize(scale_normalize, -translation_normalize)

    print('Saving result')
    # here we use original mesh tesselation (without remeshing)
    mesh_filename_ori = os.path.join(input_folder, high_res_model_filename)
    pred_rig = tranfer_to_ori_mesh(mesh_filename_ori, mesh_filename, pred_rig)
    pred_rig.save(mesh_filename_ori.replace('.obj', '_rig.txt'))

    normalized_files = glob.glob('*_normlalized.*') + glob.glob('*_normlalized_simplified.*')
    print(normalized_files)

    print('Done!')
