# Sim-on-wheels-Renderer

### Installment
Python environment: 3.9.12
```
pip install -r requirements.txt
```

### Download Scenario Assets and Example Sequences

#### Scenario Assets, including pre-baked agent animations, traffic assets, and others:
- create folder assets/ at the project root directory
- download assets and place this folder in the asset folder: [asset link](https://uofi.box.com/s/7h7w1jazgmgu7vpcrfnoackqt07axb2q)

#### KITTI-360
- create folder kitti360/ at the project root directory
- You only need one KITTI sequence, from [KITTI-360 dataset](https://www.cvlibs.net/datasets/kitti-360/download.php), download its Vechicle Poses (cam0_to_world.txt, poses.txt), and Perspective Images. 

The kitti360 folder should be arranged as follows:
```
kitti360   
└───data_2d_raw
    └───2013_05_28_drive_0000_sync
           └───image_00
                  └───data_rect
└───data_poses   
    └───2013_05_28_drive_0000_sync
           └───cam0_to_world.txt
           └───poses.txt
```

### Run
To run sim-on-wheels renderer on KITTI-360 sequences:
```
python kitti360.py
```
