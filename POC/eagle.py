# 📦 Import libraries
from astropy.io import fits
from astropy.visualization import PercentileInterval, AsinhStretch, ImageNormalize
import numpy as np
import matplotlib.pyplot as plt
from skimage.restoration import richardson_lucy
from scipy.ndimage import gaussian_filter, median_filter
from skimage import exposure

# 📂 Load FITS files
fits_oiii = fits.open(r"zdata\502nmos.fits")[0].data.astype(np.float32)
fits_ha   = fits.open(r"zdata\656nmos.fits")[0].data.astype(np.float32)
fits_sii  = fits.open(r"zdata\673nmos.fits")[0].data.astype(np.float32)

# 🌈 Stretch with Asinh + percentile normalization
def stretch(img, pct=99.8, beta=0.8):
    interval = PercentileInterval(pct)
    v = interval(img)
    v = (v - v.min()) / (v.max() - v.min() + 1e-9)
    norm = ImageNormalize(v, stretch=AsinhStretch(beta))
    return norm(v)

s_oiii = stretch(fits_oiii)
s_ha   = stretch(fits_ha)
s_sii  = stretch(fits_sii)

# 🔴 Gamma correction to enhance color gradients
def gamma_correct(img, gamma=1.2):
    return np.power(np.clip(img, 0, 1), gamma)

s_sii_boosted  = gamma_correct(s_sii * 1.8, gamma=1.2)  # Red channel
s_ha_boosted   = gamma_correct(s_ha  * 1.0, gamma=1.1)  # Green channel
s_oiii_boosted = gamma_correct(s_oiii * 1.4, gamma=1.1) # Blue channel

# 🎨 Stack into RGB (SHO palette)
rgb = np.dstack([s_sii_boosted, s_ha_boosted, s_oiii_boosted])

# 🌟 Use H-alpha as luminance and apply CLAHE + sharpening
L_clahe = exposure.equalize_adapthist(s_ha, clip_limit=0.03)
psf = np.ones((3,3))/9
L_sharp = richardson_lucy(L_clahe, psf, num_iter=20)

# 🧠 Apply luminance sharpening
rgb_lum = np.clip(rgb * (L_sharp[..., None] + 1e-3), 0, 1)

# 🧼 Reduce star halos with median filtering
rgb_clean = median_filter(rgb_lum, size=(1,1,1))
rgb_final = np.clip(0.8 * rgb_lum + 0.2 * rgb_clean, 0, 1)

# 🖼️ Display final image
plt.figure(figsize=(14,14))
plt.imshow(rgb_final, origin='lower')
plt.title("Pillars of Creation – Enhanced SHO Composite")
plt.axis('off')
plt.show()
