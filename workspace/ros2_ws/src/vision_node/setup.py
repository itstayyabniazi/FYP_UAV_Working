from setuptools import find_packages, setup

package_name = 'vision_node'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='zanan',
    maintainer_email='zanan@todo.todo',
    description=(
        'ArUco marker-based vision perception for the moving-platform '
        'landing target (camera -> LandingTarget -> RLObservation), the '
        'deployment/demo counterpart to the ground-truth training path.'
    ),
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'aruco_landing_target_node = vision_node.aruco_landing_target_node:main',
            'vision_relative_state_node = vision_node.vision_relative_state_node:main',
        ],
    },
)
