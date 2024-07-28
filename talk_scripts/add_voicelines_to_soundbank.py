import copy
import json
import os
import shutil
import subprocess
from typing import Union


#The root_audio_dir must contain a folder structure like:
#[AccountID]
#   Intro
#       0.wav
#       1.wav
#       2.wav
#   Outro
#       0.wav
#       1.wav
#And so on, for each AccountID.
root_audio_dir = r"C:\Users\lugia19\Desktop\Programs\AC6_tools\Research\Arena sounds\bnk-autoedit\audio-files"

#Where rewwise (and fnv-hash.exe specifically) is located
fnv_hash_path = r"C:\Users\lugia19\Desktop\Programs\AC6_tools\Audio\rewwise\fnv-hash.exe"

#The extracted soundbank.json to modify, npc015.bnk is the one for ALLMIND, so it's the one that's recommended, as it's loaded when necessary.
soundbank_path = r"C:\Users\lugia19\Desktop\Programs\AC6_tools\Research\Arena sounds\bnk-autoedit\npc015\soundbank.json"





base_talk_accountid = 310
override_conversion_script_path = None

if override_conversion_script_path:
    conversion_script_path = override_conversion_script_path
else:
    current_script_path = os.path.abspath(__file__)
    current_script_folder = os.path.dirname(current_script_path)
    conversion_script_path = os.path.join(current_script_folder, "wem_conversion_wrapper.py")

soundbank_data:dict = json.load(open(soundbank_path, "r"))
object_list:list = soundbank_data["sections"][1]["body"]["HIRC"]["objects"]

def get_hash(input_text):
    command = [fnv_hash_path, "--input", input_text]

    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        return int(result.stdout.strip())
    except subprocess.CalledProcessError as e:
        print(f"Error running the command: {e}")
        print(f"Error output: {e.stderr}")
        return None

def get_object(object_id:Union[str, int]):
    if isinstance(object_id, str):
        hash_id = get_hash(object_id)
        string_id = object_id
    else:
        hash_id = object_id
        string_id = "nonexistant"
    for snd_object in object_list:
        if snd_object["id"].get("Hash") == hash_id or snd_object["id"].get("String") == string_id:
            return snd_object

    return None


def update_sound(talk_id:int, sound_filename:str):
    string_id = f"Sound_v{talk_id}"
    new_sound = get_object(string_id)

    if not new_sound:   #Create it anew
        new_sound = copy.deepcopy(base_sound)
        new_sound["id"]["Hash"] = get_hash(string_id)
        object_list.insert(object_list.index(base_sound), new_sound)
    #new_sound["body"]["Sound"]["bank_source_data"]["source_type"] = "Streaming"
    new_sound["body"]["Sound"]["bank_source_data"]["source_type"] = "Embedded"

    #Update the source filename
    new_sound["body"]["Sound"]["bank_source_data"]["media_information"]["source_id"] = int(sound_filename.replace(".wem",""))

    if new_sound["id"]["Hash"] not in actor_mixer["body"]["ActorMixer"]["children"]["items"]:
        actor_mixer["body"]["ActorMixer"]["children"]["items"].append(new_sound["id"]["Hash"])

    return new_sound["id"]["Hash"]

def add_action(talk_id:int, is_play:bool, sound_filename:str):
    if is_play:
        base_action = base_play_action
    else:
        base_action = base_stop_action
    string_id = f"{'Play_' if is_play else 'Stop_'}Action_v{talk_id}"

    new_action = get_object(string_id)
    if not new_action:
        new_action = copy.deepcopy(base_action)
        new_action["id"]["Hash"] = get_hash(string_id)
        object_list.insert(object_list.index(base_action), new_action)

    #Update the referenced sound, ensuring it exists
    sound_hash = update_sound(talk_id, sound_filename)
    new_action["body"]["Action"]["external_id"] = sound_hash

    return new_action["id"]["Hash"]

