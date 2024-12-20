import cv2
from pyzbar.pyzbar import decode
import logging
from typing import Optional
import AVFoundation
import UIKit

class BarcodeScanner:
    def __init__(self):
        self.session = AVFoundation.AVCaptureSession.alloc().init()
        self.device = self._get_camera_device()
        self.setup_logging()
        self.initialize_capture_session()

    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def _get_camera_device(self) -> Optional[AVFoundation.AVCaptureDevice]:
        devices = AVFoundation.AVCaptureDevice.devicesWithMediaType_(
            AVFoundation.AVMediaTypeVideo
        )
        for device in devices:
            if device.position() == AVFoundation.AVCaptureDevicePositionBack:
                return device
        self.logger.error("No back camera found")
        return None

    def initialize_capture_session(self):
        if not self.device:
            raise RuntimeError("Camera device not available")

        input_device = AVFoundation.AVCaptureDeviceInput.deviceInputWithDevice_error_(
            self.device, None
        )[0]
        
        if self.session.canAddInput_(input_device):
            self.session.addInput_(input_device)
        else:
            raise RuntimeError("Could not add camera input to session")

        self.output = AVFoundation.AVCaptureVideoDataOutput.alloc().init()
        if self.session.canAddOutput_(self.output):
            self.session.addOutput_(self.output)
        else:
            raise RuntimeError("Could not add video output to session")

    def scan_barcode(self) -> str:
        """
        Activates the camera, scans for a barcode, and returns the decoded value.
        
        Returns:
            str: The decoded barcode value
            
        Raises:
            RuntimeError: If scanning fails or no barcode is detected
        """
        try:
            self.session.startRunning()
            
            # Get frame from camera
            sampleBuffer = self.output.copyNextSampleBuffer()
            if not sampleBuffer:
                raise RuntimeError("Failed to get camera frame")

            # Convert to OpenCV format
            image = self._convert_sample_buffer_to_image(sampleBuffer)
            
            # Decode barcode
            decoded_objects = decode(image)
            
            if not decoded_objects:
                raise RuntimeError("No barcode detected")
                
            # Get first detected barcode
            barcode_data = decoded_objects[0].data.decode('utf-8')
            self.logger.info(f"Successfully scanned barcode: {barcode_data}")
            
            return barcode_data
            
        except Exception as e:
            self.logger.error(f"Error scanning barcode: {str(e)}")
            raise
            
        finally:
            self.session.stopRunning()

    def _convert_sample_buffer_to_image(self, sampleBuffer):
        """Convert AVCaptureVideoDataOutput to OpenCV format"""
        imageBuffer = AVFoundation.CMSampleBufferGetImageBuffer(sampleBuffer)
        
        CVPixelBufferLockBaseAddress(imageBuffer, 0)
        baseAddress = CVPixelBufferGetBaseAddress(imageBuffer)
        
        width = CVPixelBufferGetWidth(imageBuffer)
        height = CVPixelBufferGetHeight(imageBuffer)
        
        # Create OpenCV mat
        img = cv2.cvtColor(
            numpy.array(baseAddress).reshape(height, width, 4),
            cv2.COLOR_BGRA2BGR
        )
        
        CVPixelBufferUnlockBaseAddress(imageBuffer, 0)
        
        return img

    def __del__(self):
        """Cleanup when object is destroyed"""
        if hasattr(self, 'session'):
            self.session.stopRunning()