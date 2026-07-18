from setuptools import find_packages, setup
import os
from glob import glob

package_name = 'robot_move_1'

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
    maintainer='rama',
    maintainer_email='ramageorgius@gmail.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            "read_ulson = robot_moving_1.read_ulson_1:main",
            "madgwick_data = robot_moving_1.madgwick_data:main",
        ],
    },
)
