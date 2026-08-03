import csv
import io
import os
from typing import List
from app.utils.exceptions import ValidationException


class ValidationService:
    """Performs structural and semantic checks on uploaded CSV datasets."""

    def validate_file_basics(self, filename: str, content_type: str, file_size: int) -> None:
        """Validates basic file metadata before reading the stream."""
        if not filename.lower().endswith(".csv"):
            raise ValidationException("Invalid file: only CSV file formats (.csv) are supported.")

        # Accept common CSV MIME types or text files
        allowed_mimes = {
            "text/csv",
            "text/plain",
            "application/csv",
            "application/vnd.ms-excel",
            "text/x-csv",
            "application/x-csv",
            "text/comma-separated-values",
            "application/octet-stream",  # Fallback for raw byte streams
        }
        if content_type not in allowed_mimes and not content_type.startswith("text/"):
            raise ValidationException(f"Invalid MIME type: file format '{content_type}' is not supported.")

        if file_size <= 0:
            raise ValidationException("Invalid file: the uploaded file is empty.")

        max_size = 100 * 1024 * 1024  # 100 MB
        if file_size > max_size:
            raise ValidationException("Payload too large: maximum upload size limit is 100 MB.")

    def validate_csv_content(self, file_path: str, encoding: str = "utf-8", delimiter: str = ",") -> None:
        """Performs structural parsing validation of the saved temporary file."""
        if not os.path.exists(file_path):
            raise ValidationException("System error: temporary file path does not exist.")

        try:
            with open(file_path, "r", encoding=encoding, newline="") as f:
                reader = csv.reader(f, delimiter=delimiter)
                
                # Check for empty headers
                try:
                    headers = next(reader)
                except StopIteration:
                    raise ValidationException("Empty dataset: file does not contain a header row.")

                if not headers or all(not col.strip() for col in headers):
                    raise ValidationException("Missing header: CSV column headers cannot be empty.")

                # Check duplicate column names
                seen_columns = set()
                for i, col in enumerate(headers):
                    col_name = col.strip()
                    if not col_name:
                        raise ValidationException(f"Missing header name: column index {i} has an empty label.")
                    if col_name in seen_columns:
                        raise ValidationException(f"Duplicate columns detected: column '{col_name}' is declared multiple times.")
                    seen_columns.add(col_name)

                # Check for empty content (no data rows)
                row_count = 0
                expected_cols = len(headers)
                
                for row_idx, row in enumerate(reader, start=1):
                    row_count += 1
                    # Check for corrupted lines (varying column length)
                    if len(row) != expected_cols:
                        raise ValidationException(
                            f"Corrupted CSV structure: row index {row_idx} contains {len(row)} fields, "
                            f"but the header defined {expected_cols} columns."
                        )
                
                if row_count == 0:
                    raise ValidationException("Empty dataset: the CSV file contains headers but has no data rows.")
        except UnicodeDecodeError:
            raise ValidationException(f"Encoding mismatch: the file is not decodable using character set '{encoding}'.")
        except csv.Error as e:
            raise ValidationException(f"Corrupted CSV: parsing error encountered: {str(e)}")
