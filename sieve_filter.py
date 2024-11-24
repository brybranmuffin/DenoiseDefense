# from restack_ai.function import function, log
from dataclasses import dataclass
import sieve
import os.path
import shutil

def denoise(input: str):
   
    # log.info("denoise function started", input=input)

    file_path = input

    file = sieve.File(path=file_path)
    backend = "aicoustics"
    task = "all"
    enhancement_steps = 64

    audio_enhance = sieve.function.get("sieve/audio-enhance")
    output = audio_enhance.run(file, backend, task, enhancement_steps).path

    # log.info("denoise function completed", output=output)
    return output      


directory = './src/unedited/'

for filename in os.listdir(directory):
    output_path = denoise(directory + filename)
    new_directory = './src/edited_by_sieve/'
    print("copying from {} to {}".format(output_path, new_directory + "sieve_enhanced_" +filename))
    shutil.copy(output_path, new_directory + "sieve_enhanced_" +filename)
print("Done!")