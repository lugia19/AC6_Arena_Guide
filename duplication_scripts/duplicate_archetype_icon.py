import os
import shutil
import xml.etree.ElementTree as ET


def copy_folder(source_folder, num_copies, starting_id):
    source_dir, source_name = os.path.split(source_folder)

    for i in range(num_copies):
        new_id = starting_id + i if "archetype" in source_name.lower() else starting_id+i*10
        new_folder_name = f"{prefix}_{new_id:08d}-tpf-dcx"
        new_folder_path = os.path.join(source_dir, new_folder_name)

        shutil.copytree(source_folder, new_folder_path, dirs_exist_ok=True)
        print(f"Copied {source_folder} to {new_folder_path}")

        # Update the XML file
        xml_file = os.path.join(new_folder_path, "_witchy-tpf.xml")
        update_xml_file(xml_file, new_id)

        # Rename the DDS image file
        old_image_file = os.path.join(new_folder_path, f"{prefix}_{source_name.split('_')[-1].split('-')[0]}.dds")
        new_image_file = os.path.join(new_folder_path, f"{prefix}_{new_id:08d}.dds")
        os.rename(old_image_file, new_image_file)
        print(f"Renamed {old_image_file} to {new_image_file}")


def update_xml_file(xml_file, new_id):
    tree = ET.parse(xml_file)
    root = tree.getroot()

    filename_element = root.find("filename")
    if filename_element is not None:
        filename_element.text = f"{prefix}_{new_id:08d}.tpf.dcx"

    texture_element = root.find("textures/texture")
    if texture_element is not None:
        name_element = texture_element.find("name")
        if name_element is not None:
            name_element.text = f"{prefix}_{new_id:08d}.dds"

    tree.write(xml_file)
    print(f"Updated {xml_file}")


# Example usage
source_folder = r"C:\Users\lugia19\Desktop\Programs\AC6_tools\ModEngine-2.1.0.0-win64\arena-edit\menu\hi\00_solo-tpfbdt\MENU_Decal_00009900-tpf-dcx"
num_copies = 100
starting_id = 999009800

_, source_name = os.path.split(source_folder)
prefix = source_name.split("_")[0]+"_"+source_name.split("_")[1]

copy_folder(source_folder, num_copies, starting_id)