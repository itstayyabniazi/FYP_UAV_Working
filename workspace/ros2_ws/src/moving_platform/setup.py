import os
from glob import glob

from setuptools import find_packages, setup

package_name = 'moving_platform'

# Recursively install everything under models/, preserving directory
# structure, instead of naming files individually -- the previous explicit
# list (model.sdf, model.config) predated materials/textures/aruco_marker.png
# and silently never installed it: GZ_SIM_RESOURCE_PATH pointing at the
# colcon install tree found the model directory fine, but the texture file
# itself was never copied there, so Gazebo still couldn't resolve
# model://moving_platform/materials/textures/aruco_marker.png at spawn time.
def _model_data_files():
    entries = []
    for dirpath, _, filenames in os.walk('models'):
        if not filenames:
            continue
        install_dir = os.path.join('share', package_name, dirpath)
        files = [os.path.join(dirpath, f) for f in filenames]
        entries.append((install_dir, files))
    return entries


setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        *_model_data_files(),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='zanan',
    maintainer_email='zanan@todo.todo',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'moving_platform_node = moving_platform.moving_platform_node:main',
        ],
    },
)
