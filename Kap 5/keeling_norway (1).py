"""
keeling_norway.py
=================

Keeling-kurven for Ny-Ålesund (Zeppelinobservatoriet, Svalbard)
----------------------------------------------------------------
"""

from __future__ import annotations

from datetime import datetime

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from urllib.request import Request, urlopen
from urllib.error import URLError


# =====================================================================
# 1.  DATALASTING
# =====================================================================
NOAA_URL = (
    "https://gml.noaa.gov/aftp/data/trace_gases/co2/flask/surface/txt/"
    "co2_zep_surface-flask_1_ccgg_month.txt"
)


def try_download_zeppelin() -> pd.DataFrame | None:
    try:
        req = Request(NOAA_URL, headers={"User-Agent": "Mozilla/5.0"})
        with urlopen(req, timeout=15) as resp:
            raw = resp.read().decode("utf-8", errors="ignore")
    except (URLError, TimeoutError, OSError):
        return None

    data_lines = [ln for ln in raw.splitlines() if ln and not ln.startswith("#")]
    if not data_lines:
        return None

    rows = []
    for ln in data_lines:
        parts = ln.split()
        if len(parts) < 4:
            continue
        try:
            year = int(parts[1])
            month = int(parts[2])
            value = float(parts[3])
        except ValueError:
            continue
        if value < 0 or value > 700:
            continue
        rows.append((year, month, value))

    if not rows:
        return None

    df = pd.DataFrame(rows, columns=["year", "month", "co2"])
    df["date"] = pd.to_datetime(df[["year", "month"]].assign(day=15))
    df = df.sort_values("date").reset_index(drop=True)
    return df[["date", "co2"]]


def synthetic_zeppelin() -> pd.DataFrame:
    rng = np.random.default_rng(seed=42)
    start = pd.Timestamp("1989-01-15")
    end = pd.Timestamp(datetime.today().replace(day=15))
    dates = pd.date_range(start, end, freq="MS") + pd.Timedelta(days=14)

    t = np.array([(d - start).days / 365.25 for d in dates])

    trend = 352.0 + 1.45 * t + 0.020 * t ** 2

    covid_mask = (dates >= "2020-03-01") & (dates <= "2020-12-31")
    trend = trend - np.where(covid_mask, 0.7, 0.0)

    months = np.array([d.month for d in dates])
    phase_main = 2 * np.pi * (months - 3.2) / 12
    phase_sub  = 2 * np.pi * (months - 11.0) / 6
    seasonal = 6.5 * np.cos(phase_main) + 2.5 * np.cos(phase_sub)

    noise = rng.normal(0.0, 0.35, size=len(dates))

    co2 = trend + seasonal + noise

    return pd.DataFrame({"date": dates, "co2": co2})


def load_data() -> tuple[pd.DataFrame, bool]:
    df = try_download_zeppelin()
    if df is not None and len(df) > 60:
        return df, True
    return synthetic_zeppelin(), False


# =====================================================================
# 2.  HOVEDFIGUR
# =====================================================================
def make_figure(df: pd.DataFrame, is_real: bool) -> plt.Figure:

    df = df.sort_values("date").reset_index(drop=True)

    df["trend_12m"] = df["co2"].rolling(
        window=12, center=True, min_periods=12
    ).mean()

    # Stil (større tekst)
    plt.rcParams.update({
        "font.family":       "DejaVu Sans",
        "font.size":         14,
        "axes.labelsize":    15,
        "axes.titlesize":    18,
        "xtick.labelsize":   13,
        "ytick.labelsize":   13,
        "legend.fontsize":   13,
        "axes.edgecolor":    "#1a1a1a",
        "axes.linewidth":    1.1,
        "axes.spines.top":    True,
        "axes.spines.right":  True,
        "axes.spines.bottom": True,
        "axes.spines.left":   True,
        "xtick.color":       "#1a1a1a",
        "ytick.color":       "#1a1a1a",
        "xtick.direction":   "out",
        "ytick.direction":   "out",
        "figure.facecolor":  "white",
        "axes.facecolor":    "white",
    })

    fig, ax = plt.subplots(figsize=(12.5, 7.2))

    # Månedlige data
    ax.plot(df["date"], df["co2"],
            color="#1f8a8a", linewidth=1.1, alpha=0.95,
            label="Månedlige observasjoner", zorder=2)

    # Glidende middel
    ax.plot(df["date"], df["trend_12m"],
            color="#c82a2a", linewidth=2.4,
            label="Langsiktig trend (12-måneders glidende middel)",
            zorder=4)

    # Akser
    ax.set_xlabel("År")
    ax.set_ylabel("CO₂-konsentrasjon (ppm)")

    ax.grid(True, which="major", axis="both",
            linestyle="--", linewidth=0.7,
            color="#9a9a9a", alpha=0.85)

    ax.set_axisbelow(True)

    ax.xaxis.set_major_locator(mdates.YearLocator(5))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.xaxis.set_minor_locator(mdates.YearLocator(1))

    ymin = np.floor(df["co2"].min() / 10) * 10 - 2
    ymax = np.ceil(df["co2"].max() / 10) * 10 + 4
    ax.set_ylim(ymin, ymax)

    # Undertittel beholdes
    data_label = "målte data" if is_real else "syntetiske data (kalibrert)"
    ax.set_title(
        f"Månedlige middelverdier, 1989–{df['date'].dt.year.max()}   ·   78.9 °N, 11.9 °Ø   ·   {data_label}",
        fontsize=12,
        color="#555555",
        loc="left",
        pad=10
    )

    ax.legend(loc="upper left", frameon=True,
              framealpha=0.95, edgecolor="#cccccc")

    # Kilde
    source_txt = (
        "Kilde: NOAA GML / NILU / Stockholms universitet · Zeppelinobservatoriet (ZEP)"
        if is_real else
        "Kilde: Syntetisk datasett kalibrert mot publiserte verdier fra NILU/MOSJ og NOAA GML"
    )

    fig.text(0.01, 0.01, source_txt,
             fontsize=10, color="#777777", ha="left")

    plt.subplots_adjust(left=0.08, right=0.97, top=0.90, bottom=0.09)

    return fig


# =====================================================================
# 4.  HOVEDPROGRAM
# =====================================================================
def main() -> None:
    print("Laster CO2-data for Zeppelinobservatoriet ...")

    df, is_real = load_data()

    if is_real:
        print(f"  ✔  Reelle NOAA GML-data ({len(df)} månedlige verdier)")
    else:
        print(f"  ⓘ  Bruker syntetisk serie ({len(df)} månedlige verdier)")

    fig = make_figure(df, is_real)

    out_png = "keeling_norway.png"
    fig.savefig(out_png, dpi=200, bbox_inches="tight", facecolor="white")

    print(f"  ✔  Figur lagret som {out_png}")


if __name__ == "__main__":
    main()