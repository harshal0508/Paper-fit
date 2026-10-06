import sys, os, unittest
sys.path.append(os.path.join(os.path.dirname(__file__), "../src"))
from common import load, extract_profile

class TestRules(unittest.TestCase):
    def setUp(self):
        self.lex = load("config/lexicon.json")
        
    def test_mesonet_rule(self):
        # Claim: "Video forgery detection using deep learning." -> claims video
        text_claim = "Video forgery detection using deep learning."
        # Demo: "We average the per-frame predictions to get the video score." -> triggers frame_aggregation_phrases
        text_demo = "To evaluate the video, we extract frames and average the per-frame predictions to get the final video score."
        
        prof = extract_profile(text_claim, text_demo, self.lex)
        
        # Should claim video
        self.assertTrue(prof["modality"]["video"]["claimed"])
        
        # But demonstrated should be FORCEABLY False due to the rule
        self.assertFalse(prof["modality"]["video"]["demonstrated"])
        
        # Check that evidence was recorded
        self.assertTrue(len(prof["modality"]["video"]["evidence"]) > 0)
        
    def test_genuine_video_rule(self):
        text_claim = "Video forgery detection using 3D CNNs."
        # Demo without frame averaging phrases
        text_demo = "Our 3D CNN processes the entire video sequence, leveraging temporal convolutions across frames to catch artifacts."
        
        prof = extract_profile(text_claim, text_demo, self.lex)
        self.assertTrue(prof["modality"]["video"]["claimed"])
        self.assertTrue(prof["modality"]["video"]["demonstrated"])

    def test_average_precision_exclusion(self):
        text_claim = "Video forgery detection."
        # Demo has "average precision" which should NOT trigger the frame aggregation rule
        text_demo = "We process the video frames independently. Our model achieves high average precision on the dataset."
        
        prof = extract_profile(text_claim, text_demo, self.lex)
        self.assertTrue(prof["modality"]["video"]["claimed"])
        self.assertTrue(prof["modality"]["video"]["demonstrated"])

if __name__ == "__main__":
    unittest.main()
