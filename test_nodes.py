import unittest
import torch
from nodes import create_guidance_scales

class TestFDGNode(unittest.TestCase):

    def test_create_guidance_scales_linear(self):
        scales = create_guidance_scales(10.0, 1.0, 4, "linear")
        self.assertEqual(len(scales), 4)
        self.assertAlmostEqual(scales[0], 10.0)
        self.assertAlmostEqual(scales[-1], 1.0)
        self.assertTrue(torch.allclose(torch.tensor(scales), torch.linspace(10.0, 1.0, 4)))

    def test_create_guidance_scales_cosine(self):
        scales = create_guidance_scales(10.0, 1.0, 4, "cosine")
        self.assertEqual(len(scales), 4)
        self.assertAlmostEqual(scales[0], 10.0)
        self.assertAlmostEqual(scales[-1], 1.0)

    def test_create_guidance_scales_single_level(self):
        scales = create_guidance_scales(10.0, 1.0, 1)
        self.assertEqual(scales, [10.0])

    def test_create_guidance_scales_invalid_method(self):
        with self.assertRaises(ValueError):
            create_guidance_scales(10.0, 1.0, 4, "invalid")

if __name__ == '__main__':
    unittest.main()
