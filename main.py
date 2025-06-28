from fetchDataFromAPI import fetch_product_by_name
import sys
from listener import mic_listen
import cv2
import time
import threading
import argparse
from insightface.app import FaceAnalysis

from speak import ( init_dashscope_api_key, 
                    synthesis_text_to_speech_and_play_by_streaming_mode, 
                    LLM_Speak, 
                    userQueryQueue, 
                    LAST_ASSISTANT_RESPONSE, 
                    STOP_EVENT, 
                    NOW_SPEAKING,
                    USER_ABSENT)

from greetings import (male_greetings, 
                       female_greetings, 
                       neutral_greetings)
from suggestion import AUTO_SUGGESTIONS
from chat import SYSTEM_PROMPT, NO_RESPONSE_NEEDED_RULE
from echocheck import is_likely_system_echo
import random
import os
import multiprocessing

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    print("Warning: psutil not installed - CPU monitoring disabled. Install with: pip install psutil")

# Import CPU optimizer
from cpu_optimizer import get_optimizer, optimize_process_priority, enable_cpu_affinity_optimization

# Argument parser for headless mode
parser = argparse.ArgumentParser()
parser.add_argument("--headless", action="store_true", help="Run without GUI display")
# Cam id
parser.add_argument("--camid", type=int, default=1, help="Camera ID")
args = parser.parse_args()

absence_threshold = 5  # seconds

# Speaking and suggestion variables
face_detected = False
suggest_interval = 30  # seconds
stop_event = threading.Event()
is_greeted = False

# Face distance estimation constants
KNOWN_FACE_WIDTH = 0.15  # Average human face width in meters (15cm)
FOCAL_LENGTH = 500  # Approximate focal length, will need calibration for accuracy



# Queue for sharing detected gender
gender_queue = multiprocessing.Queue()

# Helper to play speech in thread and release lock when done
def play_speech(text):
    try:
        # Don't update LAST_ASSISTANT_RESPONSE here since it's not visible to LLM_Speak thread
        synthesis_text_to_speech_and_play_by_streaming_mode(text=text)
    finally:
        NOW_SPEAKING.release()

# Auto-suggest thread function
def suggest_loop():
    while not stop_event.is_set():
        time.sleep(suggest_interval)
        if face_detected and NOW_SPEAKING.acquire(blocking=False):
            index = random.randint(0, len(AUTO_SUGGESTIONS) - 1)
            t = threading.Thread(target=play_speech, args=(f"。　{AUTO_SUGGESTIONS[index]}　。",), daemon=True)
            t.start()

def speak_loop():
    while not stop_event.is_set():
        time.sleep(1)
        if face_detected and NOW_SPEAKING.acquire(blocking=False):
            t = threading.Thread(target=play_speech, args=(f"。　{AUTO_SUGGESTIONS[index]}　。",), daemon=True)
            t.start()


GREETINGs = []

# Greet user based on detected gender
def greet_user():
    global is_greeted, GREETINGs
    gender = gender_queue.get()
    greeting = random.choice(GREETINGs)
    if gender == 'M':
        # age = age_queue.get()
        text = f"。先生　{greeting}　。"
        # lst = male_greetings
    elif gender == 'F':
        text = f"。女士　{greeting}　。"
        # lst = female_greetings
    else:
        text = f"。　{greeting}　。"
        # lst = neutral_greetings
    t = threading.Thread(target=play_speech, args=(text,), daemon=True)
    t.start()
    is_greeted = True

# Calculate distance from face width
def calculate_distance(face_width_pixels):
    # Using the formula: distance = (known_width * focal_length) / perceived_width
    distance = (KNOWN_FACE_WIDTH * FOCAL_LENGTH) / face_width_pixels
    return distance

def age_detection(age):

    if age < 18:
        return "小朋友"
    elif age < 25:
        return "年轻人"
    elif age < 35:
        return "中年人"

