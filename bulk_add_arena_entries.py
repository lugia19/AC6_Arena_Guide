import copy
import csv
import os

param_directory = r"C:\Users\lugia19\Desktop 3\stuff\all_params"
text_directory = r"C:\Users\lugia19\Desktop 3\stuff\all_texts"

baseline_ac = 11200000  #This is the AC we copy stuff from, so its defaults will be used for stuff that's not specified (such as the AI logic file).
#I picked Carla (my beloved) because it has everything with the same ID, so it's ez.


number_of_combatants = 100

name_prefix = "NeoArena"

starting_arena_id = 300   #Used for the Arena ID.
starting_arena_rank = 300   #Used for the rank texture. This will DECREASE as the ID increases.

starting_account_id = 19800
starting_npc_chara_id = 999009800    #Used for CharaInitiParam, NpcParam, NpcThinkParam (and its associated LogicID)

base_fight_data = {
    "missionParamId": 9411,
    "menuCategory":20,
    "introCutsceneId": 23000,
    "bgmSoundId": 50000,
    "initialCoamReward":1,
    "repeatCoamReward":1,
    "outroCutsceneId":-1
}


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


def get_csv_list(csv_file):
    if not csv_file.endswith(".csv"):
        csv_file += ".csv"
    check_csv_header(os.path.join(param_directory, csv_file))
    with open(os.path.join(param_directory, csv_file), "r") as file:

        reader = csv.DictReader(file)
        csv_data = list(reader)
    return csv_data

def get_entry_with_id(ID, entry_list, ID_property="ID"):
    for entry in entry_list:
        if entry[ID_property] == str(ID):
            return copy.deepcopy(entry)
    return None

ArenaParam_data = get_csv_list("ArenaParam")
complete_base_fight_data = get_entry_with_id(11200000, ArenaParam_data, "charaInitParamId")
for key, value in base_fight_data.items():
    complete_base_fight_data[key] = value

AccountParam_data = get_csv_list("AccountParam")
base_account_data = copy.deepcopy(AccountParam_data[-1])

CharaInitParam_data = get_csv_list("CharaInitParam")
base_charinit_data = get_entry_with_id(baseline_ac, CharaInitParam_data)

NPCParam_data = get_csv_list("NpcParam")
base_npcparam_data = get_entry_with_id(baseline_ac, NPCParam_data)

NPCThink_data = get_csv_list("NpcThinkParam")
base_npcthink_data = get_entry_with_id(baseline_ac, NPCThink_data)

def remove_empty_lines_before_hash(lines):
    result = []
    for i, line in enumerate(lines):
        if i > 0 and (line.startswith('###') or i == len(lines)-1) and lines[i-1].strip() == '':
            result.pop()
        result.append(line)
    if result[-1].strip() == "":
        result.pop()
    return result

characters_lines = remove_empty_lines_before_hash(open(os.path.join(text_directory, "TitleCharacters.fmgmerge.txt")).readlines())
rankerprofile_lines = remove_empty_lines_before_hash(open(os.path.join(text_directory, "RankerProfile.fmgmerge.txt")).readlines())

def add_description(arena_id, text):
    rankerprofile_lines.append(f"###{arena_id}\n")
    rankerprofile_lines.append(text+"\n")

def add_char(account_id, ac_text, pilot_text):
    characters_lines.append(f"###{account_id}###{account_id+2}\n")
    characters_lines.append(ac_text + "\n")
    characters_lines.append(f"###{account_id+1}###{account_id + 3}\n")
    characters_lines.append(pilot_text + "\n")

def insert_param_entry(dict_obj, dict_list):
    # Find the index where the dict_obj should be inserted based on its ID
    insert_index = None
    for i in range(len(dict_list)):
        if int(dict_obj["ID"]) < int(dict_list[i]["ID"]):
            insert_index = i
            break

    # If the dict_obj has the highest ID, append it to the end of the list
    if insert_index is None:
        dict_list.append(dict_obj)
    else:
        dict_list.insert(insert_index, dict_obj)

    return dict_list

