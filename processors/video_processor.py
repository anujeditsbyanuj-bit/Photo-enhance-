import cv2
import numpy as np
import os
import logging
import subprocess
from pathlib import Path

logger = logging.getLogger(__name__)

class VideoProcessor:
    """AI Video Enhancement Processor"""
    
    @staticmethod
    def enhance_video(
        input_path: str,
        output_path: str,
        enhancement_type: str = "auto"
    ) -> bool:
        """Video enhance karo frame by frame"""
        try:
            cap = cv2.VideoCapture(input_path)
            
            if not cap.isOpened():
                logger.error("Video open nahi hua")
                return False
            
            # Video properties
            fps = int(cap.get(cv2.CAP_PROP_FPS))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            logger.info(f"Video: {width}x{height} @ {fps}fps, {total_frames} frames")
            
            # Output writer
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
            
            frame_count = 0
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Enhance each frame
                enhanced = VideoProcessor._enhance_frame(frame, enhancement_type)
                out.write(enhanced)
                
                frame_count += 1
                
                # Progress log every 30 frames
                if frame_count % 30 == 0:
                    progress = (frame_count / total_frames) * 100
                    logger.info(f"Progress: {progress:.1f}%")
            
            cap.release()
            out.release()
            
            logger.info(f"Video enhanced: {frame_count} frames processed")
            return True
            
        except Exception as e:
            logger.error(f"Video enhance error: {e}")
            return False
    
    @staticmethod
    def _enhance_frame(frame: np.ndarray, enhancement_type: str) -> np.ndarray:
        """Single frame enhance karo"""
        try:
            if enhancement_type == "auto":
                # Denoise
                enhanced = cv2.fastNlMeansDenoisingColored(frame, None, 5, 5, 7, 21)
                
                # CLAHE
                lab = cv2.cvtColor(enhanced, cv2.COLOR_BGR2LAB)
                l, a, b = cv2.split(lab)
                clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
                cl = clahe.apply(l)
                merged = cv2.merge((cl, a, b))
                enhanced = cv2.cvtColor(merged, cv2.COLOR_LAB2BGR)
                
                # Sharpen
                kernel = np.array([[0,-1,0],[-1,5,-1],[0,-1,0]])
                enhanced = cv2.filter2D(enhanced, -1, kernel)
                
                return enhanced
                
            elif enhancement_type == "stabilize":
                return frame  # Future: add stabilization
                
            elif enhancement_type == "denoise":
                return cv2.fastNlMeansDenoisingColored(frame, None, 10, 10, 7, 21)
                
            elif enhancement_type == "hdr":
                lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
                l, a, b = cv2.split(lab)
                clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
                cl = clahe.apply(l)
                merged = cv2.merge((cl, a, b))
                return cv2.cvtColor(merged, cv2.COLOR_LAB2BGR)
                
            elif enhancement_type == "sharpen":
                kernel = np.array([[-1,-1,-1],[-1,9,-1],[-1,-1,-1]])
                return cv2.filter2D(frame, -1, kernel)
                
            else:
                return frame
                
        except Exception as e:
            logger.error(f"Frame enhance error: {e}")
            return frame
    
    @staticmethod
    def get_video_info(video_path: str) -> dict:
        """Video information nikalo"""
        try:
            cap = cv2.VideoCapture(video_path)
            
            info = {
                "fps": int(cap.get(cv2.CAP_PROP_FPS)),
                "width": int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
                "height": int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
                "frames": int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
                "duration": int(cap.get(cv2.CAP_PROP_FRAME_COUNT) / 
                              cap.get(cv2.CAP_PROP_FPS))
            }
            
            cap.release()
            return info
            
        except Exception as e:
            logger.error(f"Video info error: {e}")
            return {}
