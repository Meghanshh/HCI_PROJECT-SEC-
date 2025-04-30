import cv2
import os

def display_gestures():
    gestures_dir = 'gestures'
    for gesture_id in os.listdir(gestures_dir):
        gesture_path = os.path.join(gestures_dir, gesture_id)
        if os.path.isdir(gesture_path):
            print(f'Displaying images for gesture {gesture_id}')
            for img_file in os.listdir(gesture_path):
                img_path = os.path.join(gesture_path, img_file)
                img = cv2.imread(img_path)
                cv2.imshow(f'Gesture {gesture_id}', img)
                if cv2.waitKey(100) & 0xFF == ord('q'):
                    break
            cv2.destroyAllWindows()

display_gestures() 