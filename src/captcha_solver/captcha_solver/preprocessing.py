import numpy as np
import cv2


class ImageProcessor:
    def __init__(self, img: np.ndarray):
        """
        Preprocess image for CAPTCHA solver
        Args:
            img: image of interest, must be RGB or grayscale
        """
        self.img = img

    def median_filter(self, kernel_size=3) -> np.ndarray:
        """
        Apply median filter

        Args:
            kernel_size: size of kernel
        """
        return cv2.medianBlur(src=self.img, ksize=kernel_size)

    def blur_filter(self, kernel_size=3, gaussian=True, sigma_x=0) -> \
            np.ndarray:
        """Apply blur filter (smoothing)

        Args:
            kernel_size: size of kernel
            gaussian: flag to use Gaussian blur
            sigma_x: Gaussian kernel standard deviation in X direction
        """
        if gaussian:
            return cv2.GaussianBlur(src=self.img, ksize=kernel_size,
                                    sigmaX=sigma_x)
        else:
            return cv2.blur(src=self.img, ksize=kernel_size)

    def open_close(self, kernel_size=3, niter=1) -> np.ndarray:
        """Morphological operations (open and close)

        Args:
            kernel_size: size of kernel
            niter: number of open-close iterations
        """
        kernel = np.ones((kernel_size, kernel_size), np.uint8)
        img = self.img
        for _ in range(niter):
            cv2.morphologyEx(src=img, dst=img, op=cv2.MORPH_OPEN,
                             kernel=kernel)
            cv2.morphologyEx(src=img, dst=img, op=cv2.MORPH_CLOSE,
                             kernel=kernel)
        return img

    def dilate(self, kernel_size=3) -> np.ndarray:
        """Dilate image

        Args:
            kernel_size: size of kernel
        """
        kernel = np.ones((kernel_size, kernel_size), np.uint8)
        return cv2.dilate(self.img, kernel, iterations=1)

    def erode(self, kernel_size=3) -> np.ndarray:
        """Erode image

        Args:
            kernel_size: size of kernel
        """
        kernel = np.ones((kernel_size, kernel_size), np.uint8)
        return cv2.erode(self.img, kernel, iterations=1)

    def threshold(
            self,
            threshold_value=150,
            max_value=255,
            threshold_type=cv2.THRESH_BINARY+cv2.THRESH_OTSU
    ) -> np.ndarray:
        """
        Apply simple threshold (default: OTSU)

        Args:
            threshold_value: threshold below and above pixel values will
            change accordingly
            max_value: max value that can be assigned to a pixel
            threshold_type: type of threshold, default to
            cv2.THRESH_BINARY+cv2.THRESH_OTSU
        """
        _, thr = cv2.threshold(src=self.img, thresh=threshold_value,
                               maxval=max_value, type=threshold_type)
        return thr

    def adaptive_threshold(
            self,
            max_value=255,
            block_size=3,
            adaptive_method=cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            threshold_type=cv2.THRESH_BINARY,
            c=2
    ) -> np.ndarray:
        """
        Apply adaptive threshold

        Args:
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
        if len(self.img.shape) > 2:
            gray_img = cv2.cvtColor(self.img, cv2.COLOR_RGB2GRAY)
        else:
            gray_img = self.img
        return cv2.adaptiveThreshold(src=gray_img,
                                     maxValue=max_value,
                                     adaptiveMethod=adaptive_method,
                                     blockSize=block_size,
                                     thresholdType=threshold_type,
                                     C=c)

    def resize(self, width: [int, float], height: [int, float]) -> np.ndarray:
        """
        Resize image

        Args:
            width: desired width
            height: desired height
        """
        return cv2.resize(self.img, (width, height))

    def get_contours(self) -> list:
        # TODO: get all contours in image
        pass

    def get_bounding_boxes(self) -> list:
        # TODO: get individual bounding boxes for contours
        pass

    def preprocess(self) -> np.ndarray:
        # TODO: general image processing pipeline
        # open/close -> erode/dilate -> blurring -> threshold
        pass
