!pip install scenedetect
import os
import cv2
from scenedetect import open_video, SceneManager
from scenedetect.detectors import ContentDetector

def detect_scenes(video_path, threshold=15.0):
    video = open_video(video_path)
    manager = SceneManager()
    manager.add_detector(ContentDetector(threshold=threshold))
    manager.detect_scenes(video)
    scene_list = manager.get_scene_list()
    return [(int(start.get_frames()), int(end.get_frames())) for start, end in scene_list]

def split_scene_if_too_long(start, end, max_frames=300):
    if end - start <= max_frames:
        return [(start, end)]
    segments = []
    current = start
    while current + max_frames < end:
        segments.append((current, current + max_frames))
        current += max_frames
    segments.append((current, end))
    return segments

def extract_18_frames(video_path, scene_ranges, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    cap = cv2.VideoCapture(video_path)
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    scene_count = 0
    for (start_frame, end_frame) in scene_ranges:
        segments = split_scene_if_too_long(start_frame, end_frame)
        for (seg_start, seg_end) in segments:
            total_frames = seg_end - seg_start
            if total_frames < 18:
                continue

            step = (total_frames - 1) / 17
            frame_indices = [round(seg_start + i * step) for i in range(18)]

            scene_count += 1
            print(f"\nScene {scene_count} - Frames: {frame_indices}")
            scene_folder = os.path.join(output_dir, f"scene_{scene_count}")
            os.makedirs(scene_folder, exist_ok=True)

            for i, frame_num in enumerate(frame_indices):
                if frame_num >= total:
                    continue
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
                ret, frame = cap.read()
                if ret:
                    out_path = os.path.join(scene_folder, f"frame_{i+1}.jpg")
                    cv2.imwrite(out_path, frame)
                else:
                    print(f"Failed to read frame {frame_num}.")

    cap.release()
    print("Done extracting frames.")

def process_all_videos(input_folder, output_root, threshold=12.0):
    video_files = [f for f in os.listdir(input_folder) if f.lower().endswith(('.mp4', '.avi', '.mov', '.mkv'))]

    for video_file in video_files:
        video_path = os.path.join(input_folder, video_file)
        video_name = os.path.splitext(video_file)[0]
        output_folder = os.path.join(output_root, video_name)

        print(f"Processing: {video_file}")
        scenes = detect_scenes(video_path, threshold=threshold)
        if not scenes:
            cap = cv2.VideoCapture(video_path)
            total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            cap.release()
            scenes = [(0, total)]
            print("No scene cuts detected")

        print(f"Total scenes: {len(scenes)}")
        print("Extracting 18 frames")
        extract_18_frames(video_path, scenes, output_folder)

if __name__ == "__main__":
    input_folder = "/content/sample_data/folder/"  # Please load the files here
    output_root = "Ouput_Videos"  # Ouput Folder where all the outputs videos will be there.
    process_all_videos(input_folder, output_root)
