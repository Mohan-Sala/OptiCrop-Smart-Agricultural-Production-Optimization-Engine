import csv
import hashlib
import os
from typing import Tuple
import anyio
from charset_normalizer import detect


class MetadataService:
    """Sniffs CSV properties (delimiters, encodings) and calculates file checksums."""

    async def calculate_sha256(self, file_path: str) -> str:
        """Computes SHA-256 checksum of a file on disk."""
        def _hash():
            sha256 = hashlib.sha256()
            with open(file_path, "rb") as f:
                while chunk := f.read(8192):
                    sha256.update(chunk)
            return sha256.hexdigest()

        return await anyio.to_thread.run_sync(_hash)

    async def detect_encoding_and_delimiter(self, file_path: str) -> Tuple[str, str]:
        """Runs Sniffer and Normalizer in thread pool to extract encoding and separators."""
        def _detect():
            # 1. Detect Character Encoding
            with open(file_path, "rb") as f:
                raw_bytes = f.read(1024 * 1024)  # Read first 1MB for speed
            
            result = detect(raw_bytes)
            encoding = result.get("encoding") or "utf-8"
            
            # 2. Detect Separator Delimiter
            try:
                sample_text = raw_bytes.decode(encoding, errors="ignore")
                lines = [line for line in sample_text.splitlines() if line.strip()]
                if not lines:
                    delimiter = ","
                else:
                    sample = "\n".join(lines[:5])
                    sniffer = csv.Sniffer()
                    dialect = sniffer.sniff(sample, delimiters=[",", ";", "\t", "|"])
                    delimiter = dialect.delimiter
            except Exception:
                delimiter = ","  # Default fallback
                
            return encoding, delimiter

        return await anyio.to_thread.run_sync(_detect)
