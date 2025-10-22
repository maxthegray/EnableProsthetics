import os
import subprocess
import csv
from stl import mesh
import numpy as np
import sys

def get_stl_size(stl_file):
    stl_mesh = mesh.Mesh.from_file(stl_file)
    vertices = stl_mesh.vectors.reshape(-1, 3)
    min_point = np.min(vertices, axis=0)
    max_point = np.max(vertices, axis=0)
    size = max_point - min_point
    return size

def check_size(stl_file):
    size = get_stl_size(stl_file)
    max_size = 240
    if np.all(size <= max_size):
        return True
    return False

def render_part(part, side, hand_width_mm, arm_length_mm, forearm_circumference_mm, bicep_circumference_mm, arm_pieces, cover_pieces, open_scad_file, output_dir):
    # Ensure the output directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Correct output file path with .stl extension
    output_file = os.path.join(output_dir, f"{part}.stl")

    # Command with explicit export format
    command = [
        "/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD",
        "--export-format", "stl",  # Explicitly define the export format as STL
        "-o", output_file,  # No extra quotes here
        "-D", f"part=\"{part}\"",
        "-D", f"Side=\"{side}\"",
        "-D", f"HandWidth={hand_width_mm}",
        "-D", f"ArmLength={arm_length_mm}",
        "-D", f"ForearmCircumference={forearm_circumference_mm}",
        "-D", f"BicepCircumference={bicep_circumference_mm}",
        "-D", "PaddingThickness=4",
        "-D", f"ArmPieces={arm_pieces}",
        "-D", f"CoverPieces={cover_pieces}",
        "-D", "PalmBoltDiameter=4",
        "-D", "CoverPinDiameter=6",
        "-D", "ElbowBoltDiameter=6",
        "-D", "TensionerBoltDiameter=2",
        "-D", "GripLatch=\"Yes\"",
        "-D", "PencilHolder=\"Yes\"",
        open_scad_file  # No extra quotes around OpenSCAD file path
    ]

    # Run the command and capture output and error
    result = subprocess.run(command, capture_output=True, text=True)

    # Print output and error for debugging
    if result.returncode != 0:
        print(f"Error rendering part {part}:")
        print(f"Error: {result.stderr}")
    else:
        print(f"Successfully rendered {part}.stl")

def check_fit(stl_file):
    if not check_size(stl_file):
        print(f"Error: {stl_file} exceeds maximum allowed size.")
        return False
    return True

