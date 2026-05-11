"""
Media Handler
Manages images, video, and audio files
"""

from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
import hashlib


class MediaHandler:
    """Handle media file operations"""
    
    def __init__(self, base_path: Path):
        self.base_path = Path(base_path)
        (self.base_path / "images").mkdir(parents=True, exist_ok=True)
        (self.base_path / "video").mkdir(parents=True, exist_ok=True)
        (self.base_path / "audio").mkdir(parents=True, exist_ok=True)
    
    def get_image_metadata(self, file_path: str) -> Dict:
        """Get image metadata"""
        try:
            from PIL import Image
            from PIL.ExifTags import TAGS
            
            with Image.open(file_path) as img:
                metadata = {
                    "format": img.format,
                    "mode": img.mode,
                    "width": img.width,
                    "height": img.height,
                    "size_bytes": Path(file_path).stat().st_size
                }
                
                # Extract EXIF data
                exif_data = {}
                if hasattr(img, '_getexif') and img._getexif():
                    exif = img._getexif()
                    for tag_id, value in exif.items():
                        tag = TAGS.get(tag_id, tag_id)
                        exif_data[tag] = str(value)
                
                metadata["exif"] = exif_data
                
                return metadata
                
        except ImportError:
            return {"error": "Pillow not installed. Install: pip install Pillow"}
        except Exception as e:
            return {"error": str(e)}
    
    def get_video_metadata(self, file_path: str) -> Dict:
        """Get video metadata"""
        try:
            # Try using moviepy
            from moviepy.editor import VideoFileClip
            
            with VideoFileClip(file_path) as clip:
                duration = clip.duration
                fps = clip.fps
                width, height = clip.size
                
                return {
                    "duration": round(duration, 2),
                    "duration_formatted": self._format_duration(duration),
                    "fps": fps,
                    "width": width,
                    "height": height,
                    "resolution": f"{width}x{height}",
                    "size_bytes": Path(file_path).stat().st_size,
                    "bitrate": self._estimate_bitrate(file_path, duration)
                }
                
        except ImportError:
            # Fallback to ffprobe or basic file info
            return self._get_basic_video_info(file_path)
        except Exception as e:
            return {"error": str(e)}
    
    def _get_basic_video_info(self, file_path: str) -> Dict:
        """Get basic video info without moviepy"""
        try:
            import subprocess
            
            result = subprocess.run(
                ['ffprobe', '-v', 'error', '-show_entries',
                 'format=duration,size,bit_rate', '-show_entries',
                 'stream=width,height,r_frame_rate', '-of',
                 'default=noprint_wrappers=1', file_path],
                capture_output=True,
                text=True
            )
            
            # Parse output
            info = {"path": file_path, "size_bytes": Path(file_path).stat().st_size}
            
            for line in result.stdout.strip().split('\n'):
                if '=' in line:
                    key, value = line.split('=', 1)
                    info[key] = value
            
            return info
            
        except:
            return {
                "path": file_path,
                "size_bytes": Path(file_path).stat().st_size,
                "note": "Install moviepy or ffprobe for detailed metadata"
            }
    
    def _format_duration(self, seconds: float) -> str:
        """Format seconds as HH:MM:SS"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        else:
            return f"{minutes:02d}:{secs:02d}"
    
    def _estimate_bitrate(self, file_path: str, duration: float) -> str:
        """Estimate video bitrate"""
        size_bits = Path(file_path).stat().st_size * 8
        bitrate = size_bits / duration if duration > 0 else 0
        
        if bitrate > 1_000_000_000:
            return f"{bitrate / 1_000_000_000:.2f} Gbps"
        elif bitrate > 1_000_000:
            return f"{bitrate / 1_000_000:.2f} Mbps"
        elif bitrate > 1_000:
            return f"{bitrate / 1_000:.2f} Kbps"
        else:
            return f"{bitrate:.2f} bps"
    
    def create_thumbnail(self, file_path: str, size: Tuple[int, int] = (200, 200)) -> str:
        """Create thumbnail for image or video"""
        ext = Path(file_path).suffix.lower()
        
        if ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']:
            return self._create_image_thumbnail(file_path, size)
        elif ext in ['.mp4', '.avi', '.mov', '.mkv', '.webm']:
            return self._create_video_thumbnail(file_path, size)
        else:
            return f"Thumbnail not supported for: {ext}"
    
    def _create_image_thumbnail(self, file_path: str, size: Tuple[int, int]) -> str:
        """Create image thumbnail"""
        try:
            
            output_dir = Path(self.base_path) / "images" / "thumbnails"
            output_dir.mkdir(exist_ok=True)
            
            # Generate output filename
            file_hash = hashlib.md5(file_path.encode()).hexdigest()[:8]
            output_path = output_dir / f"thumb_{file_hash}_{size[0]}x{size[1]}.jpg"
            
            with Image.open(file_path) as img:
                # Convert to RGB if necessary
                if img.mode in ('RGBA', 'LA', 'P'):
                    img = img.convert('RGB')
                
                # Create thumbnail
                img.thumbnail(size, Image.Resampling.LANCZOS)
                img.save(output_path, "JPEG", quality=85)
            
            return str(output_path)
            
        except ImportError:
            return "Pillow not installed"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def _create_video_thumbnail(self, file_path: str, size: Tuple[int, int]) -> str:
        """Create video thumbnail from first frame"""
        try:
            
            output_dir = Path(self.base_path) / "video" / "thumbnails"
            output_dir.mkdir(exist_ok=True)
            
            file_hash = hashlib.md5(file_path.encode()).hexdigest()[:8]
            output_path = output_dir / f"thumb_{file_hash}.jpg"
            
            with VideoFileClip(file_path) as clip:
                # Save frame at 1 second
                frame_time = min(1.0, clip.duration / 2)
                clip.save_frame(str(output_path), t=frame_time)
            
            # Resize thumbnail
            return self._create_image_thumbnail(str(output_path), size)
            
        except ImportError:
            return "moviepy not installed"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def convert_image_format(self, file_path: str, output_format: str, output_path: str) -> str:
        """Convert image to different format"""
        try:
            
            with Image.open(file_path) as img:
                if img.mode in ('RGBA', 'LA') and output_format.upper() == 'JPEG':
                    # Remove transparency for JPEG
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'RGBA':
                        background.paste(img, mask=img.split()[-1])
                    else:
                        background.paste(img)
                    img = background
                
                img.save(output_path, output_format.upper())
            
            return output_path
            
        except ImportError:
            return "Pillow not installed"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def resize_image(self, file_path: str, new_size: Tuple[int, int], output_path: str) -> str:
        """Resize image to new dimensions"""
        try:
            
            with Image.open(file_path) as img:
                resized = img.resize(new_size, Image.Resampling.LANCZOS)
                resized.save(output_path)
            
            return output_path
            
        except ImportError:
            return "Pillow not installed"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def compress_image(self, file_path: str, quality: int = 75, output_path: Optional[str] = None) -> str:
        """Compress image with specified quality"""
        try:
            
            if output_path is None:
                output_path = file_path
            
            with Image.open(file_path) as img:
                if img.mode in ('RGBA', 'LA', 'P'):
                    img = img.convert('RGB')
                
                img.save(output_path, "JPEG", quality=quality, optimize=True)
            
            return output_path
            
        except ImportError:
            return "Pillow not installed"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def extract_audio_from_video(self, video_path: str, output_path: str) -> str:
        """Extract audio track from video"""
        try:
            
            with VideoFileClip(video_path) as clip:
                if clip.audio:
                    clip.audio.write_audiofile(output_path)
                    return output_path
                else:
                    return "No audio track found"
                    
        except ImportError:
            return "moviepy not installed"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def trim_video(self, video_path: str, start: float, end: float, output_path: str) -> str:
        """Trim video to specified time range"""
        try:
            
            with VideoFileClip(video_path) as clip:
                trimmed = clip.subclip(start, end)
                trimmed.write_videofile(output_path, codec='libx264')
            
            return output_path
            
        except ImportError:
            return "moviepy not installed"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def get_audio_metadata(self, file_path: str) -> Dict:
        """Get audio file metadata"""
        try:
            from mutagen.mp3 import MP3
            from mutagen.wave import WAVE
            from mutagen.flac import FLAC
            
            ext = Path(file_path).suffix.lower()
            
            if ext == '.mp3':
                audio = MP3(file_path)
            elif ext == '.wav':
                audio = WAVE(file_path)
            elif ext == '.flac':
                audio = FLAC(file_path)
            else:
                return {"error": f"Format not supported: {ext}"}
            
            return {
                "duration": round(audio.info.length, 2),
                "duration_formatted": self._format_duration(audio.info.length),
                "bitrate": audio.info.bitrate,
                "sample_rate": audio.info.sample_rate,
                "channels": audio.info.channels,
                "size_bytes": Path(file_path).stat().st_size
            }
            
        except ImportError:
            return {"error": "mutagen not installed. Install: pip install mutagen"}
        except Exception as e:
            return {"error": str(e)}