def add_event(talk_id:int, is_play:bool, sound_filename:str):
    if is_play:
        prefix = "Play_"
        base_event = base_play_event
    else:
        prefix = "Stop_"
        base_event = base_stop_event

    event_string_id = f"{prefix}v{talk_id}"
    new_event = get_object(event_string_id)
    if not new_event:
        new_event = copy.deepcopy(base_event)
        if "Hash" in new_event["id"]:
            new_event["id"].pop("Hash")
        new_event["id"]["String"] = event_string_id
        object_list.insert(object_list.index(base_event), new_event)

    if is_play:
        new_action_id = add_action(talk_id, is_play, sound_filename)
    else:
        new_action_id = add_action(talk_id, is_play, sound_filename)

    new_event["body"]["Event"]["actions"] = [new_action_id]

    return new_event["id"]["String"]

#Iterate over sound files
#Add sound file (assuming it does not exist already)
#Add play/stop events (which will add the corresponding actions)

def main():
    soundbank_folder = os.path.dirname(soundbank_path)
    #wem_folder = os.path.join(os.path.dirname(soundbank_folder), "wem")
    #os.makedirs(wem_folder, exist_ok=True)

    for account_id in os.listdir(root_audio_dir):
        account_folder = os.path.join(root_audio_dir, account_id)
        if os.path.isdir(account_folder) and account_id.isdigit():
            for subfolder in os.listdir(account_folder):
                subfolder_path = os.path.join(account_folder, subfolder)
                if os.path.isdir(subfolder_path):
                    for filename in os.listdir(subfolder_path):
                        if filename.endswith(".wav"):
                            # Get the path to the wem file
                            wem_filename = os.path.splitext(filename)[0] + ".wem"
                            wem_filepath = os.path.join(subfolder_path, wem_filename)
                            wav_filepath = os.path.join(subfolder_path, filename)

                            if not os.path.exists(wem_filepath):
                                # Call the convert_audio.py script with the WAV file as an argument
                                command = ["python", conversion_script_path, wav_filepath]
                                subprocess.run(command, check=True)

                            # Extract the offset from the filename
                            offset = int(os.path.splitext(filename)[0])

                            #Calculate the talk_id
                            if os.path.basename(os.path.dirname(wav_filepath)).lower() == "intro":
                                talk_id = 600000000 + int(account_id) * 1000 + 100 + offset
                            else:
                                talk_id = 700000000 + int(account_id) * 1000 + offset



                            new_wem_filename = str(get_hash(f"Source_v{talk_id}")) + ".wem"
                            #new_wem_filepath = os.path.join(wem_folder, new_wem_filename)
                            new_wem_filepath = os.path.join(soundbank_folder, new_wem_filename)
                            os.makedirs(os.path.dirname(new_wem_filepath), exist_ok=True)

                            if os.path.exists(new_wem_filepath):
                                print("Warning - overwriting existing file.")
                            shutil.copy2(wem_filepath, new_wem_filepath)

                            # Call add_event twice for each file
                            add_event(talk_id, is_play=True, sound_filename=new_wem_filename)
                            add_event(talk_id, is_play=False, sound_filename=new_wem_filename)


    print(f'Final ActorMixer children count: {len(actor_mixer["body"]["ActorMixer"]["children"]["items"])}')
    print(f'Final object count: {len(object_list)}')
    json.dump(soundbank_data, open(soundbank_path, "w"), indent=2)
    print("Done saving. Rebuild the bnk from the folder.")

if __name__ == "__main__":
    base_play_event = copy.deepcopy(get_object(f"Play_v{600000000 + base_talk_accountid * 1000 + 100}"))
    base_play_action = copy.deepcopy(get_object(base_play_event["body"]["Event"]["actions"][0]))
    base_stop_event = copy.deepcopy(get_object(f"Stop_v{600000000 + base_talk_accountid * 1000 + 100}"))
    base_stop_action = copy.deepcopy(get_object(base_stop_event["body"]["Event"]["actions"][0]))
    base_sound = copy.deepcopy(get_object(base_stop_action["body"]["Action"]["external_id"]))

    actor_mixer = get_object(base_sound["body"]["Sound"]["node_base_params"]["direct_parent_id"])
    main()
print("")