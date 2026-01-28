import numpy as np
from logging import getLogger


# logger
logger = getLogger()


def parse_game_features(s):
    """
    Parse the game features we want to detect.
    """
    game_features = ["target", "enemy", "health", "weapon", "ammo"]
    split = list(filter(None, s.split(",")))
    assert all(x in game_features for x in split)
    return [x in split for x in game_features]


class GameFeaturesConfusionMatrix:
    """
    A class for storing confusion matrix of game feature predictions.
    Used for model evaluation.
    """

    def __init__(self, map_ids, n_features):
        """
        Store game features predictions results.
        We store results separatly for all maps.
        """
        assert type(map_ids) is list and len(map_ids) > 0 and n_features > 0
        self.id_to_map = sorted(map_ids)
        self.map_to_id = {m: i for i, m in enumerate(self.id_to_map)}
        self.n_features = n_features
        self.pred_tp = np.zeros((len(map_ids), n_features)).astype(np.int32)
        self.pred_tn = np.zeros((len(map_ids), n_features)).astype(np.int32)
        self.pred_fp = np.zeros((len(map_ids), n_features)).astype(np.int32)
        self.pred_fn = np.zeros((len(map_ids), n_features)).astype(np.int32)

    def update_predictions(self, pred, gold, map_id):
        """
        Update game feature predictions made by the model.
        `map_id` corresponds to the map where the prediction is made.
        `pred` are predicted features
        `gold` are true game features (targets)
        """
        assert len(pred) == self.n_features
        j = self.map_to_id[map_id]
        for i in range(self.n_features):
            if pred[i] > 0.5:
                if gold[i]:
                    self.pred_tp[j, i] += 1
                else:
                    self.pred_fp[j, i] += 1
            else:
                if gold[i]:
                    self.pred_fn[j, i] += 1
                else:
                    self.pred_tn[j, i] += 1

    def print_statistics(self):
        """
        Print statistics about the game feature predictions.
        If there is more than one map, we also show a summary for all map.
        """
        count = self.pred_tp + self.pred_tn + self.pred_fp + self.pred_fn
        assert len(set(count.ravel())) == 1
        logger.info("*************** Game features summary ***************")

        # Print statistics for each map
        for j, m in enumerate(self.id_to_map):
            # Use f-string for map label
            logger.info(f"Map{m:02d}")
            for i in range(self.n_features):
                pre = (
                    self.pred_tp[j, i]
                    * 1.0
                    / max(self.pred_tp[j, i] + self.pred_fp[j, i], 1)
                )
                rec = (
                    self.pred_tp[j, i]
                    * 1.0
                    / max(self.pred_tp[j, i] + self.pred_fn[j, i], 1)
                )
                f1 = pre * rec / max(pre + rec, 1)
                # Convert to f-string for readability
                logger.info(
                    f"{i} ||| P: {self.pred_tp[j, i] + self.pred_fn[j, i]:6d} ||| "
                    f"TP: {self.pred_tp[j, i]:6d} - FP: {self.pred_fp[j, i]:6d} - "
                    f"FN: {self.pred_fn[j, i]:6d} - TN: {self.pred_tn[j, i]:6d} ||| "
                    f"Pre: {100.0 * pre:3.5f} - Rec: {100.0 * rec:3.5f} - F: {200.0 * f1:3.5f}"
                )

        # Print statistics for all maps
        # If there is just one map, this is not necessary
        if len(self.id_to_map) == 1:
            return
        logger.info("All maps")
        for i in range(self.n_features):
            pre = (
                self.pred_tp[:, i].sum()
                * 1.0
                / max(self.pred_tp[:, i].sum() + self.pred_fp[:, i].sum(), 1)
            )
            rec = (
                self.pred_tp[:, i].sum()
                * 1.0
                / max(self.pred_tp[:, i].sum() + self.pred_fn[:, i].sum(), 1)
            )
            f1 = pre * rec / max(pre + rec, 1)
            # Convert to f-string for readability
            logger.info(
                f"{i} ||| P: {self.pred_tp[:, i].sum() + self.pred_fn[:, i].sum():6d} ||| "
                f"TP: {self.pred_tp[:, i].sum():6d} - FP: {self.pred_fp[:, i].sum():6d} - "
                f"FN: {self.pred_fn[:, i].sum():6d} - TN: {self.pred_tn[:, i].sum():6d} ||| "
                f"Pre: {100.0 * pre:3.5f} - Rec: {100.0 * rec:3.5f} - F: {200.0 * f1:3.5f}"
            )