for fight_index in range(number_of_combatants):
    npc_chara_id = starting_npc_chara_id+fight_index
    arena_id = starting_arena_id+fight_index
    account_id = starting_account_id+fight_index*10

    new_fight = copy.deepcopy(complete_base_fight_data)
    new_fight["ID"] = arena_id
    new_fight["rankTextureId"] = starting_arena_rank-fight_index
    new_fight["Name"] = f"{name_prefix} Combatant #{fight_index+1}"
    new_fight["accountParamId"] = account_id
    new_fight["charaInitParamId"] = npc_chara_id
    new_fight["npcParamId"] = npc_chara_id
    new_fight["npcThinkParamId"] = npc_chara_id
    ArenaParam_data.append(new_fight)
    add_description(new_fight["ID"], f"{name_prefix} Description #{fight_index+1}")

    new_account = copy.deepcopy(base_account_data)
    new_account["Name"] = f"{name_prefix} Account #{fight_index+1}"
    new_account["ID"] = account_id
    new_account["fmgId"] = account_id
    new_account["menuDecalId"] = account_id
    insert_param_entry(new_account, AccountParam_data)
    add_char(account_id, f"{name_prefix} AC #{fight_index+1}", f"{name_prefix} Pilot #{fight_index+1}")

    new_charainit = copy.deepcopy(base_charinit_data)
    new_charainit["Name"] = f"{name_prefix} CharaInit #{fight_index + 1}"
    new_charainit["ID"] = npc_chara_id
    new_charainit["acDesignId"] = npc_chara_id
    insert_param_entry(new_charainit, CharaInitParam_data)

    new_npcparam = copy.deepcopy(base_npcparam_data)
    new_npcparam["Name"] = f"{name_prefix} NpcParam #{fight_index + 1}"
    new_npcparam["ID"] = npc_chara_id
    new_npcparam["accountParamId"] = account_id
    insert_param_entry(new_npcparam, NPCParam_data)

    new_npcthinkdata = copy.deepcopy(base_npcthink_data)
    new_npcthinkdata["Name"] = f"{name_prefix} NpcThink #{fight_index + 1}"
    new_npcthinkdata["ID"] = npc_chara_id
    insert_param_entry(new_npcthinkdata, NPCThink_data)


def save_csv(csv_file, data):
    if not csv_file.endswith(".csv"):
        csv_file += ".csv"

    # Write the CSV file with escaped quotes
    with open(os.path.join(param_directory, "edited", csv_file), "w") as file:
        fieldnames = data[0].keys()
        writer = csv.DictWriter(file, fieldnames=fieldnames, quoting=csv.QUOTE_NONE, escapechar='\\')
        writer.writeheader()
        writer.writerows(data)

    # Read the CSV file and unescape the quotes
    with open(os.path.join(param_directory, "edited", csv_file), "r") as file:
        content = file.read()

    # Replace \" with "
    content = content.replace('\\"', '"')

    # Write the modified content back to the CSV file
    with open(os.path.join(param_directory, "edited", csv_file), "w") as file:
        file.write(content)


if not os.path.exists(os.path.join(param_directory, "edited")):
    os.mkdir(os.path.join(param_directory, "edited"))

if not os.path.exists(os.path.join(text_directory, "edited")):
    os.mkdir(os.path.join(text_directory, "edited"))

save_csv("ArenaParam", ArenaParam_data)
save_csv("AccountParam", AccountParam_data)
save_csv("CharaInitParam", CharaInitParam_data)
save_csv("NpcParam", NPCParam_data)
save_csv("NpcThinkParam", NPCThink_data)

with open(os.path.join(text_directory, "edited", "TitleCharacters.fmgmerge.txt"), "w") as text_file:
    text_file.writelines(remove_empty_lines_before_hash(characters_lines))

with open(os.path.join(text_directory, "edited", "RankerProfile.fmgmerge.txt"), "w") as text_file:
    text_file.writelines(remove_empty_lines_before_hash(rankerprofile_lines))