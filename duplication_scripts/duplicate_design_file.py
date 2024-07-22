#Simple script made to help you bulk duplicate design files.
import os
import shutil
import xml.etree.ElementTree as ET

def main():
    source_file = r"C:\Users\lugia19\Desktop\Programs\AC6_tools\ModEngine-2.1.0.0-win64\arena-edit\param\asmparam\asmparam-designbnd-dcx\11200000.design"
    num_copies = 100
    starting_number = 999009800
    xml_file = r"C:\Users\lugia19\Desktop\Programs\AC6_tools\ModEngine-2.1.0.0-win64\arena-edit\param\asmparam\asmparam-designbnd-dcx\_witchy-bnd4.xml"

    new_files = copy_files(source_file, num_copies, starting_number)
    update_xml_file(xml_file, new_files)

def copy_files(source_file, num_copies, starting_number):
    source_dir, source_name = os.path.split(source_file)
    base_name, extension = os.path.splitext(source_name)

    new_files = []

    for i in range(num_copies):
        new_number = starting_number + i
        new_file_name = f"{new_number:09d}{extension}"
        new_file_path = os.path.join(source_dir, new_file_name)
        shutil.copy(source_file, new_file_path)
        print(f"Copied {source_file} to {new_file_path}")
        new_files.append(new_file_name)

    return new_files

def update_xml_file(xml_file, new_files):
    tree = ET.parse(xml_file)
    root = tree.getroot()

    files_element = root.find("files")

    if files_element is None:
        files_element = ET.SubElement(root, "files")

    max_id = -1
    for file_element in files_element.findall("file"):
        id_element = file_element.find("id")
        if id_element is not None:
            max_id = max(max_id, int(id_element.text))

    for new_file in new_files:
        max_id += 1
        file_element = ET.SubElement(files_element, "file")
        flags_element = ET.SubElement(file_element, "flags")
        flags_element.text = "Flag1"
        id_element = ET.SubElement(file_element, "id")
        id_element.text = str(max_id)
        path_element = ET.SubElement(file_element, "path")
        path_element.text = new_file

    tree.write(xml_file)
    print(f"Updated {xml_file} with {len(new_files)} new files")


if __name__=="__main__":
    main()
