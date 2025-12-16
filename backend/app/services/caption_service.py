"""
Caption Service - AI Caption Generation for Videos using UniVL

Unified service handling both UniVL model loading and caption generation.
"""

import os
import sys
import random
import torch
import numpy as np
import tempfile
from pathlib import Path
from typing import Optional

# Add UniVL to path
UNIVL_PATH = Path(__file__).resolve().parents[3] / "UniVL"
VIDEO_EXTRACTOR_PATH = UNIVL_PATH / "VideoFeatureExtractor"
if str(VIDEO_EXTRACTOR_PATH) not in sys.path:
    sys.path.insert(0, str(VIDEO_EXTRACTOR_PATH))
if str(UNIVL_PATH) not in sys.path:
    sys.path.insert(0, str(UNIVL_PATH))

# Global variables for lazy loading
_model = None
_tokenizer = None
_s3d_model = None
_initialized = False


class CaptionService:
    """
    Service for generating captions from videos using AI.

    Implementation modes:
    1. REAL: UniVL model (if available)
    2. MOCK: Random captions (fallback)
    """

    # Mock captions pool for testing/fallback
    MOCK_CAPTIONS = [
        "A person is explaining web accessibility standards in a well-lit room with clear audio.",
        "The instructor demonstrates ARIA attributes using code examples displayed on screen.",
        "Tutorial showing keyboard navigation techniques for screen readers and assistive technologies.",
        "Video demonstration of WCAG 2.1 compliance testing tools and accessibility evaluation methods.",
        "Speaker discusses the importance of semantic HTML for screen reader compatibility.",
        "Presentation covering color contrast requirements and visual accessibility guidelines.",
        "Developer walking through accessible form design with proper label associations.",
        "Tutorial on implementing skip navigation links and landmark regions for better accessibility.",
        "Demonstration of how to test websites using popular screen reader software like NVDA and JAWS.",
        "Expert explaining the differences between WCAG levels A, AA, and AAA conformance.",
    ]

    def __init__(self, use_real_model: bool = True):
        """
        Initialize the caption service.
        
        Args:
            use_real_model: If True, use UniVL. If False, use MOCK.
        """
        self.model_loaded = False
        self.use_real_model = use_real_model
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.max_frames = 48
        self.max_words = 48
        self.beam_size = 5
        
        # Paths
        self.checkpoint_path = str(UNIVL_PATH / "weight" / "best_checkpoint.bin")
        self.s3d_weights_path = str(UNIVL_PATH / "VideoFeatureExtractor" / "model" / "s3d_howto100m.pth")
        self.bert_model_path = str(UNIVL_PATH / "modules" / "bert-base-uncased")
        
        if use_real_model:
            print(f"[CaptionService] Initialized with REAL UniVL (device: {self.device})")
        else:
            print("[CaptionService] Initialized with MOCK implementation")

    def _load_models(self):
        """Load UniVL and S3D models (lazy loading, chỉ load 1 lần)."""
        global _model, _tokenizer, _s3d_model, _initialized
        
        if _initialized:
            return
        
        print("[CaptionService] Loading AI models...")
        
        from modules.tokenization import BertTokenizer  # type: ignore
        from modules.modeling import UniVL  # type: ignore
        from modules.file_utils import PYTORCH_PRETRAINED_BERT_CACHE  # type: ignore
        from VideoFeatureExtractor.videocnn.models import s3dg  # type: ignore
        from VideoFeatureExtractor.model import init_weight  # type: ignore
        import argparse
        
        # Load tokenizer
        print("  Loading tokenizer...")
        _tokenizer = BertTokenizer.from_pretrained(self.bert_model_path, do_lower_case=True)
        
        # Prepare model args
        parser = argparse.ArgumentParser()
        parser.add_argument("--bert_model", default="bert-base-uncased", type=str)
        parser.add_argument("--visual_model", default="visual-base", type=str)
        parser.add_argument("--cross_model", default="cross-base", type=str)
        parser.add_argument("--decoder_model", default="decoder-base", type=str)
        parser.add_argument("--do_lower_case", action='store_true', default=True)
        parser.add_argument("--cache_dir", default="", type=str)
        parser.add_argument('--max_words', type=int, default=48)
        parser.add_argument('--max_frames', type=int, default=48)
        parser.add_argument('--video_dim', type=int, default=1024)
        parser.add_argument('--text_num_hidden_layers', type=int, default=12)
        parser.add_argument('--visual_num_hidden_layers', type=int, default=6)
        parser.add_argument('--cross_num_hidden_layers', type=int, default=2)
        parser.add_argument('--decoder_num_hidden_layers', type=int, default=3)
        parser.add_argument('--stage_two', action='store_true', default=True)
        parser.add_argument('--task_type', type=str, default='caption')
        parser.add_argument("--do_pretrain", action='store_true', default=False)
        parser.add_argument("--do_train", action='store_true', default=False)
        parser.add_argument("--do_eval", action='store_true', default=False)
        parser.add_argument('--batch_size', type=int, default=32)
        parser.add_argument('--n_gpu', type=int, default=1)
        parser.add_argument('--n_pair', type=int, default=1)
        parser.add_argument('--margin', type=float, default=0.1)
        parser.add_argument('--negative_weighting', type=int, default=1)
        parser.add_argument('--hard_negative_rate', type=float, default=0.5)
        parser.add_argument('--use_mil', action='store_true', default=False)
        parser.add_argument('--sampled_use_mil', action='store_true', default=False)
        parser.add_argument('--local_rank', type=int, default=0)
        parser.add_argument('--world_size', type=int, default=1)
        args = parser.parse_args([])
        
        # Load UniVL model
        print(f"  Loading UniVL model from: {self.checkpoint_path}")
        if not os.path.exists(self.checkpoint_path):
            raise FileNotFoundError(f"Checkpoint not found: {self.checkpoint_path}")
        
        model_state_dict = torch.load(self.checkpoint_path, map_location='cpu')
        cache_dir = os.path.join(str(PYTORCH_PRETRAINED_BERT_CACHE), 'distributed')
        
        _model = UniVL.from_pretrained(
            args.bert_model, args.visual_model, args.cross_model, args.decoder_model,
            cache_dir=cache_dir, state_dict=model_state_dict, task_config=args
        )
        _model.to(self.device)
        _model.eval()
        
        # Load S3D model
        print(f"  Loading S3D model from: {self.s3d_weights_path}")
        if not os.path.exists(self.s3d_weights_path):
            raise FileNotFoundError(f"S3D weights not found: {self.s3d_weights_path}")
        
        _s3d_model = s3dg.S3D(last_fc=False)
        _s3d_model = _s3d_model.to(self.device)
        s3d_dict = torch.load(self.s3d_weights_path, map_location='cpu')
        _s3d_model = init_weight(_s3d_model, s3d_dict)
        _s3d_model.eval()
        
        _initialized = True
        self.model_loaded = True
        print("[CaptionService] ✓ Models loaded successfully!")
    
    def _extract_s3d_features(self, video_path: str) -> np.ndarray:
        """Extract S3D features từ video (1 feature per second)."""
        from VideoFeatureExtractor.video_loader import VideoLoader  # type: ignore
        import pandas as pd
        import torch.nn.functional as F
        import ffmpeg
        
        print(f"  Extracting S3D features from: {os.path.basename(video_path)}")
        
        probe = ffmpeg.probe(video_path)
        video_stream = next((s for s in probe['streams'] if s['codec_type'] == 'video'), None)
        
        duration = float(video_stream.get('duration', probe['format']['duration']))
        num_seconds = int(duration)
        print(f"    Video duration: {duration:.2f}s → {num_seconds} features")
        
        # Create temp CSV for VideoLoader
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
            temp_csv = f.name
            df = pd.DataFrame({'video_path': [video_path], 'feature_path': ['dummy.npy']})
            df.to_csv(temp_csv, index=False)
        
        try:
            SIZE, FPS = 224, 16
            dataset = VideoLoader(temp_csv, framerate=FPS, size=SIZE, centercrop=True)
            data = dataset[0]
            video = data['video']  # [T, C, H, W]
            
            if video.shape[0] <= 1:
                raise ValueError(f"Failed to decode video: {video_path}")
            
            num_decoded_frames = len(video)
            print(f"    Loaded {num_decoded_frames} frames (fps={FPS})")
            
            video = video / 255.0
            features_list = []
            
            with torch.no_grad():
                for i in range(num_seconds):
                    start_frame, end_frame = i * 16, (i + 1) * 16
                    
                    if end_frame <= num_decoded_frames:
                        clip = video[start_frame:end_frame]
                    else:
                        clip = video[start_frame:]
                        padding_needed = 16 - len(clip)
                        padding = torch.zeros(padding_needed, clip.shape[1], clip.shape[2], clip.shape[3])
                        clip = torch.cat([clip, padding], dim=0)
                    
                    clip = clip.permute(1, 0, 2, 3).unsqueeze(0).to(self.device)
                    feature = _s3d_model(clip)
                    feature = F.normalize(feature, dim=1)
                    features_list.append(feature.cpu())
            
            features = torch.cat(features_list, dim=0).numpy()
            print(f"    ✓ Features extracted: {features.shape}")
            return features
        finally:
            if os.path.exists(temp_csv):
                os.unlink(temp_csv)
    
    def _generate_caption_from_features(self, video_features: np.ndarray) -> str:
        """Generate caption từ features using beam search."""
        from modules.beam import Beam  # type: ignore
        
        print("  Generating caption with beam search...")
        
        num_frames = video_features.shape[0]
        if num_frames > self.max_frames:
            video_features = video_features[:self.max_frames]
            num_frames = self.max_frames
        else:
            padding = np.zeros((self.max_frames - num_frames, 1024), dtype=np.float32)
            video_features = np.concatenate([video_features, padding], axis=0)
        
        video_mask = np.zeros(self.max_frames, dtype=np.int64)
        video_mask[:num_frames] = 1
        
        video = torch.from_numpy(video_features).unsqueeze(0).float().to(self.device)
        video_mask = torch.from_numpy(video_mask).unsqueeze(0).long().to(self.device)
        
        input_ids = torch.zeros(1, 1, dtype=torch.long).to(self.device)
        input_ids[0, 0] = _tokenizer.vocab["[CLS]"]
        input_mask = torch.ones(1, 1, dtype=torch.long).to(self.device)
        segment_ids = torch.zeros(1, 1, dtype=torch.long).to(self.device)
        
        with torch.no_grad():
            sequence_output, visual_output = _model.get_sequence_visual_output(
                input_ids, segment_ids, input_mask, video, video_mask
            )
            
            n_bm = self.beam_size
            n_inst, len_s, d_h = sequence_output.size()
            _, len_v, v_h = visual_output.size()
            
            decoder = _model.decoder_caption
            
            input_ids = input_ids.view(-1, input_ids.shape[-1])
            input_mask = input_mask.view(-1, input_mask.shape[-1])
            video_mask = video_mask.view(-1, video_mask.shape[-1])
            
            sequence_output_rpt = sequence_output.repeat(1, n_bm, 1).view(n_inst * n_bm, len_s, d_h)
            visual_output_rpt = visual_output.repeat(1, n_bm, 1).view(n_inst * n_bm, len_v, v_h)
            input_ids_rpt = input_ids.repeat(1, n_bm).view(n_inst * n_bm, len_s)
            input_mask_rpt = input_mask.repeat(1, n_bm).view(n_inst * n_bm, len_s)
            video_mask_rpt = video_mask.repeat(1, n_bm).view(n_inst * n_bm, len_v)
            
            inst_dec_beams = [Beam(n_bm, device=self.device, tokenizer=_tokenizer) for _ in range(n_inst)]
            active_inst_idx_list = list(range(n_inst))
            inst_idx_to_position_map = {idx: pos for pos, idx in enumerate(active_inst_idx_list)}
            
            # Beam search decode
            for len_dec_seq in range(1, self.max_words + 1):
                dec_partial_seq = [b.get_current_state() for b in inst_dec_beams if not b.done]
                if not dec_partial_seq:
                    break
                dec_partial_seq = torch.stack(dec_partial_seq).to(self.device).view(-1, len_dec_seq)
                next_decoder_mask = torch.ones(dec_partial_seq.size(), dtype=torch.uint8).to(self.device)
                
                dec_output = decoder(sequence_output_rpt, visual_output_rpt, input_ids_rpt, input_mask_rpt,
                                     video_mask_rpt, dec_partial_seq, next_decoder_mask, shaped=True, get_logits=True)
                dec_output = dec_output[:, -1, :]
                word_prob = torch.nn.functional.log_softmax(dec_output, dim=1)
                word_prob = word_prob.view(len(inst_idx_to_position_map), n_bm, -1)
                
                active_inst_idx_list = []
                for inst_idx, inst_position in inst_idx_to_position_map.items():
                    if not inst_dec_beams[inst_idx].advance(word_prob[inst_position]):
                        active_inst_idx_list.append(inst_idx)
                
                if not active_inst_idx_list:
                    break
                inst_idx_to_position_map = {idx: pos for pos, idx in enumerate(active_inst_idx_list)}
            
            # Collect best hypothesis
            all_hyp = []
            for inst_idx in range(n_inst):
                scores, tail_idxs = inst_dec_beams[inst_idx].sort_scores()
                all_hyp.append([inst_dec_beams[inst_idx].get_hypothesis(i) for i in tail_idxs[:1]])
            
            result_list = [all_hyp[i][0] for i in range(n_inst)]
            
            for re_list in result_list:
                decode_text_list = _tokenizer.convert_ids_to_tokens(re_list)
                if "[SEP]" in decode_text_list:
                    decode_text_list = decode_text_list[:decode_text_list.index("[SEP]")]
                if "[PAD]" in decode_text_list:
                    decode_text_list = decode_text_list[:decode_text_list.index("[PAD]")]
                decode_text = ' '.join(decode_text_list).replace(" ##", "").strip("##").strip()
                
                print(f"  ✓ Caption generated: {decode_text}")
                return decode_text
    
    def generate_caption(self, video_path: str) -> str:
        """
        Generate caption for video (end-to-end pipeline).

        Args:
            video_path: Path to the video file

        Returns:
            Generated caption text
        """
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")

        print(f"[CaptionService] Generating caption for: {os.path.basename(video_path)}")

        # REAL model
        if self.use_real_model:
            if not self.model_loaded:
                self._load_models()
            
            features = self._extract_s3d_features(video_path)
            caption = self._generate_caption_from_features(features)
            print(f"[CaptionService] ✓ REAL caption: {caption[:50]}...")
            return caption
        
        # MOCK fallback
        caption = random.choice(CaptionService.MOCK_CAPTIONS)
        print(f"[CaptionService] MOCK caption: {caption[:50]}...")
        return caption

    def extract_video_frame(
        self, video_path: str, frame_position: float = 0.5
    ) -> Optional[str]:
        """
        Extract a frame from video for caption generation.

        Args:
            video_path: Path to the video file
            frame_position: Position to extract (0.0 to 1.0, where 0.5 is middle)

        Returns:
            Path to extracted frame image, or None if failed

        Note:
            Currently not used by UniVL (uses S3D features instead).
        """
        print(
            f"[CaptionService] Would extract frame at position {frame_position}"
        )
        return None

    def load_model(self):
        """
        Load the AI model for caption generation.
        
        For UniVL, models are lazy-loaded on first use.
        """
        if self.use_real_model:
            print("[CaptionService] Model will be loaded on first use (lazy loading)")
        else:
            print("[CaptionService] MOCK: No model to load")
        self.model_loaded = True

    def unload_model(self):
        """
        Unload the AI model to free memory.
        
        Note: UniVL models stay in memory for performance.
        """
        print("[CaptionService] Model unload not implemented (models cached for performance)")
        self.model_loaded = False


# Singleton instance for reuse
_caption_service_instance: Optional[CaptionService] = None


def get_caption_service(use_real_model: bool = True) -> CaptionService:
    """
    Get or create the caption service singleton.

    Args:
        use_real_model: If True, use UniVL. If False, use MOCK.

    Returns:
        CaptionService instance
    """
    global _caption_service_instance
    if _caption_service_instance is None:
        # Check environment variable for override
        use_mock = os.getenv("USE_MOCK_CAPTION", "false").lower() == "true"
        _caption_service_instance = CaptionService(use_real_model=not use_mock and use_real_model)
    return _caption_service_instance