# Face detection loop - ULTRA OPTIMIZED WITH ADAPTIVE PERFORMANCE
def face_detection_loop():
    global face_detected, is_greeted
    absent = False
    # Absence timer variables
    absence_start = None
    # Distance threshold timer
    distance_threshold = 1.0  # meters
    distance_far_start = None
    
    # Get CPU optimizer for adaptive performance
    optimizer = get_optimizer()
    
    # Performance optimization variables - ADAPTIVE
    # These will be dynamically adjusted based on CPU usage
    TARGET_FPS = 3  # Default, will be adjusted
    frame_time = 1.0 / TARGET_FPS
    last_frame_time = 0
    skip_frame_count = 0
    FRAME_SKIP_WHEN_ABSENT = 8  # Default, will be adjusted
    last_face_detection_time = 0
    FACE_DETECTION_INTERVAL = 0.6  # Default, will be adjusted
    
    # Adaptive performance update timer
    last_perf_update = 0
    PERF_UPDATE_INTERVAL = 3.0  # Update performance settings every 3 seconds
    
    # CPU monitoring for dynamic adjustment - ENHANCED
    last_cpu_check = 0
    CPU_CHECK_INTERVAL = 1.5  # Check CPU every 1.5 seconds for faster response
    adaptive_frame_skip = 0
    cpu_high_threshold = 70  # Reduced from 80 to 70 for earlier throttling
    cpu_low_threshold = 40   # Reduced from 50 to 40 for better performance recovery
    
    # Disable frame saving to reduce I/O overhead
    ENABLE_FRAME_SAVING = False  # Completely disable frame saving for CPU optimization
    
    # Initialize face analysis with ADAPTIVE optimized settings
    app = FaceAnalysis(allowed_modules=['detection', 'genderage'])
    
    # Get initial performance settings
    perf_settings = optimizer.get_performance_settings()
    det_size = perf_settings['detection_size']
    camera_res = perf_settings['camera_resolution']
    
    app.prepare(ctx_id=-1, det_size=det_size)  # Adaptive detection size
    cap = cv2.VideoCapture(args.camid)
    
    # Optimize camera settings with ADAPTIVE resolution
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, camera_res[0])  # Adaptive width
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, camera_res[1])  # Adaptive height
    cap.set(cv2.CAP_PROP_FPS, perf_settings['face_detection_fps'])  # Adaptive FPS
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Minimize buffer to avoid lag
    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))  # Use MJPEG for better performance
    cap.set(cv2.CAP_PROP_AUTOFOCUS, 0)  # Disable autofocus to save CPU
    cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.25)  # Reduce auto-exposure processing
    
    try:
        while True:
            current_time = time.time()
            
            # Update adaptive performance settings
            if current_time - last_perf_update > PERF_UPDATE_INTERVAL:
                perf_settings = optimizer.get_performance_settings()
                TARGET_FPS = perf_settings['face_detection_fps']
                frame_time = 1.0 / TARGET_FPS
                FACE_DETECTION_INTERVAL = perf_settings['face_detection_interval']
                FRAME_SKIP_WHEN_ABSENT = max(8, int(8 * perf_settings['sleep_multiplier']))
                last_perf_update = current_time
            
            # Dynamic CPU monitoring and adaptive frame skipping
            if PSUTIL_AVAILABLE and current_time - last_cpu_check > CPU_CHECK_INTERVAL:
                try:
                    cpu_percent = psutil.cpu_percent(interval=0.05)  # Faster CPU check
                    if cpu_percent > cpu_high_threshold:  # High CPU usage
                        adaptive_frame_skip = min(adaptive_frame_skip + 2, 5)  # More aggressive skipping
                        print(f"High CPU detected ({cpu_percent:.1f}%), increasing frame skip to {adaptive_frame_skip}")
                    elif cpu_percent < cpu_low_threshold:  # Low CPU usage
                        adaptive_frame_skip = max(adaptive_frame_skip - 1, 0)
                    last_cpu_check = current_time
                except Exception as e:
                    print(f"CPU monitoring error: {e}")
                    adaptive_frame_skip = 0
            
            # Frame rate limiting with adaptive skipping - OPTIMIZED
            if current_time - last_frame_time < frame_time:
                sleep_time = 0.05 * perf_settings['sleep_multiplier']  # Adaptive sleep time
                time.sleep(sleep_time)
                continue
            last_frame_time = current_time
            
            ret, frame = cap.read()
            if not ret:
                break
                
            # Enhanced frame skipping logic - ULTRA OPTIMIZED
            total_skip_frames = FRAME_SKIP_WHEN_ABSENT + adaptive_frame_skip
            if absent and skip_frame_count < total_skip_frames:
                skip_frame_count += 1
                sleep_time = 0.1 * perf_settings['sleep_multiplier']  # Adaptive sleep during skipping
                time.sleep(sleep_time)
                continue
            skip_frame_count = 0
            
            rotated = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
            
            # Only run face detection at intervals, not every frame - with caching
            if current_time - last_face_detection_time >= FACE_DETECTION_INTERVAL:
                try:
                    faces = app.get(rotated)
                    last_face_detection_time = current_time
                    # Cache successful detection results
                    cached_faces = faces
                except Exception as e:
                    print(f"Face detection error: {e}")
                    # Use cached results on error
                    faces = cached_faces if 'cached_faces' in locals() else []
            else:
                # Use cached face detection results to save CPU
                faces = cached_faces if 'cached_faces' in locals() else []
            
            face_detected = bool(faces)
            distance_too_far = False
            closest_face_distance = float('inf')
            closest_face_gender = None

            # Absence detection logic
            if face_detected:
                absence_start = None
                absent = False
                
                # Process each detected face
                for face in faces:
                    x1, y1, x2, y2 = map(int, face.bbox)
                    face_width = x2 - x1
                    
                    # Calculate distance in meters
                    distance = calculate_distance(face_width)
                    
                    # Track closest face for greeting
                    if distance < closest_face_distance:
                        closest_face_distance = distance
                        closest_face_gender = face.sex
                    
                    # Check if distance is too far
                    if distance > distance_threshold:
                        distance_too_far = True
                        if distance_far_start is None:
                            distance_far_start = current_time
                        else:
                            elapsed = current_time - distance_far_start
                            if elapsed >= absence_threshold:
                                absent = True
                            remaining = max(0, absence_threshold - int(elapsed))
                            far_text = f"Too far: {remaining}s"
                            cv2.putText(frame, far_text, (20, 120), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 255), 2)
                    else:
                        distance_far_start = None
                    
                    label = f"{face.sex}:{face.age}"
                    distance_label = f"Distance: {distance:.2f}m"
                    
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
                    cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
                    cv2.putText(frame, distance_label, (x1, y2 + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
                    
                    # FRAME SAVING COMPLETELY DISABLED FOR CPU OPTIMIZATION
                    # Frame saving causes significant I/O overhead and is disabled for performance
                
                # Greeting logic - only greet if user is close enough
                if not is_greeted and not distance_too_far and closest_face_distance <= distance_threshold:
                    if NOW_SPEAKING.acquire(blocking=False):
                        gender_queue.put(closest_face_gender)
                        threading.Thread(target=greet_user, daemon=True).start()
                
                # If all faces are not too far, reset the timer
                if not distance_too_far:
                    distance_far_start = None
            else:
                if absence_start is None:
                    absence_start = current_time
                else:
                    elapsed = current_time - absence_start
                    if elapsed >= absence_threshold:
                        absent = True
                    remaining = max(0, absence_threshold - int(elapsed))
                    timer_text = f"User away: {remaining}s"
                    cv2.putText(frame, timer_text, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 2)

            if absent:
                cv2.putText(frame, "User not exist", (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 2)
                is_greeted = False
                face_detected = False
                if distance_too_far:
                    cv2.putText(frame, "User too far", (20, 160), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 255), 2)
                # Set the USER_ABSENT event when user is absent or too far
                USER_ABSENT.set()
            else:
                # Clear the USER_ABSENT event when user is present and not too far
                USER_ABSENT.clear()

            if not args.headless:
                cv2.imshow("InsightFace", frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            else:
                # Adaptive sleep in headless mode for CPU optimization
                sleep_time = 0.15 * perf_settings['sleep_multiplier']  # Adaptive sleep time
                time.sleep(sleep_time)

    finally:
        stop_event.set()
        cap.release()
        if not args.headless:
            cv2.destroyAllWindows()


def get_user_input():
    mic_listen()
    
# def get_user_input():
#     global userQueryQueue
#     while True:
#         user_input = input("Enter text to synthesize: ")
#         if is_likely_system_echo(user_input, LAST_ASSISTANT_RESPONSE):
#             print("Detected system echo, skipping response")
#             continue
#         userQueryQueue.put(user_input)

if __name__ == "__main__":
    
    # print(NO_RESPONSE_NEEDED_RULE)
    # global AUTO_SUGGESTIONSs
    # global GREETINGs
    
    # Initialize CPU optimizations
    print("Initializing CPU optimizations...")
    optimize_process_priority()
    enable_cpu_affinity_optimization()
    
    # Start CPU monitoring
    cpu_optimizer = get_optimizer()
    cpu_optimizer.start_monitoring()
    
    # Initialize TTS
    print("Initializing TTS API...")
    init_dashscope_api_key()    

    print("Fetching product data from API...")
    try:
        api_result = fetch_product_by_name("6")
        if 'error' in api_result:
            print(f"API Error: {api_result['error']}")
            print("Using fallback configuration...")
            result = None
        else:
            result = api_result['data']
            print("Product data loaded successfully.")
    except Exception as e:
        print(f"Failed to fetch API data: {e}")
        print("Using fallback configuration...")
        result = None
    # print(f"RES:::: {result}")
    # sys.exit(0)
    if result and result.get("products") and result.get("prompt") and result.get("greetings") and result.get("suggestions"):
        products = result.get("products")
        prompt = result.get("prompt")

        prompt += "你可以推荐以下饮品：\n" + ",".join(products)    
        prompt += NO_RESPONSE_NEEDED_RULE
        SYSTEM_PROMPT = prompt
        # print(result.get("greetings"))
        GREETINGs = result.get("greetings")
        AUTO_SUGGESTIONS = result.get("suggestions")
        # print(AUTO_SUGGESTIONS)
    else:
        print("Using default configuration...")
        # Fallback configuration
        GREETINGs = ["欢迎光临", "您好", "欢迎"]
        AUTO_SUGGESTIONS = ["需要推荐吗?", "要试试我们的招牌饮品吗?", "有什么可以帮您的?"]
        SYSTEM_PROMPT = "你是一个友好的咖啡店助手。" + NO_RESPONSE_NEEDED_RULE
    print("Starting application threads...")
    threading.Thread(target=face_detection_loop, daemon=True).start()
    threading.Thread(target=LLM_Speak, args=(SYSTEM_PROMPT,), daemon=True).start()
    threading.Thread(target=suggest_loop, daemon=True).start()
    threading.Thread(target=mic_listen, daemon=True).start()
    # threading.Thread(target=get_user_input, daemon=True).start()
    
    print("Application started successfully!")
    
    # Prevent main thread from exiting
    while not stop_event.is_set():
        time.sleep(1)