def process_case(case_data, csv_file, open_scad_file, kwawu_files_dir):
    case_name, side, hand_width_mm, arm_length_mm, forearm_circumference_mm, bicep_circumference_mm = case_data

    case_dir = os.path.join(kwawu_files_dir, case_name)
    petg_dir = os.path.join(case_dir, "PETG")
    tpu_dir = os.path.join(case_dir, "TPU")
    pla_dir = os.path.join(case_dir, "PLA")

    os.makedirs(case_dir, exist_ok=True)
    os.makedirs(petg_dir, exist_ok=True)
    os.makedirs(tpu_dir, exist_ok=True)
    os.makedirs(pla_dir, exist_ok=True)

    petg_parts = ["Cuff", "Palm", "PalmTop", "WristArmAttach", "WristBolt", "Tensioner", "IndexFingerEnd", "IndexFingerPhalanx",
                  "MiddleFingerEnd", "MiddleFingerPhalanx", "PinkyFingerEnd", "PinkyFingerPhalanx", "RingFingerEnd", "RingFingerPhalanx",
                  "ThumbEnd", "ThumbPhalanx", "WhippleTreePrimary", "WhippleTreeSecondary", "LatchSlider", "LatchPin", "LatchTeeth"]
    tpu_parts = ["Hinge4Knuckles", "HingeIndexFinger", "HingeMiddleFinger", "HingePinkyFinger", "HingeRingFinger", "HingeThumb",
                 "HingeThumbKnuckle", "PencilHolderCover", "WristCompressionBushing", "LatchHinge"]
    pla_parts = ["Thermoform1", "Thermoform2", "Thermoform3"]

    arm_pieces = 1
    cover_pieces = 1
    render_part("Arm1", side, hand_width_mm, arm_length_mm, forearm_circumference_mm, bicep_circumference_mm, arm_pieces, cover_pieces, open_scad_file, petg_dir)

    if not check_fit(f"{petg_dir}/Arm1.stl"):
        os.remove(f"{petg_dir}/Arm1.stl")
        arm_pieces = 2
        render_part("Arm1", side, hand_width_mm, arm_length_mm, forearm_circumference_mm, bicep_circumference_mm, arm_pieces, cover_pieces, open_scad_file, petg_dir)
        render_part("Arm2", side, hand_width_mm, arm_length_mm, forearm_circumference_mm, bicep_circumference_mm, arm_pieces, cover_pieces, open_scad_file, petg_dir)
        if not check_fit(f"{petg_dir}/Arm1.stl") or not check_fit(f"{petg_dir}/Arm2.stl"):
            os.remove(f"{petg_dir}/Arm1.stl")
            os.remove(f"{petg_dir}/Arm2.stl")
            arm_pieces = 4
            for i in range(1, 5):
                render_part(f"Arm{i}", side, hand_width_mm, arm_length_mm, forearm_circumference_mm, bicep_circumference_mm, arm_pieces, cover_pieces, open_scad_file, petg_dir)

    render_part("Cover1", side, hand_width_mm, arm_length_mm, forearm_circumference_mm, bicep_circumference_mm, arm_pieces, cover_pieces, open_scad_file, petg_dir)

    if not check_fit(f"{petg_dir}/Cover1.stl"):
        os.remove(f"{petg_dir}/Cover1.stl")
        cover_pieces = 2
        render_part("Cover1", side, hand_width_mm, arm_length_mm, forearm_circumference_mm, bicep_circumference_mm, arm_pieces, cover_pieces, open_scad_file, petg_dir)
        render_part("Cover2", side, hand_width_mm, arm_length_mm, forearm_circumference_mm, bicep_circumference_mm, arm_pieces, cover_pieces, open_scad_file, petg_dir)
        if not check_fit(f"{petg_dir}/Cover1.stl") or not check_fit(f"{petg_dir}/Cover2.stl"):
            os.remove(f"{petg_dir}/Cover1.stl")
            os.remove(f"{petg_dir}/Cover2.stl")
            cover_pieces = 4
            for i in range(1, 5):
                render_part(f"Cover{i}", side, hand_width_mm, arm_length_mm, forearm_circumference_mm, bicep_circumference_mm, arm_pieces, cover_pieces, open_scad_file, petg_dir)

    for part in petg_parts:
        render_part(part, side, hand_width_mm, arm_length_mm, forearm_circumference_mm, bicep_circumference_mm, 1, 1, open_scad_file, petg_dir)
    for part in tpu_parts:
        render_part(part, side, hand_width_mm, arm_length_mm, forearm_circumference_mm, bicep_circumference_mm, 1, 1, open_scad_file, tpu_dir)
    for part in pla_parts:
        render_part(part, side, hand_width_mm, arm_length_mm, forearm_circumference_mm, bicep_circumference_mm, 1, 1, open_scad_file, pla_dir)

def main():
    # Paths with spaces need to be escaped
    csv_file = "/System/Volumes/Data/Users/arikorpus/Desktop/Kwawu Uganda 2/Uganda 2.csv"
    open_scad_file = "/System/Volumes/Data/Users/arikorpus/Downloads/thermo/Kwawu_2.1_Prosthetic_Arm-_Thermoform_Version.scad"
    output_dir = "/System/Volumes/Data/Users/arikorpus/Desktop/Kwawu Uganda 2"

    kwawu_files_dir = os.path.join(output_dir, "Kwawu Files")
    os.makedirs(kwawu_files_dir, exist_ok=True)

    with open(csv_file, newline='') as f:
        reader = csv.reader(f)
        next(reader)  # Skip header
        for case_data in reader:
            process_case(case_data, csv_file, open_scad_file, kwawu_files_dir)

    print("Rendering complete!")

if __name__ == "__main__":
    main()

