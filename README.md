# Sim-on-Wheels: Physical World in the Loop Simulation for Self-Driving (Renderer)
This is an official repo for the paper titled "Sim-on-Wheels: Physical World in the Loop Simulation for Self-Driving", RAL 2023

[Yuan Shen<sup>*</sup>](https://yshen47.github.io/),
[Bhargav Chandaka<sup>*</sup>](https://bchandaka.github.io),
[Zhi-Hao Lin](https://zhihao-lin.github.io),
[Albert Zhai](https://ajzhai.github.io),
[Hang Cui](https://hangpersonal.com),
[David Forsyth](http://luthuli.cs.uiuc.edu/~daf/),
[Shenlong Wang](https://shenlong.web.illinois.edu/)<br/>
Unversity of Illinois at Urbana-Champaign

(* denotes equal contribution)

[Project link](https://sim-on-wheels.github.io/) | [Paper link](https://arxiv.org/abs/2306.08807)

### Installment
Python environment: 3.9.12
```
pip install -r requirements.txt
```

### Download Scenario Assets and Example Sequences

#### Scenario Assets, including pre-baked agent animations, traffic assets, and others:
- create folder assets/ at the project root directory
- download assets and place this folder in the asset folder: [asset link with box](https://uofi.box.com/s/7h7w1jazgmgu7vpcrfnoackqt07axb2q) or [asset link with one drive](https://1drv.ms/f/s!AvOiKE0vFTuWik9ciMHq_pIxyD3T?e=tA2B8j)

#### KITTI-360
- create folder kitti360/ at the project root directory
- You only need one KITTI sequence, from [KITTI-360 dataset](https://www.cvlibs.net/datasets/kitti-360/download.php), download its Vechicle Poses (cam0_to_world.txt, poses.txt), and Perspective Images. 

#### Rosbag from our real-world captures
- create folder ros_sequences/ at the project root directory
- Download the rosbag sequence from [this link](https://drive.google.com/drive/folders/1yHUMqnT3Lz7-TBsCSvRaByM7l5fAjQz8?usp=share_link)

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
#### To run sim-on-wheels renderer on KITTI-360 sequences:
```
python kitti360.py
```

You can change this configuration file (configs/kitti360.yaml), to specify agent transform, movement, trigger conditions and agent types.  

#### To run sim-on-wheels renderer on real-world ROSBAG sequences:
```
python main.py
```

We provide different scenario configs examples in configs folder. You can load different config by changing config directory path in main.py:33. Our config yaml file can specify trigger distance condition, actor types, scenario types, and lighting related hyperparamters. 

### Citation
Please cite us if you use any part of our work:
```
@inproceedings{shen2023simonwheels,
  author={Shen, Yuan and Chandaka, Bhargav and Lin, Zhi-Hao and Zhai, Albert and Cui, Hang and Forsyth, David and Wang, Shenlong},
  journal={IEEE Robotics and Automation Letters}, 
  title={Sim-on-Wheels: Physical World in the Loop Simulation for Self-Driving}, 
  year={2023},
  volume={8},
  number={12},
  pages={8192-8199},
  doi={10.1109/LRA.2023.3325689}
}
```
