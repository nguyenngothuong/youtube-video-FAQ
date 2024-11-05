from setuptools import setup, find_packages

setup(
    name="youtube_transcript_extractor",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'yt-dlp',
        'youtube-transcript-api',
        'tqdm',
        'colorama',
    ],
) 