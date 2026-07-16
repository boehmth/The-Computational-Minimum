# ============================================================
#  Letter Dataset Factory (9x9 bitmaps)
# ============================================================

class LetterDatasetFactory:
    """
    Provides 9x9 bitmap data for letters A, L, R.
    Returns:
        data:   list of flattened 81-element pixel vectors
        labels: list of one-hot encoded target vectors
        index_to_letter: mapping from output index to letter
    """

    @staticmethod
    def get_letters():
        bitmaps = {
            "A": [
                0,0,0,0,0,0,0,0,0,
                0,0,0,1,1,1,0,0,0,
                0,0,1,1,1,1,1,0,0,
                0,1,1,0,0,0,1,1,0,
                0,1,1,0,0,0,1,1,0,
                0,1,1,1,1,1,1,1,0,
                0,1,1,1,1,1,1,1,0,
                0,1,1,0,0,0,1,1,0,
                0,0,0,0,0,0,0,0,0
            ],
            "L": [
                0,0,0,0,0,0,0,0,0,
                0,1,1,0,0,0,0,0,0,
                0,1,1,0,0,0,0,0,0,
                0,1,1,0,0,0,0,0,0,
                0,1,1,0,0,0,0,0,0,
                0,1,1,0,0,0,1,1,0,
                0,1,1,1,1,1,1,1,0,
                0,1,1,1,1,1,1,1,0,
                0,0,0,0,0,0,0,0,0
            ],
            "R": [
                0,0,0,0,0,0,0,0,0,
                0,1,1,1,1,1,0,0,0,
                0,1,1,0,0,1,1,0,0,
                0,1,1,0,0,1,1,0,0,
                0,1,1,1,1,1,0,0,0,
                0,1,1,0,1,1,0,0,0,
                0,1,1,0,0,1,1,0,0,
                0,1,1,0,0,0,1,1,0,
                0,0,0,0,0,0,0,0,0
            ]
        }

        letters = ["A", "L", "R"]
        data = [bitmaps[ch] for ch in letters]

        # one-hot encoding: A=0, L=1, R=2
        labels = []
        for i in range(len(letters)):
            vec = [0]*len(letters)
            vec[i] = 1
            labels.append(vec)

        return data, labels, letters
