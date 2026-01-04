# ============================================================
#  Dataset Factory
# ============================================================

class DatasetFactory:
    """
    Factory for generating different training and test datasets.
    Modes:
        - "small"   : linear, limited range (4–7)
        - "large"   : linear, full range (3–9)
        - "circle"  : non-linear, perceptron fails
    """

    @staticmethod
    def get(mode):
        if mode == "small":
            return DatasetFactory._small_dataset(), DatasetFactory._linear_test()
        elif mode == "large":
            return DatasetFactory._large_dataset(), DatasetFactory._linear_test()
        elif mode == "circle":
            # For the circle dataset, test = train (perceptron fails already here)
            train = DatasetFactory._circle_dataset()
            return train, train
        else:
            raise ValueError(f"Unknown dataset mode: {mode}")

    # --------------------------------------------------------
    # Internal dataset generators
    # --------------------------------------------------------

    @staticmethod
    def _small_dataset():
        features = [
            (4, 4), (4, 5), (4, 6), (4, 7),
            (5, 4), (5, 5), (5, 6), (5, 7),
            (6, 4), (6, 5), (6, 6), (6, 7),
            (7, 4), (7, 5), (7, 6), (7, 7)
        ]
        labels = [
            0,1,1,1,
            0,0,1,1,
            0,0,0,1,
            0,0,0,0
        ]
        return features, labels

    @staticmethod
    def _large_dataset():
        features = [
            (x1, x2)
            for x1 in range(3, 10)
            for x2 in range(3, 10)
        ]
        labels = [
        0,1,1,1,1,1,1,   # Zeile x1=3
        0,0,1,1,1,1,1,   # Zeile x1=4
        0,0,0,1,1,1,1,   # Zeile x1=5
        0,0,0,0,1,1,1,   # Zeile x1=6
        0,0,0,0,0,1,1,   # Zeile x1=7
        0,0,0,0,0,0,1,   # Zeile x1=8
        0,0,0,0,0,0,0    # Zeile x1=9
        ]
        return features, labels

    @staticmethod
    def _linear_test():
        features = [
            (10, 10), (10, 11), (10, 12),
            (11, 10), (11, 11), (11, 12),
            (12, 10), (12, 11), (12, 12)
        ]
        labels = [
            0, 1, 1,
            0, 0, 1,
            0, 0, 0
        ]
        return features, labels

    @staticmethod
    def _circle_dataset():
        features = [
            (x1, x2)
            for x1 in range(1, 10)
            for x2 in range(1, 10)
        ]

        # 7×7 circle mask (centered)
        circle_labels = [
            0,0,0,0,0,0,0,0,0,
            0,0,0,1,1,1,0,0,0,
            0,0,1,1,1,1,1,0,0,
            0,1,1,1,1,1,1,1,0,
            0,1,1,1,1,1,1,1,0,
            0,1,1,1,1,1,1,1,0,
            0,0,1,1,1,1,1,0,0,
            0,0,0,1,1,1,0,0,0,
            0,0,0,0,0,0,0,0,0
        ]
        return features, circle_labels

