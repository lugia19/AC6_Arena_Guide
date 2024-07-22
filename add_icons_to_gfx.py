import os
import re
import shutil
import subprocess

import xmltodict

def process_gfx_file(ffdec_path, gfx_file, layout_file):
    # Copy the existing file as [filename]-backup.gfx
    backup_file = os.path.splitext(gfx_file)[0] + '-backup.gfx'
    shutil.copy2(gfx_file, backup_file)

    # Convert the .gfx file to .xml
    xml_file = os.path.splitext(gfx_file)[0] + '.xml'
    subprocess.run([ffdec_path, '-swf2xml', gfx_file, xml_file], check=True)

    # Read the first XML file
    with open(layout_file, 'r') as file:
        xml_data1 = file.read()

    # Parse the first XML data
    layout_data = xmltodict.parse(xml_data1)

    # Extract filenames and IDs from the first XML
    rank_image_files = []

    for item in layout_data["TextureAtlas"]['SubTexture']:
        filename = item['@name']
        id_match = re.search(r'_(\d+)\.png$', filename)
        if id_match:
            id_value = int(id_match.group(1))
            rank_image_files.append({"filename": filename, "rankID": id_value})

    # Read the second XML file
    with open(xml_file, 'r') as file:
        xml_data2 = file.read()

    # Parse the second XML data
    gfx_data = xmltodict.parse(xml_data2)

    highest_character_id = max([int(item['@characterID']) for item in gfx_data['swf']["tags"]["item"] if '@characterID' in item])
    base_character_id_offset = ((highest_character_id // 100) + 1) * 100

    # Find the characterID corresponding to ArenaRank_00000d.tga
    arena_rank_00000d_id = None
    for item in gfx_data['swf']['tags']['item']:
        if item['@type'] == 'DefineExternalImage2' and item['@exportName'] == 'ArenaRank_00000d':
            arena_rank_00000d_id = int(item['@characterID'])
            break

    if arena_rank_00000d_id is None:
        print("ArenaRank_00000d.tga not found.")
        exit()

    # Find the last line with the specified format
    last_line_index = None
    for i, item in enumerate(gfx_data['swf']["tags"]["item"]):
        if item['@type'] == 'DefineExternalImage2' and 'ArenaRank' in item['@exportName']:
            last_line_index = i

    # Insert new lines after the last line
    for idx, image_file_data in enumerate(rank_image_files):
        new_line = f'<item type="DefineExternalImage2" bitmapFormat="13" characterID="{base_character_id_offset + idx}" exportName="{image_file_data["filename"][:-4]}" fileName="{image_file_data["filename"][:-4]}.tga" forceWriteAsLong="false" imageID="{base_character_id_offset + idx}" targetHeight="128" targetWidth="232" unknownID="0"/>'
        rank_image_files[idx]["characterID"] = base_character_id_offset + idx
        gfx_data['swf']["tags"]["item"].insert(last_line_index + 1, xmltodict.parse(new_line)['item'])

    #Find the SymbolClassTag, and build out a dict
    names_by_charID = {}
    for item in gfx_data['swf']['tags']['item']:
        if item['@type'] == 'SymbolClassTag':
            for i in range(len(item["tags"]["item"])):
                names_by_charID[int(item["tags"]["item"][i])] = item["names"]["item"][i]

    # Find the ArenaRank tag
    sprite_tag = None
    for item in gfx_data['swf']['tags']['item']:
        if item['@type'] == 'DefineSpriteTag':
            character_id = int(item['@spriteId'])
            if "arenarank" in names_by_charID.get(character_id, "").lower():
                sprite_tag = item


    images_by_rank = {image["rankID"]: image for image in rank_image_files}
    last_image_id = max(images_by_rank.keys())
    sub_tags_copy = sprite_tag['subTags']['item'].copy()

    def find_nth_frame_tag_index(n):
        inner_frame_count = 0
        for i, tag in enumerate(sprite_tag['subTags']['item']):
            if tag['@type'] == 'ShowFrameTag':
                inner_frame_count += 1
                if inner_frame_count == n:
                    return i
        return -1

    # Count frames and check for matching IDs
    frame_count = 1
    for sub_tag in sub_tags_copy:
        if sub_tag['@type'] == 'ShowFrameTag':
            if frame_count - 1 in images_by_rank.keys():
                # Insert RemoveObject2Tag and PlaceObject3Tag for matching imageIDs
                remove_object2_tag = '<item type="RemoveObject2Tag" depth="1" forceWriteAsLong="false"/>'
                place_object3_tag = f'<item type="PlaceObject3Tag" bitmapCache="0" blendMode="0" characterId="{images_by_rank[frame_count - 1]["characterID"]}" clipDepth="0" depth="1" forceWriteAsLong="true" placeFlagHasBlendMode="false" placeFlagHasCacheAsBitmap="false" placeFlagHasCharacter="true" placeFlagHasClassName="false" placeFlagHasClipActions="false" placeFlagHasClipDepth="false" placeFlagHasColorTransform="false" placeFlagHasFilterList="false" placeFlagHasImage="true" placeFlagHasMatrix="true" placeFlagHasName="false" placeFlagHasRatio="false" placeFlagHasVisible="false" placeFlagMove="false" placeFlagOpaqueBackground="false" ratio="0" reserved="false" visible="0">'
                place_object3_tag += '<matrix type="MATRIX" hasRotate="false" hasScale="false" nRotateBits="0" nScaleBits="0" nTranslateBits="13" rotateSkew0="0" rotateSkew1="0" scaleX="0" scaleY="0" translateX="-2320" translateY="-1280"/>'
                place_object3_tag += '</item>'
                index = find_nth_frame_tag_index(frame_count)
                if index != -1:
                    sprite_tag['subTags']['item'].insert(index, xmltodict.parse(remove_object2_tag)['item'])
                    sprite_tag['subTags']['item'].insert(index + 1, xmltodict.parse(place_object3_tag)['item'])

            if frame_count == last_image_id + 2:
                # Insert PlaceObject3Tag for ArenaRank_00000d.tga on the frame after the last image ID
                place_object3_tag = f'<item type="PlaceObject3Tag" bitmapCache="0" blendMode="0" characterId="{arena_rank_00000d_id}" clipDepth="0" depth="1" forceWriteAsLong="true" placeFlagHasBlendMode="false" placeFlagHasCacheAsBitmap="false" placeFlagHasCharacter="true" placeFlagHasClassName="false" placeFlagHasClipActions="false" placeFlagHasClipDepth="false" placeFlagHasColorTransform="false" placeFlagHasFilterList="false" placeFlagHasImage="true" placeFlagHasMatrix="true" placeFlagHasName="false" placeFlagHasRatio="false" placeFlagHasVisible="false" placeFlagMove="false" placeFlagOpaqueBackground="false" ratio="0" reserved="false" visible="0">'
                place_object3_tag += '<matrix type="MATRIX" hasRotate="false" hasScale="false" nRotateBits="0" nScaleBits="0" nTranslateBits="13" rotateSkew0="0" rotateSkew1="0" scaleX="0" scaleY="0" translateX="-2320" translateY="-1280"/>'
                place_object3_tag += '</item>'
                index = find_nth_frame_tag_index(frame_count)
                if index != -1:
                    sprite_tag['subTags']['item'].insert(index, xmltodict.parse(place_object3_tag)['item'])

            frame_count += 1

    # Write the modified second XML file
    edited_xml_file = os.path.splitext(gfx_file)[0] + '-edited.xml'
    with open(edited_xml_file, 'w') as file:
        file.write(xmltodict.unparse(gfx_data, pretty=True))

    # Convert the edited .xml file back to .gfx
    subprocess.run([ffdec_path, '-xml2swf', edited_xml_file, gfx_file], check=True)
    os.remove(xml_file)
    os.remove(edited_xml_file)

def main():
    # Ask the user for the location of ffdec.bat
    ffdec_path = r"C:\Program Files (x86)\FFDec\ffdec.bat"

    if not os.path.exists(ffdec_path):
        print("ffdec.bat not found in the expected location. If you haven't installed JPEXS Decompiler, please do so.")
        ffdec_path = input('Otherwise, manually enter the path to ffdec.bat: ').replace("\"","")

    # Ask the user for the location of the .layout file
    layout_file = input('Enter the path to the .layout file: ').replace("\"","")

    # Ask the user for the location of the .gfx files
    gfx_files = []
    while True:
        gfx_file = input('Enter the path to a .gfx file (or press Enter to finish): ').replace("\"","")
        if gfx_file:
            gfx_files.append(gfx_file)
        else:
            break

    # Process each .gfx file
    for gfx_file in gfx_files:
        print(f"Processing {gfx_file}...")
        process_gfx_file(ffdec_path, gfx_file, layout_file)

    input("All .gfx files edited. Press Enter to exit.")

if __name__ == '__main__':
    main()