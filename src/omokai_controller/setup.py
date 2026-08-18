from glob import glob

from setuptools import find_packages, setup

package_name = 'omokai_controller'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(),
    data_files=[
        (
            'share/ament_index/resource_index/packages',
            ['resource/' + package_name]
        ),
        (
            'share/' + package_name,
            ['package.xml']
        ),
        (
            'share/' + package_name + '/launch',
            [
                'launch/simulation.launch.py',
                'launch/omokai.launch.py'
            ]
        ),
        (
            'share/' + package_name + '/missions',
            glob('missions/*.json')
        ),
        (
            'share/' + package_name + '/simulation/worlds',
            glob('simulation/worlds/*.sdf')
        ),
        (
            'share/' + package_name + '/simulation/models/vehicle_blue',
            glob('simulation/models/vehicle_blue/*')
        ),
        (
            'share/' + package_name + '/test',
            glob('test/*.py')
        ),
    ],

    install_requires=[
        'setuptools',
        'requests',
    ],
    tests_require=[
        'pytest',
    ],
    zip_safe=True,
    maintainer='aswin',
    maintainer_email='aswin@todo.todo',
    description='Omokai robot controller',
    license='TODO',
    entry_points={
        'console_scripts': [
            'square_controller = omokai_controller.square_controller:main',
        ],
    },
)
