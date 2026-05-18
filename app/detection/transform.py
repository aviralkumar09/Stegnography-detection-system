import numpy as np


def _haar_energy(gray: np.ndarray) -> float:
    h = gray.shape[0] - (gray.shape[0] % 2)
    w = gray.shape[1] - (gray.shape[1] % 2)
    if h == 0 or w == 0:
        return 0.0
    g = gray[:h, :w]
    approx = (g[0::2, 0::2] + g[1::2, 0::2] + g[0::2, 1::2] + g[1::2, 1::2]) / 4
    detail = g - np.repeat(np.repeat(approx, 2, axis=0), 2, axis=1)
    return float(np.mean(np.abs(detail)))


def transform_analysis(frame: np.ndarray) -> dict:
    gray = frame.mean(axis=2).astype(np.float32)
    dct_like = np.abs(np.fft.fft2(gray))
    high_freq_energy = float(np.mean(dct_like[dct_like.shape[0] // 2 :, dct_like.shape[1] // 2 :]))
    wavelet_energy = _haar_energy(gray)
    score = min(1.0, (high_freq_energy / 1000.0 + wavelet_energy / 30.0) / 2)
    return {
        "module": "transform",
        "score": float(score),
        "details": {"dct_energy": high_freq_energy, "wavelet_energy": wavelet_energy},
    }
