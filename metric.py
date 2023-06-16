import os
from PIL import Image
import numpy as np
import torch
import lpips 
from skimage.metrics import structural_similarity as calculate_ssim

def compute_psnr(gt, pred):
    '''image size: (h, w, 3) 
    should be normalized in (0, 1)'''
    mse = np.mean((gt - pred)**2)
    psnr = -10. * np.log(mse) / np.log(10)
    return psnr 

def compute_ssim(gt, pred):
    '''image size: (h, w, 3)'''
    ssim = calculate_ssim(pred, gt, data_range=gt.max() - gt.min(), channel_axis=-1)
    return ssim

class ComputeLPIPS():
    def __init__(self, device='cuda'):
        self.device = device 
        self.model = lpips.LPIPS(net='alex').to(device)
    
    def __call__(self, image_0, image_1):
        '''images are normalized in (0, 1)'''
        image_0 = torch.tensor(image_0).to(self.device)
        image_1 = torch.tensor(image_1).to(self.device)
        image_0 = image_0.permute(2, 0, 1)
        image_1 = image_1.permute(2, 0, 1)
        out = self.model(image_0, image_1)
        val = out.item()
        return val 

def read_image(path):
    image = Image.open(path)
    image = np.array(image)[:,:,:3]
    image = (image / 255).astype(np.float32)
    return image

def test():
    root = 'ros_sequences/reality/00_crop/'
    img_gt = read_image(os.path.join(root, 'gt/cone.png'))
    img_render = read_image(os.path.join(root, 'render/cone.png'))

    psnr = compute_psnr(img_gt, img_render)
    ssim = compute_ssim(img_gt, img_render)
    compute_lpips = ComputeLPIPS()
    lpips = compute_lpips(img_gt, img_render)

    print('PSNR:  {:.3f}'.format(psnr))
    print('SSIM:  {:.3f}'.format(ssim))
    print('LPIPS: {:.3f}'.format(lpips))

def main():
    root_dir = 'ros_sequences/reality/00_crop/'
    gt_dir = os.path.join(root_dir, 'gt')
    render_dir = os.path.join(root_dir, 'render')
    items = ['bench', 'chair_b', 'chair_o', 'cone', 
        'ladder', 'trolley',]# 'yuan', 'zhihao']
    n_items = len(items)

    compute_lpips = ComputeLPIPS()

    psnr_list  = []
    ssim_list  = []
    lpips_list = []
    
    for i in range(n_items):
        path_gt = os.path.join(gt_dir, '{}.png'.format(items[i]))
        path_render = os.path.join(render_dir, '{}.png'.format(items[i]))
        img_gt = read_image(path_gt)
        img_render = read_image(path_render)

        psnr = compute_psnr(img_gt, img_render)
        ssim = compute_ssim(img_gt, img_render)
        lpips = compute_lpips(img_gt, img_render)

        print('======== {} ========'.format(items[i]))
        print('PSNR:  {:.3f}'.format(psnr))
        print('SSIM:  {:.3f}'.format(ssim))
        print('LPIPS: {:.3f}'.format(lpips))

        psnr_list.append(psnr)
        ssim_list.append(ssim)
        lpips_list.append(lpips)

    print('======= Overall =======')
    print('PSNR:  {:.3f}'.format(np.mean(psnr)))
    print('SSIM:  {:.3f}'.format(np.mean(ssim)))
    print('LPIPS: {:.3f}'.format(np.mean(lpips)))

if __name__ == '__main__':
    main()
    # test()