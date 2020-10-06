import numpy as np
import cv2
import imutils


class ImageProcessor:
    def __init__(self, img: np.ndarray):
        """
        Preprocess image for CAPTCHA solver
        Args:
            img: image of interest, must be RGB or grayscale
        """
        self.img = img

    def median_filter(self, img=None, kernel_size=3) -> np.ndarray:
        """
        Apply median filter

        Args:
            img: target image
            kernel_size: size of kernel
        """
        if img is None:
            img = self.img

        return cv2.medianBlur(src=img, ksize=kernel_size)

    def blur_filter(self,
                    img=None,
                    kernel_size=(3, 3),
                    gaussian=True,
                    sigma_x=0) -> np.ndarray:
        """Apply blur filter (smoothing)

        Args:
            img: target image
            kernel_size: size of kernel
            gaussian: flag to use Gaussian blur
            sigma_x: Gaussian kernel standard deviation in X direction
        """
        if img is None:
            img = self.img

        if isinstance(kernel_size, int):
            kernel_size = (kernel_size, kernel_size)

        if gaussian:
            return cv2.GaussianBlur(src=img, ksize=kernel_size,
                                    sigmaX=sigma_x)
        else:
            return cv2.blur(src=img, ksize=kernel_size)

    def open_close(self, img=None, kernel_size=3, niter=1) -> np.ndarray:
        """Morphological operations (open and close)

        Args:
            img: target image
            kernel_size: size of kernel
            niter: number of open-close iterations
        """
        if img is None:
            img = self.img

        kernel = np.ones((kernel_size, kernel_size), np.uint8)

        for _ in range(niter):
            cv2.morphologyEx(src=img, dst=img, op=cv2.MORPH_OPEN,
                             kernel=kernel)
            cv2.morphologyEx(src=img, dst=img, op=cv2.MORPH_CLOSE,
                             kernel=kernel)
        return img

    def dilate(self, img=None, kernel_size=3) -> np.ndarray:
        """Dilate image

        Args:
            kernel_size: size of kernel
            img: target image
        """
        if img is None:
            img = self.img

        kernel = np.ones((kernel_size, kernel_size), np.uint8)
        return cv2.dilate(img, kernel, iterations=1)

    def erode(self, img=None, kernel_size=3) -> np.ndarray:
        """Erode image

        Args:
            img: target image
            kernel_size: size of kernel
        """
        if img is None:
            img = self.img

        kernel = np.ones((kernel_size, kernel_size), np.uint8)
        return cv2.erode(img, kernel, iterations=1)

    def threshold(
            self,
            img=None,
            threshold_value=150,
            max_value=255,
            threshold_type=cv2.THRESH_BINARY+cv2.THRESH_OTSU
    ) -> np.ndarray:
        """
        Apply simple threshold (default: OTSU)

        Args:
            img: target image
            threshold_value: threshold below and above pixel values will
            change accordingly
            max_value: max value that can be assigned to a pixel
            threshold_type: type of threshold, default to
            cv2.THRESH_BINARY+cv2.THRESH_OTSU
        """
        if img is None:
            img = self.img

        _, thr = cv2.threshold(src=img, thresh=threshold_value,
                               maxval=max_value, type=threshold_type)
        return thr

    def adaptive_threshold(
            self,
            img=None,
            max_value=255,
            block_size=3,
            adaptive_method=cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            threshold_type=cv2.THRESH_BINARY,
            c=2
    ) -> np.ndarray:
        """
        Apply adaptive threshold

        Args:
            img: target image
            block_size: size of pixel neighborhood, must be an odd number (
            3, 5, 7 and so on)
            adaptive_method: method of adaptive threshold, default as
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C
            max_value: max value that can be assigned to a pixel
            threshold_type: type of threshold, must be cv2.THRESH_BINARY or
            cv2.THRESH_BINARY_INV
            c: constant to be subtracted from the mean (usually, a positive
            int)
        """
        if img is None:
            img = self.img

        if len(img.shape) > 2:
            gray_img = self.convert_color(color_code=cv2.COLOR_RGB2GRAY)
        else:
            gray_img = img
        return cv2.adaptiveThreshold(src=gray_img,
                                     maxValue=max_value,
                                     adaptiveMethod=adaptive_method,
                                     blockSize=block_size,
                                     thresholdType=threshold_type,
                                     C=c)

    def convert_color(self,
                      img=None,
                      color_code=cv2.COLOR_RGB2GRAY) -> np.ndarray:
        """
        Convert image's color

        Args:
            img: target image
            color_code: must be one of 'cv2.COLOR_'
        """
        if img is None:
            img = self.img

        return cv2.cvtColor(img, color_code)

    def resize(self,
               width: [int, float],
               height: [int, float],
               img=None) -> np.ndarray:
        """
        Resize image

        Args:
            img: target image
            width: desired width
            height: desired height
        """
        if img is None:
            img = self.img

        return cv2.resize(img, (width, height))

    def get_contours(self,
                     img=None,
                     preprocess=False,
                     canny_threshold_low=30,
                     canny_threshold_up=200,
                     find_contours_method=cv2.CHAIN_APPROX_SIMPLE,
                     find_contours_mode=cv2.RETR_TREE,
                     sort_contours_key=cv2.contourArea,
                     ) -> list:
        """
        Resize image

        Args:
            img: target image
            preprocess: whether to preprocess the image or not
            find_contours_mode: see ContourApproximationModes (openCV doc)
            find_contours_method: see RetrievalModes (openCV doc)
            sort_contours_key: key to sort contours (currently sort by area)
            canny_threshold_low: lower Canny threshold value
            canny_threshold_up: upper Canny threshold value
        """
        if img is None:
            img = self.img

        if preprocess:
            img = self.preprocess(img)

        if len(img.shape) > 2:
            gray_img = self.convert_color(img, color_code=cv2.COLOR_RGB2GRAY)
        else:
            gray_img = img

        edged = cv2.Canny(image=gray_img,
                          threshold1=canny_threshold_low,
                          threshold2=canny_threshold_up)
        contours = cv2.findContours(image=edged.copy(),
                                    mode=find_contours_mode,
                                    method=find_contours_method)

        contours = imutils.grab_contours(contours)
        contours = sorted(contours, key=sort_contours_key, reverse=True)

        return contours

    @staticmethod
    def get_bounding_boxes(contours, split_threshold=1.3) -> list:
        """
        Return bounding boxes for each contour found. Can be used to slice
        the image

        Args:
            contours: contours list
            split_threshold: split bounding box in two if width >
            split_threshold * height
        """
        contours_copy = contours
        rectangle_list = []
        while contours_copy:
            x, y, w, h = cv2.boundingRect(contours_copy)
            if w > split_threshold * h:
                rectangle_list.append((x, y, w//2, h))
                rectangle_list.append((x+w//2, y, w//2, h))
            else:
                rectangle_list.append((x, y, w, h))
            contours_copy = contours_copy.h_next()
        return rectangle_list

    def crop(self, x, y, height, width, img=None) -> np.ndarray:
        """
        Return cropped image from bounding box

        Args:
            img: target image
            width: width of bounding box
            height: height of bounding box
            y: y coordinate of top left corner of bounding box
            x: x coordinate of top left corner of bounding box
        """
        if img is None:
            img = self.img

        if len(img.shape) > 2:
            return img[y:y + height, x:x + width, :]
        else:
            return img[y:y + height, x:x + width]

    def preprocess(self,
                   img=None,
                   open_close=True,
                   dilate=True,
                   erode=True,
                   blur=True,
                   threshold=True) -> np.ndarray:
        """
        Returns preprocessed image. Uses the following operations:
        open/close, erode/dilate, blurring and thresholding (adaptive)

        Args:
            img: target image
            open_close: if True, performs open and close operation with
            default settings
            dilate: if True, performs dilation with default settings
            erode: if True, performs erosion with default settings
            blur: if True, performs blurring with default settings
            threshold: if True, performs adaptive threshold with
            default settings
        """
        if img is None:
            img = self.img

        if open_close:
            img = self.open_close(img=img)
        if dilate:
            img = self.dilate(img=img)
        if erode:
            img = self.erode(img=img)
        if blur:
            img = self.blur_filter(img=img)
        if threshold:
            img = self.adaptive_threshold(img=img)

        return img
