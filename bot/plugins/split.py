# GOAL:
# getting track for logging

import logging

LOGGER = logging.getLogger(__name__)

# GOAL:
# create split handler class

from os import path as os_path, remove as os_remove
import asyncio
from glob import glob
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser

async def func(filepath, size):
    if not os_path.isfile(filepath):
        return False

    cmd = [
        "split",
        "--numeric-suffixes=1",
        "--suffix-length=3",
        f"--bytes={size}",
        filepath,
        filepath + "."
    ]
    LOGGER.debug(cmd)

    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    await process.communicate()

    list = glob(filepath + ".*").sort()
    LOGGER.debug(list)
    return list

async def ffmpeg(filepath, size):
    supported = ['.mp4','.mkv','.avi','.webm','.wmv','.mov']
    if not os_path.isfile(filepath):
        yield False
    
    file_path_name, file_ext = os_path.splitext(filepath)
    if not file_ext in supported:
        yield False

    metadata = extractMetadata(createParser(filepath))
    if not metadata.has("duration"):
        yield False

    total_duration = metadata.get("duration").seconds

    splited_duration = 0
    i = 0

    while splited_duration < total_duration:    
        i+=1
        out_file = file_path_name + ".{:03d}".format(i) + file_ext
        cmd = [
            "ffmpeg",
            "-hide_banner",
            "-i",
            filepath,
            "-ss",
            str(splited_duration),
            "-fs",
            str(size * 9/10),
            "-async",
            "1",
            "-c",
            "copy",
            out_file
        ]
        LOGGER.debug(cmd)

        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        await process.communicate()
        

        metadata = extractMetadata(createParser(out_file))
        if not metadata.has("duration"):
            os_remove(out_file)
            return False
        splited_duration += metadata.get("duration").seconds
        
        yield out_file