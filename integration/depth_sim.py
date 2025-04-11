import cv2
import glob
import matplotlib
import numpy as np
import os
import torch
import json
from depth_anything_v2.dpt import DepthAnythingV2


class DepthSim():
    def __init__(self):
        pass

    def run(self):

        print('Hello from depth sim')

        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        img_path = config['img_path']
        encoder = config['encoder']
        outdir = config['outdir']
        input_size = config['input_size']
        
        DEVICE = 'cuda' if torch.cuda.is_available() else 'mps' if torch.backends.mps.is_available() else 'cpu'
        
        model_configs = {
            'vits': {'encoder': 'vits', 'features': 64, 'out_channels': [48, 96, 192, 384]},
            'vitb': {'encoder': 'vitb', 'features': 128, 'out_channels': [96, 192, 384, 768]},
            'vitl': {'encoder': 'vitl', 'features': 256, 'out_channels': [256, 512, 1024, 1024]},
            'vitg': {'encoder': 'vitg', 'features': 384, 'out_channels': [1536, 1536, 1536, 1536]}
        }
        
        depth_anything = DepthAnythingV2(**model_configs[encoder])
        depth_anything.load_state_dict(torch.load(f'depth_anything_v2_{encoder}.pth', map_location='cpu', weights_only=True))
        depth_anything = depth_anything.to(DEVICE).eval()
        
        if os.path.isfile(img_path):
            if img_path.endswith('txt'):
                with open(img_path, 'r') as f:
                    filenames = f.read().splitlines()
            else:
                filenames = [img_path]
        else:
            filenames = glob.glob(os.path.join(img_path, '**/*'), recursive=True)
        
        os.makedirs(outdir, exist_ok=True)
        
        cmap = matplotlib.colormaps.get_cmap('Spectral_r')
        
        for k, filename in enumerate(filenames):
            print(f'Depth Progress {k+1}/{len(filenames)}: {os.path.basename(filename)}')
            
            raw_image = cv2.imread(filename)
            
            depth = depth_anything.infer_image(raw_image, input_size)
            
            depth = (depth - depth.min()) / (depth.max() - depth.min()) * 255.0
            depth = depth.astype(np.uint8)
            
            out_path = os.path.join(outdir, os.path.splitext(os.path.basename(filename))[0] + '.png')
            cv2.imwrite(out_path, depth)
        
        print("Depth Simulation Done!")

if __name__ == "__main__":
    ds = DepthSim()
    ds.run()