"""
Script to compute the Threshold Optimization Curve and 5-Fold Grouped Cross-Validation
for Agentry (TabPFN-3.5 vs Baselines).
"""

import sys
import time
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.model_selection import GroupKFold, GroupShuffleSplit
from sklearn.metrics import (
    balanced_accuracy_score,
    f1_score,
    roc_auc_score,
    recall_score,
    mean_absolute_error,
    r2_score,
)

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from agentry.telemetry import load_telemetry_data
from agentry.engine import TabPFNGuardrailEngine
from agentry.benchmark import HeuristicRuleBaseline, HeuristicCostRegressor
import xgboost as xgb
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.linear_model import LogisticRegression, Ridge


def compute_threshold_curve(df: pd.DataFrame):
    """
    Computes Failure Recall vs False-Stop Rate across various risk thresholds [0.30 .. 0.90]
    on unseen test sessions.
    """
    engine = TabPFNGuardrailEngine()
    processed_df = engine._extract_tabular_features(df, fit=True)
    engine.mode_encoder.fit(df["failure_status"].astype(str))

    feature_cols = engine.FEATURE_COLS
    X = processed_df[feature_cols].copy()
    y_class = engine.mode_encoder.transform(df["failure_status"].astype(str))
    groups = df["session_id"]

    class_list = list(engine.mode_encoder.classes_)
    normal_idx = class_list.index("NORMAL")

    # Group split
    gss = GroupShuffleSplit(n_splits=1, test_size=0.30, random_state=42)
    train_idx, test_idx = next(gss.split(X, y_class, groups=groups))

    X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
    y_train_cls, y_test_cls = y_class[train_idx], y_class[test_idx]

    train_slice = df.iloc[train_idx]
    engine.fit(train_slice)

    # Predict probabilities
    if engine.is_cloud_tabpfn:
        X_test_input = df.iloc[test_idx][engine.RAW_TABPFN_COLS]
    else:
        X_test_input = X_test
    probs = engine.classifier.predict_proba(X_test_input)
    # Prob of ANY failure = 1.0 - prob(NORMAL)
    failure_probs = 1.0 - probs[:, normal_idx]

    is_normal_gt = (y_test_cls == normal_idx)
    is_failure_gt = (y_test_cls != normal_idx)
    total_normals = np.sum(is_normal_gt)
    total_failures = np.sum(is_failure_gt)

    thresholds = [0.30, 0.40, 0.50, 0.60, 0.70, 0.75, 0.80, 0.85, 0.90]
    curve = []

    for t in thresholds:
        is_halt_pred = (failure_probs >= t)
        false_stops = np.sum(is_normal_gt & is_halt_pred)
        caught_failures = np.sum(is_failure_gt & is_halt_pred)

        fpr = false_stops / max(1, total_normals)
        recall = caught_failures / max(1, total_failures)

        curve.append({
            "threshold": t,
            "failure_recall": recall,
            "false_stop_rate": fpr,
            "false_stops_count": int(false_stops),
            "caught_failures_count": int(caught_failures),
            "total_normals": int(total_normals),
            "total_failures": int(total_failures)
        })

    return curve


