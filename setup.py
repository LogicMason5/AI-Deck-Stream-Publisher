from setuptools import setup, find_packages
from glob import glob
import os

package_name = "aideck_stream_publisher"

setup(
    name=package_name,
    version="0.1.0",
    packages=find_packages(exclude=["test"]),
    data_files=[
        # Required for ament index
        (
            "share/ament_index/resource_index/packages",
            [f"resource/{package_name}"],
        ),
        # Package manifest
        (f"share/{package_name}", ["package.xml"]),
        # Launch files
        (
            os.path.join("share", package_name, "launch"),
            glob(os.path.join("launch", "*.py")),
        ),
    ],
    install_requires=[
        "setuptools",
    ],
    zip_safe=True,
    maintainer="Miguel Granero",
    maintainer_email="miguelgranero99@gmail.com",
    description="ROS2 package for streaming and viewing AI-Deck video feed.",
    license="Apache License 2.0",
    tests_require=["pytest"],
    entry_points={
        "console_scripts": [
            "viewer = aideck_stream_publisher.viewer:main",
        ],
    },
)
