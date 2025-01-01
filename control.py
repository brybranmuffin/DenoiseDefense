from openai import OpenAI
from groq import Groq
import os
import csv
import xlwt
from xlwt import Workbook


client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
clientBabylon = OpenAI(api_key='openbabylon',base_url=os.environ.get("OPENBABYLON_API_URL"))
directory_control = "./src/unedited_extended/"
directory_results = "./src/control_results/"

contentDict = {}
processedFiles = set()
for filename in os.listdir(directory_results):
    uuid = filename.split('.')[0]
    processedFiles.add(uuid)
print("=================================")
print("number of files processed already: {}".format(len(processedFiles)))
print("=================================")


for filename in os.listdir(directory_control):
    uuid = filename.split('.')[0].split('-')[0]
    if uuid in processedFiles:
        print("File {}.txt has already been processed".format(uuid))
        continue
    audio_file= open(directory_control + filename, "rb")
    transcription = client.audio.transcriptions.create(
        file=audio_file, # Required audio file
        model="whisper-large-v3-turbo", # Required model to use for transcription
        # Best practice is to write the prompt in the language of the audio, use translate.google.com if needed
        prompt=f"Опиши о чем речь в аудио. Если вы не можете перевести, выведите: «CANNOT TRANSCRIBE FILE».",  # Translation: Describe what the audio is about
        language="ru", # Original language of the audio
        response_format="json",  # Optional
        temperature=0.0  # Optional
        )

    translation_prompt = f"""
            Instructions: Translate the following content from Russian to English. Output only the translated text and nothing else. if the text says "CANNOT TRANSCRIBE FILE" Please just output the text "CANNOT TRANSCRIBE FILE"
            Content: {transcription}
            """
    response_adobe = clientBabylon.chat.completions.create(
        model="orpo-mistral-v0.3-ua-tokV2-focus-10B-low-lr-1epoch-aux-merged-1ep",
        messages=[{"role": "user", "content": translation_prompt}],
        temperature=0.0
    )
    contentDict[uuid] = response_adobe.choices[0].message.content
    with open(directory_results + "{}.txt".format(uuid), mode='w') as file:
        file.write(contentDict[uuid])
    print("Adobe uuid output {} has been written to data".format(uuid))


print("Creating xls workbook...")

wb = Workbook()
sheet1 = wb.add_sheet("Sheet 1")

print("Writing data to workbook...")
i = 0
for filename in os.listdir(directory_results):
    sheet1.write(i,0,filename.split('.')[0])
    print(filename)
    f = open(directory_results + filename, 'r')
    
    sheet1.write(i,1,f.read())
    i+= 1


xls_file_path = "unedited_control.xls"
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

