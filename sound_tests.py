import unittest
from sound import Sound
from sound_effects import SoundEffects


class TestSoundEditor(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sound = Sound("tests/SodaPop.mp3")

    def setUp(self):
        self.effects = SoundEffects(self.sound)
        self.effects.return_to_original()

    def test_change_volume(self):
        original = self.sound.frames[0][:10]
        self.effects.change_volume(0.5)
        updated = self.sound.frames[0][:10]
        for o, u in zip(original, updated):
            self.assertAlmostEqual(u, o * 0.5, delta=1e-6)

    def test_change_speed(self):
        original_len = len(self.sound.frames[0])
        self.effects.change_speed(2)
        new_len = len(self.sound.frames[0])
        self.assertAlmostEqual(new_len, original_len / 2, delta=10)

    def test_cut_fragment(self):
        original_len = len(self.sound.frames[0])
        self.effects.cut_fragment(1, 2)
        new_len = len(self.sound.frames[0])
        self.assertLess(new_len, original_len)

    # def test_trim(self): не придумала, как проверять

    def test_concat(self):
        original_len = len(self.sound.frames[0])
        self.effects.concat(Sound("tests/SodaPop.mp3"))
        new_len = len(self.sound.frames[0])
        self.assertGreater(new_len, original_len)


if __name__ == "__main__":
    unittest.main()
