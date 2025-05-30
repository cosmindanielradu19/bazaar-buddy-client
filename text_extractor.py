from __future__ import annotations

"""A minimal OCR helper around pytesseract.

This version removes all OpenCV‑based pre‑processing and lets Tesseract work
directly on the supplied image.

If you need pre‑processing, do it upstream and feed the cleaned bitmap to the
extractor.
"""

import os
from pathlib import Path
from typing import List

from PIL import Image
import pytesseract
from pytesseract import Output

from configuration import Configuration
from logging import Logger

class TextExtractor:
    """Thin wrapper around *pytesseract*.

    Parameters
    ----------
    configuration
        Runtime configuration (already initialised elsewhere).
    logger
        App‑wide logger instance.
    lang
        Tesseract language(s) to load; default is ``"eng"``.
    tess_config
        Extra config string(s) forwarded to Tesseract.  The historical
        default ``"bazaar_terms"`` is kept for backward compatibility.
    """

    def __init__(
        self,
        configuration: Configuration,
        logger: Logger,
        *,
        lang: str = "eng",
        tess_config: str = "bazaar_terms",
    ) -> None:
        self._configuration = configuration
        self._logger = logger
        self._lang = lang
        self._tess_config = tess_config

        self._prepare_tesseract_paths()

    # ------------------------------ public API --------------------------- #
    def extract_text(
        self,
        image: Image.Image,
        *,
        confidence_threshold: int = 80,
    ) -> str:
        """OCR a :class:`PIL.Image.Image` and return a *single* text string.

        Parameters
        ----------
        image
            RGB or RGBA PIL image.
        confidence_threshold
            Any Tesseract word candidate below this value (0‑100) is thrown
            away.  Default is **80**.
        """
        self._logger.debug(
            "Extracting text (conf>=%d)", confidence_threshold
        )

        tesser_data = pytesseract.image_to_data(
            image,
            lang=self._lang,
            config=self._tess_config,
            output_type=Output.DICT,
        )

        keep: List[str] = [
            txt
            for txt, conf in zip(tesser_data["text"], tesser_data["conf"])
            if txt.strip() and int(conf) >= confidence_threshold
        ]
        return " ".join(keep)

    def extract_text_from_file(
        self,
        image_path: Path | str,
    ) -> str:
        """Convenience wrapper around :py:meth:`extract_text`."""
        path = Path(image_path)
        self._logger.debug("Opening image file %s", path)
        with Image.open(path) as img:
            return self.extract_text(img)

    # -------------------------- internal utilities ----------------------- #
    def _prepare_tesseract_paths(self) -> None:
        """Point *pytesseract* at the bundled Tesseract binaries and data."""
        if self._configuration.operating_system == "Windows":
            tess_dir = self._configuration.system_path / "tools" / "windows_tesseract"
            pytesseract.pytesseract.tesseract_cmd = str(tess_dir / "tesseract.exe")
            os.environ["TESSDATA_PREFIX"] = str(tess_dir / "tessdata")
        else:
            tess_dir = self._configuration.system_path / "tools" / "mac_tesseract"
            pytesseract.pytesseract.tesseract_cmd = str(tess_dir / "bin" / "tesseract")
            os.environ["DYLD_LIBRARY_PATH"] = str(tess_dir / "lib")
            os.environ["TESSDATA_PREFIX"] = str(tess_dir / "share" / "tessdata")

        self._logger.debug(
            "Configured Tesseract binary: %s", pytesseract.pytesseract.tesseract_cmd
        )


# --------------------------------------------------------------------- #
# Quick self‑test — run `python -m ocr_text_extractor` to verify
# --------------------------------------------------------------------- #
if __name__ == "__main__":  # pragma: no cover
    from logger import logger

    cfg = Configuration()
    extractor = TextExtractor(cfg, logger)

    sample_file = Path("20250511_171546_141155.png")
    text = extractor.extract_text_from_file(sample_file)
    print(text)
