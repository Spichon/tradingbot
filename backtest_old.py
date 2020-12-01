# PORTFOLIO METHODS

def roll(self, df, w, **kwargs):
    v = df.values
    d0, d1 = v.shape
    s0, s1 = v.strides

    a = stride(v, (d0 - (w - 1), w, d1), (s0, s0, s1))
    rolled_df = pd.concat({
        row: pd.DataFrame(values, columns=df.columns)
        for row, values in zip(df.index, a)
    })
    return rolled_df.groupby(level=0, **kwargs)

# temp_df = self.roll(assets_returns, 720).apply(lambda x: self.get_percent_wish(x, optimize, assets))



# ASSET METHODS

def roll(self, df, w, **kwargs):
    v = df.values
    d0, d1 = v.shape
    s0, s1 = v.strides

    try:
        a = stride(v, (d0 - (w - 1), w, d1), (s0, s0, s1))
    except ValueError:
        a = stride(v, (d0, w, d1), (s0, s0, s1))
    rolled_df = pd.concat({
        row: pd.DataFrame(values, columns=df.columns)
        for row, values in zip(df.index, a)
    })
    return rolled_df.groupby(level=0, **kwargs)

# temp_df = self.roll(df, 720).apply(lambda x: self.get_weighted_mul(x))
