import copy
import csv
import os
import re
import subprocess
from concurrent.futures import ThreadPoolExecutor
from threading import Semaphore
from num2words import num2words
from elevenlabslib import User
from elevenlabslib.helpers import *
import keyring

#Where you want your generated audio tree to be
base_output_folder = r"C:\Users\lugia19\Desktop\Programs\AC6_tools\Research\Arena sounds\bnk-autoedit\audio-files"

#The location of your exported talkmsg
talkmsg_location = r"C:\Users\lugia19\Desktop\Programs\AC6_tools\Research\Arena sounds\bnk-autoedit\TalkMsg.fmgmerge.json"

#Where your new arena account_ids start
initial_account_id = 19800

#The number of opponents
num_accounts = 100

user = User(keyring.get_password("gpt_speaker", "elevenlabs_api_key"))
voice = user.get_voices_by_name_v2("ALLMIND")[0]

def check_csv_header(file_path):
    with open(file_path, 'r') as file:
        header = file.readline().strip()
        first_row = file.readline().strip()
        header_count = header.count(',') + 1
        first_row_count = first_row.count(',') + 1

        if header_count > first_row_count:
            # Remove the trailing comma from the header
            header = header.rstrip(',')
            # Rewrite the file with the updated header
            with open(file_path, 'r') as file:
                lines = file.readlines()
            lines[0] = header + '\n'
            with open(file_path, 'w') as file:
                file.writelines(lines)
            print(f"Trailing comma removed from the header in {file_path}")
        else:
            print(f"No trailing comma found in the header of {file_path}")

def get_talk_entry(account_id, offset, is_intro):
    if is_intro:
        talk_id = 600000000 + int(account_id) * 1000 + 100 + offset
    else:
        talk_id = 700000000 + int(account_id) * 1000 + offset

    for entry in talkmsg_data["Entries"]:
        if talk_id in entry["IDList"]:
            return entry["Text"]

    return None

def generate_account_structure(initial_account_id, num_accounts):
    for i in range(num_accounts):
        account_id = initial_account_id + i * 10
        account_folder = os.path.join(base_output_folder, str(account_id))

        intro_folder = os.path.join(account_folder, "Intro")
        os.makedirs(intro_folder, exist_ok=True)

        outro_folder = os.path.join(account_folder, "Outro")
        os.makedirs(outro_folder, exist_ok=True)

        for j in range(3):
            filename = f"{j}.wav"
            intro_file = os.path.join(intro_folder, filename)
            outro_file = os.path.join(outro_folder, filename)

            intro_text = get_talk_entry(account_id, j, True)
            generate_wav(intro_text, intro_file)
            if j < 2:
                outro_text = get_talk_entry(account_id, j, False)
                generate_wav(outro_text, outro_file)


def convert_numbers_to_words(text):
    def replace_numbers(match):
        number = match.group(0)
        return num2words(number)

    return re.sub(r'\d+', replace_numbers, text)

def generate_wav(text, output_file):
    # Fill this in with whatever TTS you want.
    # You just need to ensure the output is saved in output_file.
    # I used sam as a very simple example/demo.
    text = text.replace("#","")
    text = text.replace("NeoArena", "Neo-Arena")
    text = convert_numbers_to_words(text)
    def wrapper():
        with semaphore:
            audio_future, _ = voice.generate_audio_v3(text, generation_options=GenerationOptions(model_id="eleven_multilingual_v2"))
            save_audio_v2(audio_future.result(), output_file, "wav")

    threading.Thread(target=wrapper).start()
    #subprocess.run([r"C:\Users\lugia19\Desktop\Programs\AC6_tools\Research\Arena sounds\bnk-autoedit\SAM\sam.exe", "-wav", output_file, text], check=True)


talkmsg_data = json.load(open(talkmsg_location))

semaphore = threading.Semaphore(10)
generate_account_structure(initial_account_id, num_accounts)