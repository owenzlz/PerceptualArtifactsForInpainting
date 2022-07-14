import torch
import torch.optim as optim
import torch.nn.functional as F
import pdb
from PIL import Image
import numpy as np 
import cv2
from skimage.io import imsave
from utils import get_mean_stdinv
from torch.autograd import Variable
from tqdm import tqdm
import argparse
import os

def numpy2tensor(img):
    img = torch.from_numpy(img).transpose(0,2).transpose(1,2).unsqueeze(0).float()
    return img

def prepare_img(img_file, args):
    img = np.array(Image.open(img_file)); H, W = img.shape[0], img.shape[1]
    mean_img, stdinv_img = get_mean_stdinv(img)
    img_tensor = numpy2tensor(img).to(args.device)
    mean_img_tensor = numpy2tensor(mean_img).to(args.device)
    stdinv_img_tensor = numpy2tensor(stdinv_img).to(args.device)
    img_tensor = img_tensor - mean_img_tensor
    img_tensor = img_tensor * stdinv_img_tensor
    return img_tensor

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--device', default=0, type=int)
    parser.add_argument('--ckpt_file', default='./ckpt/best_mIoU_iter_1800_torchscript.pth', type=str)
    parser.add_argument('--single_img', default=True, type=bool)
    parser.add_argument('--img_file', default='./demo/images/xxx.png', type=str)
    parser.add_argument('--img_folder', default='./demo/images', type=str)
    parser.add_argument('--results_dir', default='./demo/results', type=str)
    args = parser.parse_args()
    
    # Load the Perceptual Artifacts Localization network
    model = torch.load(args.ckpt_file)
    model = model.to(args.device)

    # Load images
    img_file = './data/rgb_optim/images/a_amusement_park_00000006.png'
    img_tensor = prepare_img(img_file)
    seg_logit = model(img_tensor)
    seg_pred = seg_logit.argmax(dim = 1)
    seg_pred_np = seg_pred.cpu().data.numpy()[0]
    seg_pred_np_expand = np.repeat(np.expand_dims(seg_pred_np, 2), 3, 2) * 255.0

    imsave('vis_artifacts.png', np.hstack([img, seg_pred_np_expand]))
    