# import cv2

# # Load your horizontal image
# image = cv2.imread('frame_1750931326.9356942.jpg')

# # Rotate 90° clockwise to make vertical
# rotated = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)

# # Save the vertical image (new file to preserve original)
# cv2.imwrite('vertical_frame_1750931326.9356942.jpg', rotated)

# print("Image rotated and saved as 'vertical_frame_1750931326.9356942.jpg'")

import cv2
path = r'./frame_1750931326.9356942.jpg'
src = cv2.imread(path)
rotated = cv2.rotate(src, cv2.ROTATE_90_COUNTERCLOCKWISE)

cv2.imshow("270° Clockwise", rotated)
cv2.waitKey(0)
cv2.destroyAllWindows()