# Requirements for Bronze Ingestion

## 1. Sources

* Data may come from **S3** or **local paths**.
* Paths can use **glob or regex patterns**.

## 2. File Formats

* **Structured**: CSV, JSON, line-delimited JSON, Parquet, VTT.
* **Single-row-per-file**: one file maps to one row (e.g., transcripts, metadata, JSON).
* **Binary**: images, media, or other blobs.

## 3. Compression

* Supported: **gzip, snappy, zip**, etc.
* Zipped archives may contain multiple files.

## 4. Ingestion Modes

* **File-per-row**: file content or metadata stored as one row.
* **Multi-row files**: CSV, JSONL, and Parquet contain multiple rows.

## 5. Table Mapping

* Each use case has **multiple bronze tables**.
* Each bronze table has **exactly one source** (path + format).

## 6. Metadata

* Capture for every record:

  * `filename`
  * `path`
  * `ingestion_timestamp`
  * `file_format`
  * `compression_type`

## 7. Output

* Write data to **Delta bronze tables**.
* Store error records in a **quarantine table**.
* For binary/blob ingestion:

  * Store file content in a `BINARY` column.
  * Include metadata columns for provenance.

---

# Standardized Bronze Schemas

## 1. Structured Multi-Row Files (CSV, JSONL, Parquet)

* Schema is **predetermined** per table (defined in upstream design).
* Standard metadata columns must be added:

```text
<domain_columns...>   -- business-specific fields
filename STRING
path STRING
ingestion_timestamp TIMESTAMP
file_format STRING
compression_type STRING
```

## 2. Single-Row-Per-File (Text, VTT, JSON)

* File content treated as **TEXT**.
* Schema:

```text
content STRING
filename STRING
path STRING
ingestion_timestamp TIMESTAMP
file_format STRING
compression_type STRING
```

## 3. Binary / Blob Files (Images, Media, Other Blobs)

* File content stored as **BINARY**.
* Schema:

```text
content BINARY
filename STRING
path STRING
ingestion_timestamp TIMESTAMP
file_format STRING
compression_type STRING
```

---
```yaml
tables:
  bronze_orders:
	input_path: "s3://my-bucket/orders/*2025*.csv.gz"
	file_type: csv
	compression: gzip
	options:
	  header: true

  bronze_returns:
	input_path: "s3://my-bucket/returns/*.json"
	file_type: json
	compression: none
	options:
	  multiline: false
```

```yaml
tables:
  bronze_error_logs:
	input_path: "s3://my-bucket/logs/*error*.jsonl"
	file_type: jsonl
	compression: none
	options:
	  multiline: false

  bronze_access_logs:
	input_path: "s3://my-bucket/logs/*access*.jsonl"
	file_type: jsonl
	compression: none
	options:
	  multiline: false
```

```yaml
tables:
  bronze_transcripts:
	input_path: "/mnt/raw/transcripts/*.zip"
	file_type: vtt
	compression: zip
	row_mode: file_per_row
	options: {}
```

```yaml
tables:
  bronze_profiles:
	input_path: "s3://my-bucket/profiles/*.parquet"
	file_type: parquet
	compression: snappy
	options: {}
```

```yaml
tables:
  bronze_images:
	input_path: "s3://my-bucket/media/images/*"
	file_type: binary
	compression: none
	row_mode: file_per_row
	options: {}

  bronze_videos:
	input_path: "s3://my-bucket/media/videos/*.zip"
	file_type: binary
	compression: zip
	row_mode: file_per_row
	options: {}
```