import os
import xml.etree.ElementTree as ET


def update_xml_file(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()

    files_element = root.find("files")

    if files_element is None:
        files_element = ET.SubElement(root, "files")

    max_id = -1
    existing_paths = set()

    for file_element in files_element.findall("file"):
        id_element = file_element.find("id")
        path_element = file_element.find("path")

        if id_element is not None and path_element is not None:
            max_id = max(max_id, int(id_element.text))
            existing_paths.add(path_element.text)

    xml_dir = os.path.dirname(xml_file)

    for folder_name in os.listdir(xml_dir):
        if folder_name.startswith(("MENU_Decal_", "MENU_Archetype_")) and folder_name.endswith("-tpf-dcx"):
            folder_parts = folder_name.split("_")
            file_name = f"{folder_parts[0]}_{folder_parts[1]}_{int(folder_parts[2].split('-')[0]):08d}.tpf.dcx"

            if file_name not in existing_paths:
                max_id += 1
                file_element = ET.SubElement(files_element, "file")
                flags_element = ET.SubElement(file_element, "flags")
                flags_element.text = "Flag1"
                id_element = ET.SubElement(file_element, "id")
                id_element.text = str(max_id)
                path_element = ET.SubElement(file_element, "path")
                path_element.text = file_name
                print(f"Added {file_name} to the XML file")

    tree.write(xml_file)
    print(f"Updated {xml_file}")


# Example usage
xml_file = r"C:\Users\lugia19\Desktop\Programs\AC6_tools\ModEngine-2.1.0.0-win64\arena-edit\menu\hi\00_solo-tpfbdt\_witchy-bxf4.xml"
update_xml_file(xml_file)