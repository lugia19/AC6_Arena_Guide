import copy
import csv
import json
import os
from typing import Union, List

param_directory = r"C:\Users\lugia19\Desktop 3\stuff\all_params"
text_directory = r"C:\Users\lugia19\Desktop 3\stuff\all_texts_v2"


baseline_ac = 11200000  #This is the AC we copy stuff from, so its defaults will be used for stuff that's not specified (such as the AI logic file).
#I picked Carla (my beloved) because it has everything with the same ID, so it's ez.

announcer_name_text_id = 200    #The ID of the announcer for the intro/outro text. 200 = ALLMIND

number_of_combatants = 100

name_prefix = "NeoArena"

starting_arena_id = 300   #Used for the Arena ID.
starting_arena_rank = 300   #Used for the rank texture. This will DECREASE as the ID increases.

starting_account_id = 19800
starting_npc_chara_id = 999009800    #Used for CharaInitiParam, NpcParam, NpcThinkParam (and its associated LogicID)

base_fight_data = {
    "missionParamId": 9411,
    "menuCategory":20,
    "introCutsceneId": 230000,
    "bgmSoundId": 50000,
    "initialCoamReward":1,
    "repeatCoamReward":1,
    "outroCutsceneId":-1,
}


param_data = dict()
fmg_text_data = dict()

def main():
    complete_base_fight_data = get_param_entry_with_id(baseline_ac, "ArenaParam", "charaInitParamId")
    for key, value in base_fight_data.items():
        complete_base_fight_data[key] = value

    base_charinit_data = get_param_entry_with_id(baseline_ac, "CharaInitParam")
    base_npcparam_data = get_param_entry_with_id(baseline_ac, "NpcParam")
    base_account_data = get_param_entry_with_id(base_npcparam_data["accountParamId"], "AccountParam")
    base_npcthink_data = get_param_entry_with_id(baseline_ac, "NpcThinkParam")
    base_talkparam_data = get_param_entry_with_id(600000000 + int(base_npcparam_data["accountParamId"]) * 1000 + 100, "TalkParam")

    for fight_index in range(number_of_combatants):
        npc_chara_id = starting_npc_chara_id + fight_index
        arena_id = starting_arena_id + fight_index
        account_id = starting_account_id + fight_index * 10

        new_fight = copy.deepcopy(complete_base_fight_data)
        new_fight["ID"] = arena_id
        new_fight["rankTextureId"] = starting_arena_rank - fight_index
        new_fight["Name"] = f"{name_prefix} Combatant #{fight_index + 1}"
        new_fight["accountParamId"] = account_id
        new_fight["charaInitParamId"] = npc_chara_id
        new_fight["npcParamId"] = npc_chara_id
        new_fight["npcThinkParamId"] = npc_chara_id
        add_param_entry(new_fight, "ArenaParam")

        add_text_fmg_entry(new_fight["ID"], f"{name_prefix} Description #{fight_index + 1}", "RankerProfile")
        new_account = copy.deepcopy(base_account_data)
        new_account["Name"] = f"{name_prefix} Account #{fight_index + 1}"
        new_account["ID"] = account_id
        new_account["fmgId"] = account_id
        new_account["menuDecalId"] = account_id
        add_param_entry(new_account, "AccountParam")

        add_text_fmg_entry([account_id, account_id + 2], f"{name_prefix} AC #{fight_index + 1}", "TitleCharacters")
        add_text_fmg_entry([account_id + 1, account_id + 3], f"{name_prefix} Pilot #{fight_index + 1}", "TitleCharacters")

        for i in range(3):
            new_talk = copy.deepcopy(base_talkparam_data)
            new_talk["ID"] = 600000000 + account_id * 1000 + 100 + i
            new_talk["Name"] = f"{name_prefix} Fighter #{fight_index + 1} Intro #{i}"
            new_talk["msgId"] = new_talk["ID"]
            new_talk["voiceId"] = new_talk["ID"]
            new_talk["characterNameTextId"] = announcer_name_text_id
            add_param_entry(new_talk, "TalkParam")
            add_text_fmg_entry(new_talk["ID"], f"{name_prefix} Fighter #{fight_index + 1} Intro #{i}", "TalkMsg")

        for i in range(2):
            new_talk = copy.deepcopy(base_talkparam_data)
            new_talk["ID"] = 700000000 + account_id * 1000 + i
            new_talk["Name"] = f"{name_prefix} Fighter #{fight_index + 1} Outro #{i}"
            new_talk["msgId"] = new_talk["ID"]
            new_talk["voiceId"] = new_talk["ID"]
            new_talk["characterNameTextId"] = announcer_name_text_id
            add_param_entry(new_talk, "TalkParam")
            add_text_fmg_entry(new_talk["ID"], f"{name_prefix} Fighter #{fight_index + 1} Outro #{i}", "TalkMsg")

        new_charainit = copy.deepcopy(base_charinit_data)
        new_charainit["Name"] = f"{name_prefix} CharaInit #{fight_index + 1}"
        new_charainit["ID"] = npc_chara_id
        new_charainit["acDesignId"] = npc_chara_id
        add_param_entry(new_charainit, "CharaInitParam")

        new_npcparam = copy.deepcopy(base_npcparam_data)
        new_npcparam["Name"] = f"{name_prefix} NpcParam #{fight_index + 1}"
        new_npcparam["ID"] = npc_chara_id
        new_npcparam["accountParamId"] = account_id
        add_param_entry(new_npcparam, "NPCParam")

        new_npcthinkdata = copy.deepcopy(base_npcthink_data)
        new_npcthinkdata["Name"] = f"{name_prefix} NpcThink #{fight_index + 1}"
        new_npcthinkdata["ID"] = npc_chara_id
        add_param_entry(new_npcthinkdata, "NpcThinkParam")

    save_param("ArenaParam")
    save_param("AccountParam")
    save_param("CharaInitParam")
    save_param("NpcParam")
    save_param("NpcThinkParam")
    save_param("TalkParam")

    save_text("TitleCharacters")
    save_text("RankerProfile")
    save_text("TalkMsg")

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