def compute_5fold_grouped_cv(df: pd.DataFrame):
    """
    Computes 5-Fold Grouped Cross Validation across unique sessions.
    Reports Mean ± Std for TabPFN, XGBoost, Random Forest, and Rule Baseline.
    """
    engine = TabPFNGuardrailEngine()
    processed_df = engine._extract_tabular_features(df, fit=True)
    engine.mode_encoder.fit(df["failure_status"].astype(str))

    feature_cols = engine.FEATURE_COLS
    X = processed_df[feature_cols].copy()
    y_class = engine.mode_encoder.transform(df["failure_status"].astype(str))
    y_reg = df["final_cost_usd"].values
    groups = df["session_id"]

    class_list = list(engine.mode_encoder.classes_)
    normal_idx = class_list.index("NORMAL")
    loop_idx = class_list.index("INFINITE_LOOP")
    cost_idx = class_list.index("COST_RUNAWAY")

    gkf = GroupKFold(n_splits=5)
    
    models = {
        "Rule Baseline": {"recalls": [], "fprs": [], "r2s": [], "maes": []},
        "Random Forest": {"recalls": [], "fprs": [], "r2s": [], "maes": []},
        "XGBoost": {"recalls": [], "fprs": [], "r2s": [], "maes": []},
        "TabPFN-3.5 Engine": {"recalls": [], "fprs": [], "r2s": [], "maes": []}
    }

    for fold, (train_idx, test_idx) in enumerate(gkf.split(X, y_class, groups=groups)):
        X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
        y_train_cls, y_test_cls = y_class[train_idx], y_class[test_idx]
        y_train_reg, y_test_reg = y_reg[train_idx], y_reg[test_idx]

        is_normal_gt = (y_test_cls == normal_idx)
        is_failure_gt = (y_test_cls != normal_idx)
        total_normals = max(1, np.sum(is_normal_gt))
        total_failures = max(1, np.sum(is_failure_gt))

        # 1. Rule Baseline
        rule_cls = HeuristicRuleBaseline(normal_idx, loop_idx, cost_idx)
        rule_preds = rule_cls.predict(X_test)
        rule_halt = (rule_preds != normal_idx)
        models["Rule Baseline"]["recalls"].append(np.sum(is_failure_gt & rule_halt) / total_failures)
        models["Rule Baseline"]["fprs"].append(np.sum(is_normal_gt & rule_halt) / total_normals)
        rule_reg_preds = HeuristicCostRegressor().predict(X_test)
        models["Rule Baseline"]["maes"].append(mean_absolute_error(y_test_reg, rule_reg_preds))
        models["Rule Baseline"]["r2s"].append(r2_score(y_test_reg, rule_reg_preds))

        # 2. Random Forest
        rf_cls = RandomForestClassifier(n_estimators=50, max_depth=6, random_state=42)
        rf_reg = RandomForestRegressor(n_estimators=50, max_depth=6, random_state=42)
        rf_cls.fit(X_train, y_train_cls)
        rf_reg.fit(X_train, y_train_reg)
        rf_preds = rf_cls.predict(X_test)
        rf_halt = (rf_preds != normal_idx)
        models["Random Forest"]["recalls"].append(np.sum(is_failure_gt & rf_halt) / total_failures)
        models["Random Forest"]["fprs"].append(np.sum(is_normal_gt & rf_halt) / total_normals)
        rf_reg_preds = rf_reg.predict(X_test)
        models["Random Forest"]["maes"].append(mean_absolute_error(y_test_reg, rf_reg_preds))
        models["Random Forest"]["r2s"].append(r2_score(y_test_reg, rf_reg_preds))

        # 3. XGBoost
        xgb_cls = xgb.XGBClassifier(n_estimators=50, max_depth=5, learning_rate=0.1, random_state=42, eval_metric="mlogloss")
        xgb_reg = xgb.XGBRegressor(n_estimators=50, max_depth=5, learning_rate=0.1, random_state=42)
        xgb_cls.fit(X_train, y_train_cls)
        xgb_reg.fit(X_train, y_train_reg)
        xgb_preds = xgb_cls.predict(X_test)
        xgb_halt = (xgb_preds != normal_idx)
        models["XGBoost"]["recalls"].append(np.sum(is_failure_gt & xgb_halt) / total_failures)
        models["XGBoost"]["fprs"].append(np.sum(is_normal_gt & xgb_halt) / total_normals)
        xgb_reg_preds = xgb_reg.predict(X_test)
        models["XGBoost"]["maes"].append(mean_absolute_error(y_test_reg, xgb_reg_preds))
        models["XGBoost"]["r2s"].append(r2_score(y_test_reg, xgb_reg_preds))

        # 4. TabPFN Engine
        fold_engine = TabPFNGuardrailEngine()
        fold_engine.fit(df.iloc[train_idx])
        if fold_engine.is_cloud_tabpfn:
            X_test_input = df.iloc[test_idx][fold_engine.RAW_TABPFN_COLS]
        else:
            X_test_input = X_test
        tab_preds = np.argmax(fold_engine.classifier.predict_proba(X_test_input), axis=1)
        tab_halt = (tab_preds != normal_idx)
        models["TabPFN-3.5 Engine"]["recalls"].append(np.sum(is_failure_gt & tab_halt) / total_failures)
        models["TabPFN-3.5 Engine"]["fprs"].append(np.sum(is_normal_gt & tab_halt) / total_normals)
        tab_reg_preds = fold_engine.regressor.predict(X_test_input)
        models["TabPFN-3.5 Engine"]["maes"].append(mean_absolute_error(y_test_reg, tab_reg_preds))
        models["TabPFN-3.5 Engine"]["r2s"].append(r2_score(y_test_reg, tab_reg_preds))

    return models


if __name__ == "__main__":
    df = load_telemetry_data()
    print(f"Total steps: {len(df)}, unique sessions: {df['session_id'].nunique()}")

    print("\n=== 1. THRESHOLD OPTIMIZATION CURVE (P(failure) >= theta) ===")
    curve = compute_threshold_curve(df)
    print(f"{'Threshold':<12} | {'Failure Recall':<15} | {'False Stop (FPR)':<16} | {'False Stops':<12} | {'Caught Failures':<15}")
    print("-" * 80)
    for row in curve:
        print(f"{row['threshold']:<12.2f} | {row['failure_recall']*100:<14.1f}% | {row['false_stop_rate']*100:<15.1f}% | {row['false_stops_count']:<12} | {row['caught_failures_count']:<15}")

    print("\n=== 2. 5-FOLD GROUPED CROSS-VALIDATION (Mean ± Std) ===")
    cv_results = compute_5fold_grouped_cv(df)
    print(f"{'Model Architecture':<22} | {'Failure Recall':<18} | {'False Stop (FPR)':<18} | {'Cost MAE ($)':<16} | {'Cost R²':<15}")
    print("-" * 95)
    for model_name, metrics in cv_results.items():
        rec_mean, rec_std = np.mean(metrics['recalls']) * 100, np.std(metrics['recalls']) * 100
        fpr_mean, fpr_std = np.mean(metrics['fprs']) * 100, np.std(metrics['fprs']) * 100
        mae_mean, mae_std = np.mean(metrics['maes']), np.std(metrics['maes'])
        r2_mean, r2_std = np.mean(metrics['r2s']), np.std(metrics['r2s'])
        print(f"{model_name:<22} | {rec_mean:5.1f}% ± {rec_std:4.1f}%  | {fpr_mean:5.1f}% ± {fpr_std:4.1f}%  | ${mae_mean:7.4f} ± {mae_std:6.4f} | {r2_mean:6.3f} ± {r2_std:5.3f}")
