from setuptools import find_packages, setup

package_name = 'uwb_visualizer'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', ['launch/multi_tag.launch.py']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='incsl-nuc',
    maintainer_email='incsl-nuc@todo.todo',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
		'uwb_tag_publisher = uwb_visualizer.uwb_tag_publisher:main'
        ],
    },
)
