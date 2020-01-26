from distutils.core import setup

setup(
    name='berry_cam_server',
    version='0.1',
    description='The webservice that stores the camera pictures taken by berry cam.'
                'Also has the possibility to notify the user about suspicious actions going on.',
    author='Felix Wohlfrom',
    author_email='TODO',
    packages=['berry_cam_server'],
    install_requires=['flask', 'flask-restx', 'PyYAML', 'Pillow', 'pytest', 'coverage']
)
