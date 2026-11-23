
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ACCURACY IMPROVEMENT: Time-Series Validation
# NEVER shuffle sports data! Train on past, test on future
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
import pandas as pd

def time_series_split(df, train_seasons=None, test_season=None, date_col="Date", season_col="season"):
    """
    Split data WITHOUT shuffling — past = train, future = test.
    
    Usage:
        train, test = time_series_split(data, train_seasons=[2022,2023,2024], test_season=2025)
    """
    if test_season is not None:
        train_df = df[df[season_col].isin(train_seasons)].copy()
        test_df = df[df[season_col] == test_season].copy()
    else:
        df_sorted = df.sort_values(date_col).reset_index(drop=True)
        split_idx = int(len(df_sorted) * 0.8)
        train_df = df_sorted.iloc[:split_idx].copy()
        test_df = df_sorted.iloc[split_idx:].copy()
    
    return train_df, test_df


def walk_forward_split(df, n_splits=5, date_col="Date"):
    """
    Walk-forward validation — repeatedly train on past, test on next block.
    Most reliable way to measure REAL accuracy.
    """
    df_sorted = df.sort_values(date_col).reset_index(drop=True)
    splits = []
    chunk_size = len(df_sorted) // (n_splits + 1)
    
    for i in range(n_splits):
        train_end = (i + 1) * chunk_size
        test_end = train_end + chunk_size
        train = df_sorted.iloc[:train_end]
        test = df_sorted.iloc[train_end:test_end]
        splits.append((train, test))
    
    return splits
