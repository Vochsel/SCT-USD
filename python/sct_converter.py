import os
import struct
import math
import argparse

from pxr import Usd, UsdGeom, Gf

SCT_FPS = 60.0
SCT_CAMERA_FRAME_SIZE = 44


def create_usd_file(data, export_path):
    s = Usd.Stage.CreateInMemory()

    s.SetMetadata("comment","Converted USD Stage from SCT {0} file".format(
        data["source_path"]))

    s.SetFramesPerSecond(SCT_FPS)

    cam = UsdGeom.Camera.Define(s, "/capture/camera")


    cam.CreateHorizontalApertureAttr().Set(data["horizontalFOV"])
    cam.CreateVerticalApertureAttr().Set(data["verticalFOV"])
    cam.CreateFocalLengthAttr().Set(data["focalLengthX"] / 10)

    for f in data["camera_data"]:
        timecode = math.ceil(
            (f[0] - data["camera_data"][0][0]) * SCT_FPS) + 3
        UsdGeom.XformCommonAPI(cam).SetTranslate(
            Gf.Vec3d(f[1]["x"], f[1]["y"], f[1]["z"]), timecode)
        UsdGeom.XformCommonAPI(cam).SetRotate(Gf.Vec3f(
            f[2]["x"], f[2]["y"], f[2]["z"]), UsdGeom.XformCommonAPI.RotationOrderXYZ, timecode)

    s.Export(export_path or "output.usda")


def read_camera_transform(data):
    d = struct.unpack("<d7fd", data)

    return (
        d[0],
        {"x": d[1], "y": d[2], "z": d[3]},
        {"x": math.degrees(d[4]), "y": math.degrees(d[5]),
         "z": math.degrees(-d[6])},
        d[7],
        d[8]
    )


def extract_sct_data(filepath):
    print("Converting..")

    sct_data = {}
    sct_data["source_path"] = filepath

    with open(filepath, "rb") as capture_dat:

        sct_data["version"] = struct.unpack("i", capture_dat.read(4))[0]
        sct_data["frameCount"] = struct.unpack("i", capture_dat.read(4))[0]
        sct_data["deviceOrientation"] = struct.unpack(
            "i", capture_dat.read(4))[0]
        sct_data["horizontalFOV"] = struct.unpack("f", capture_dat.read(4))[0]
        sct_data["verticalFOV"] = struct.unpack("f", capture_dat.read(4))[0]
        sct_data["focalLengthX"] = struct.unpack("f", capture_dat.read(4))[0]
        sct_data["focalLengthY"] = struct.unpack("f", capture_dat.read(4))[0]
        sct_data["captureType"] = struct.unpack("i", capture_dat.read(4))[0]

        sct_data["camera_data"] = []

        cameraData = capture_dat.read(SCT_CAMERA_FRAME_SIZE)
        while cameraData:
            sct_data["camera_data"].append(read_camera_transform(cameraData))
            cameraData = capture_dat.read(SCT_CAMERA_FRAME_SIZE)

    return sct_data

def convert_video(video_path, output_image_dir):
    
    ffmpeg_cmd = "ffmpeg -i \"{video}\" -vf fps={fps} \"{output_dir}/frame_%04d.png\"".format(video=video_path, fps=SCT_FPS, output_dir=output_image_dir)
    os.makedirs(output_image_dir)
    os.system(ffmpeg_cmd)

def main():
    # Parse Args

    parser = argparse.ArgumentParser(
        description="Tool to convert binary .dat SCT (Spatial Camera Tracker) data to USD (Universal Scene Description)")

    parser.add_argument("input_data", type=str,
                        help="The .dat file containing trackign information")
    parser.add_argument("--output_usd", "-o", type=str,
                        default=None, help="Output path for USD file")

    parser.add_argument("--video", "-v", type=str,
                        default=None, help="Video path")
    parser.add_argument("--output_images", "-i", type=str,
                        default=None, help="Output image directory")

    args = parser.parse_args()

    # Convert data

    sct_data = extract_sct_data(args.input_data)

    # Create USD file

    create_usd_file(sct_data, args.output_usd)

    # Convert videos

    if args.video and args.output_images:
        convert_video(args.video, args.output_images)


if __name__ == "__main__":
    main()