def fetch_param_csv(csv_name):
    csv_file = os.path.join(param_directory, csv_name + ".csv")
    check_csv_header(os.path.join(param_directory, csv_file))
    with open(csv_file, "r") as file:
        reader = csv.DictReader(file)
        csv_data = list(reader)
    param_data[csv_name] = csv_data

def get_param_entry_with_id(ID:Union[int,str], param_name:str, ID_property="ID"):
    if param_name not in param_data:
        fetch_param_csv(param_name)

    for entry in param_data[param_name]:
        if entry[ID_property] == str(ID):
            return copy.deepcopy(entry)
    return None

def add_param_entry(new_param_entry:dict, param_name:str):
    # Find the index where the dict_obj should be inserted based on its ID
    insert_index = None

    if param_name not in param_data:
        fetch_param_csv(param_name)

    for i in range(len(param_name)):
        if int(new_param_entry["ID"]) < int(param_data[param_name][i]["ID"]):
            insert_index = i
            break

    # If the dict_obj has the highest ID, append it to the end of the list
    if insert_index is None:
        param_data[param_name].append(new_param_entry)
    else:
        param_data[param_name].insert(insert_index, new_param_entry)

def save_param(param_name):
    csv_file = param_name + ".csv"
    if not os.path.exists(os.path.join(param_directory, "edited")):
        os.mkdir(os.path.join(param_directory, "edited"))

    # Write the CSV file with escaped quotes
    with open(os.path.join(param_directory, "edited", csv_file), "w") as file:
        fieldnames = param_data[param_name][0].keys()
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(param_data[param_name])

    # Read the CSV file and unescape the quotes
    with open(os.path.join(param_directory, "edited", csv_file), "r") as file:
        content = file.read()

    # Replace \" with "
    content = content.replace('\\"', '"')

    # Write the modified content back to the CSV file
    with open(os.path.join(param_directory, "edited", csv_file), "w") as file:
        file.write(content)


def fetch_fmg_text(fmg_name):
    json_file = os.path.join(text_directory, fmg_name + ".fmgmerge.json")
    fmg_text_data[fmg_name] = json.load(open(json_file))

def add_text_fmg_entry(id_list:Union[int, List[int]], text_value:str, fmg_text_name:str):
    if isinstance(id_list, int):
        id_list = [id_list]

    if fmg_text_name not in fmg_text_data:
        fetch_fmg_text(fmg_text_name)

    # Remove the IDs from any existing item
    for item in fmg_text_data[fmg_text_name]["Entries"]:
        for id_value in id_list:
            if id_value in item["IDList"]:
                item["IDList"].remove(id_value)
                # If the IDList becomes empty after removing the ID, remove the entire item
                if len(item["IDList"]) == 0:
                    fmg_text_data[fmg_text_name]["Entries"].remove(item)

    # Check if the text already exists
    for item in fmg_text_data[fmg_text_name]["Entries"]:
        if item["Text"] == text_value:
            item["IDList"].extend(id_list)
            return

    # If the text doesn't exist, create a new item
    new_item = {"Text": text_value, "IDList": id_list}
    fmg_text_data[fmg_text_name]["Entries"].append(new_item)


def save_text(fmg_text_name):
    json_file = fmg_text_name + ".fmgmerge.json"
    if not os.path.exists(os.path.join(text_directory, "edited")):
        os.mkdir(os.path.join(text_directory, "edited"))

    with open(os.path.join(text_directory, "edited", json_file), "w") as fp:
        json.dump(fmg_text_data[fmg_text_name], fp, indent=2)









if __name__=="__main__":
    main()