import cv2
import time
import numpy as np
from insightface.app import FaceAnalysis
import argparse

# Argument parser for headless mode
parser = argparse.ArgumentParser()
parser.add_argument("--headless", action="store_true", help="Run without GUI display")
parser.add_argument("--camid", type=int, default=0, help="Camera index to use")
args = parser.parse_args()

# Initialize face analysis with emotion detection
app = FaceAnalysis(allowed_modules=['detection', 'genderage', 'emotion'])
app.prepare(ctx_id=-1, det_size=(640, 640))

# Initialize camera
cap = cv2.VideoCapture(args.camid)

# Emotion labels mapping
emotion_labels = {
    0: "Anger",
    1: "Disgust", 
    2: "Fear",
    3: "Happy",
    4: "Sad",
    5: "Surprise",
    6: "Neutral"
}

def get_emotion_text(emotion_probs):
    """Convert emotion probabilities to readable text"""
    if emotion_probs is None or len(emotion_probs) == 0:
        return "Unknown"
    
    max_idx = np.argmax(emotion_probs)
    confidence = emotion_probs[max_idx]
    emotion_name = emotion_labels.get(max_idx, "Unknown")
    
    return f"{emotion_name} ({confidence:.2f})"

def get_top_emotions(emotion_probs, top_n=3):
    """Get top N emotions with confidence scores"""
    if emotion_probs is None or len(emotion_probs) == 0:
        return []
    
    # Get indices sorted by confidence (descending)
    sorted_indices = np.argsort(emotion_probs)[::-1]
    
    top_emotions = []
    for i in range(min(top_n, len(sorted_indices))):
        idx = sorted_indices[i]
        emotion_name = emotion_labels.get(idx, "Unknown")
        confidence = emotion_probs[idx]
        top_emotions.append((emotion_name, confidence))
    
    return top_emotions

print("Starting emotion detection...")
print("Press 'q' to quit, 'r' to reset display")

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to capture frame")
            break
        
        # Detect faces and analyze emotions
        faces = app.get(frame)
        
        if faces:
            for i, face in enumerate(faces):
                # Get bounding box
                x1, y1, x2, y2 = map(int, face.bbox)
                
                # Get basic info
                age = int(face.age) if hasattr(face, 'age') else 0
                gender = "M" if face.gender == 1 else "F" if face.gender == 0 else "?"
                
                # Get emotion information
                emotion_text = "No emotion"
                if hasattr(face, 'emotion'):
                    emotion_text = get_emotion_text(face.emotion)
                    
                    # Get top 3 emotions for detailed display
                    top_emotions = get_top_emotions(face.emotion, 3)
                    
                    # Print detailed emotion info to console
                    print(f"Face {i+1}: {gender}, Age: {age}")
                    print(f"  Primary emotion: {emotion_text}")
                    if top_emotions:
                        print("  Top emotions:")
                        for emotion, conf in top_emotions:
                            print(f"    {emotion}: {conf:.3f}")
                    print("-" * 40)
                
                # Draw face rectangle
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                
                # Create label with basic info
                label = f"{gender}:{age}"
                cv2.putText(frame, label, (x1, y1 - 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                
                # Add emotion text
                cv2.putText(frame, emotion_text, (x1, y1 - 10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
                
                # Add detailed emotions on the right side of face
                if hasattr(face, 'emotion'):
                    top_emotions = get_top_emotions(face.emotion, 3)
                    for j, (emotion, conf) in enumerate(top_emotions):
                        emotion_detail = f"{emotion}: {conf:.2f}"
                        cv2.putText(frame, emotion_detail, (x2 + 10, y1 + 20 + j * 20), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
        
        # Add instructions
        cv2.putText(frame, "Press 'q' to quit", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(frame, f"Faces detected: {len(faces)}", (10, 60), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Display frame
        if not args.headless:
            cv2.imshow("InsightFace Emotion Detection", frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('r'):
                print("Display reset")
        else:
            # In headless mode, just wait a bit
            time.sleep(0.03)
            
except KeyboardInterrupt:
    print("\nStopping on user interrupt...")
    
finally:
    cap.release()
    if not args.headless:
        cv2.destroyAllWindows()
    print("Emotion detection stopped.")