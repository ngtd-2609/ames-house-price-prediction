"""Fast smoke checks on data, end-to-end artifact and backend."""
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
for p in (ROOT,ROOT/'src'):
    if str(p) not in sys.path: sys.path.insert(0,str(p))
from tests.test_data import test_supplied_splits_have_expected_shape_and_unique_ids,test_na_none_tokens_are_preserved_as_categories
from tests.test_features import test_feature_engineering_is_row_preserving_target_free_and_complete
from tests.test_prediction import test_saved_pipeline_predicts_positive_finite_prices,test_fixed_predictions_match_canonical_summary_tolerance
from tests.test_backend import test_batch_preserves_row_count_and_id_and_adds_prediction
CHECKS=[test_supplied_splits_have_expected_shape_and_unique_ids,test_na_none_tokens_are_preserved_as_categories,test_feature_engineering_is_row_preserving_target_free_and_complete,test_saved_pipeline_predicts_positive_finite_prices,test_fixed_predictions_match_canonical_summary_tolerance,test_batch_preserves_row_count_and_id_and_adds_prediction]
for f in CHECKS: f(); print('PASS',f.__module__+'.'+f.__name__)
print('ALL_SMOKE_TESTS_PASSED')
