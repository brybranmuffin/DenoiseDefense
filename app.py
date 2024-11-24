from openai import OpenAI
from groq import Groq
import os
import csv
import xlwt
from xlwt import Workbook


client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
clientBabylon = OpenAI(api_key='openbabylon',base_url=os.environ.get("OPENBABYLON_API_URL"))
directory_adobe = "./src/edited_by_adobe/"

directory_sieve = "./src/edited_by_sieve/"
inSieve = set()

contentDict = {}

for filename in os.listdir(directory_sieve):
    uuid = filename.split(".")[0].split('_')[2]
    inSieve.add(uuid)
    audio_file= open(directory_sieve + filename, "rb")
    transcription = client.audio.transcriptions.create(
        file=audio_file, # Required audio file
        model="whisper-large-v3-turbo", # Required model to use for transcription
        # Best practice is to write the prompt in the language of the audio, use translate.google.com if needed
        prompt=f"Опиши о чем речь в аудио",  # Translation: Describe what the audio is about
        language="ru", # Original language of the audio
        response_format="json",  # Optional
        temperature=0.0  # Optional
        )

    translation_prompt = f"""
            Instructions: Translate the following content from Russian to English. Output only the translated content.
            Content: {transcription}
            """
    response_sieve = clientBabylon.chat.completions.create(
        model="orpo-mistral-v0.3-ua-tokV2-focus-10B-low-lr-1epoch-aux-merged-1ep",
        messages=[{"role": "user", "content": translation_prompt}],
        temperature=0.0
    )
    contentDict[uuid] = [response_sieve.choices[0].message]
    print("Sieve uuid output {} has been written to data".format(uuid))


for filename in os.listdir(directory_adobe):
    uuid = filename.split('.')[0].split('-')[0]
    if not uuid in inSieve:
        continue
    audio_file= open(directory_adobe + filename, "rb")
    transcription = client.audio.transcriptions.create(
        file=audio_file, # Required audio file
        model="whisper-large-v3-turbo", # Required model to use for transcription
        # Best practice is to write the prompt in the language of the audio, use translate.google.com if needed
        prompt=f"Опиши о чем речь в аудио",  # Translation: Describe what the audio is about
        language="ru", # Original language of the audio
        response_format="json",  # Optional
        temperature=0.0  # Optional
        )

    translation_prompt = f"""
            Instructions: Translate the following content from Russian to English. Output only the translated content.
            Content: {transcription}
            """
    response_adobe = clientBabylon.chat.completions.create(
        model="orpo-mistral-v0.3-ua-tokV2-focus-10B-low-lr-1epoch-aux-merged-1ep",
        messages=[{"role": "user", "content": translation_prompt}],
        temperature=0.0
    )
    contentDict[uuid].append(response_adobe.choices[0].message)
    print("Adobe uuid output {} has been written to data".format(uuid))

data = [["Audio ID", "Sieve Output", "Adobe Output"]]

print("Creating xls workbook...")

wb = Workbook()
sheet1 = wb.add_sheet("Sheet 1")

print("Writing data to workbook...")
i = 0
for k, v in contentDict.items():
    sheet1.write(i,0,k)
    sheet1.write(i,1,str(v[0]))
    sheet1.write(i,2,str(v[1]))
    i+= 1


xls_file_path = "sieve_vs_adobe.xls"
wb.save(xls_file_path)

# print("Writing to CSV...")
# with open(csv_file_path, mode='w', newline='') as file:
#     writer = csv.writer(file)
#     writer.writerows(data)

print("XLS file written to {}".format(xls_file_path))




# response_adobe = clientBabylon.chat.completions.create(
#     model="orpo-mistral-v0.3-ua-tokV2-focus-10B-low-lr-1epoch-aux-merged-1ep",
#     messages=messages_adobe,
#     temperature=0.0
# )

# response_sieve = clientBabylon.chat.completions.create(
#     model="orpo-mistral-v0.3-ua-tokV2-focus-10B-low-lr-1epoch-aux-merged-1ep",
#     messages=messages_sieve,
#     temperature=0.0
# )

# print("Babylon Translation")
# print(response_sieve.choices[0].message.content)
# print(response_adobe.choices[0].message.content)

