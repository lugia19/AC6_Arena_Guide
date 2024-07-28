import os
import sys
import shutil
import subprocess
import time
import xml.etree.ElementTree as ET

def find_wwise_console_path():
    audiokinetic_path = r"C:\Program Files (x86)\Audiokinetic"
    if not os.path.exists(audiokinetic_path):
        print("Wwise 2023 is not installed. Please install Wwise 2023 and try again.")
        sys.exit(1)

    wwise_folders = [folder for folder in os.listdir(audiokinetic_path) if "Wwise" in folder]
    if not wwise_folders:
        print("No Wwise installation found. Please install Wwise 2023 and try again.")
        sys.exit(1)

    wwise_folder = None
    for folder in wwise_folders:
        if "Wwise2023" in folder:
            wwise_folder = folder
            break

    if not wwise_folder:
        wwise_folder = wwise_folders[0]
        print(f"Warning: Using Wwise version {wwise_folder}, which may not be fully supported.")

    wwise_console_path = os.path.join(audiokinetic_path, wwise_folder, "Authoring", "x64", "Release", "bin", "WwiseConsole.exe")
    if not os.path.exists(wwise_console_path):
        print(f"WwiseConsole.exe not found in the expected location: {wwise_console_path}")
        sys.exit(1)

    return wwise_console_path

def create_wwise_project(root_audio_dir, wwise_console_path):
    project_dir = os.path.join(root_audio_dir, "../conversion-project")
    project_file = os.path.join(project_dir, "conversion-project.wproj")
    if not os.path.exists(project_dir) or not os.path.exists(project_file):
        create_project_args = [wwise_console_path, "create-new-project", project_file, "--platform", "Windows"]
        subprocess.run(create_project_args, check=True)

def convert_wav_to_wem(wav_file, root_audio_dir, wwise_console_path):
    input_folder = os.path.join(root_audio_dir, "input")
    os.makedirs(input_folder, exist_ok=True)
    new_wav_location = os.path.join(input_folder, os.path.basename(wav_file))
    # Copy the WAV file to the input folder
    if os.path.exists(new_wav_location):
        os.remove(new_wav_location)
    shutil.copy2(wav_file, input_folder)

    # Generate the XML file
    xml_root = ET.Element("ExternalSourcesList", SchemaVersion="1", Root=input_folder)
    #source_element = ET.SubElement(xml_root, "Source", Path=os.path.basename(wav_file), Conversion="Default Conversion Settings")
    source_element = ET.SubElement(xml_root, "Source", Path=os.path.basename(wav_file), Conversion="Vorbis Quality High")

    xml_tree = ET.ElementTree(xml_root)
    xml_filepath = os.path.join(input_folder, "to_convert.wsources")
    xml_tree.write(xml_filepath, encoding="UTF-8", xml_declaration=True)


    # Call WwiseConsole to convert the WAV to WEM
    project_file = os.path.join(root_audio_dir, "../conversion-project", "conversion-project.wproj")
    command = [
        wwise_console_path,
        "convert-external-source",
        project_file,
        "--no-wwise-dat",
        "--source-file",
        xml_filepath,
        "--output",
        "Windows",
        input_folder
    ]

    max_retries = 5
    retry_count = 0

    while retry_count < max_retries:
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, stderr = process.communicate()

        # Print the subprocess output
        #print("Subprocess output:")
        #print(stdout)

        # Print the subprocess error (if any)
        if stderr:
            print("Subprocess error:")
            print(stderr)

        # Check the subprocess return code
        if process.returncode != 0:
            raise subprocess.CalledProcessError(process.returncode, command)

        # Move the converted WEM file next to the original WAV
        wem_filename = os.path.splitext(os.path.basename(wav_file))[0] + ".wem"
        wem_filepath = os.path.join(input_folder, wem_filename)

        # Check if the WEM file exists
        if not os.path.exists(wem_filepath):
            print(f"WEM file not found: {wem_filepath}")
            retry_count += 1
            print(f"Retrying conversion... (Attempt {retry_count}/{max_retries})")
            continue

        # Check the size of the WEM file
        wem_size = os.path.getsize(wem_filepath)
        if wem_size < 2 * 1024:  # 2KB = 2 * 1024 bytes
            print(f"WEM file size is smaller than 2KB: {wem_filepath}")
            retry_count += 1
            print(f"Retrying conversion... (Attempt {retry_count}/{max_retries})")
            continue

        break

    else:
        print(f"Conversion failed after {max_retries} attempts: {wav_file}. Continuing anyway, but file may be broken.")

    wem_filename = os.path.splitext(os.path.basename(wav_file))[0] + ".wem"
    wem_filepath = os.path.join(input_folder, wem_filename)
    new_wem_filepath = os.path.join(os.path.dirname(wav_file), wem_filename)
    shutil.move(wem_filepath, new_wem_filepath)
    os.remove(new_wav_location)
    os.remove(xml_filepath)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Please drag and drop WAV files onto the script.")
        sys.exit(1)

    wwise_console_path = find_wwise_console_path()
    root_audio_dir = os.path.dirname(os.path.abspath(__file__))

    create_wwise_project(root_audio_dir, wwise_console_path)

    for wav_file in sys.argv[1:]:
        if wav_file.lower().endswith(".wav"):
            convert_wav_to_wem(wav_file, root_audio_dir, wwise_console_path)
        else:
            print(f"Skipping non-WAV file: {wav_file}")