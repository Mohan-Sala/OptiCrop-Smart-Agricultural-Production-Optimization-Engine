#!/usr/bin/env python3
"""
OptiCrop AI - PostgreSQL to MongoDB Atlas & GridFS Migration Tool

This script connects to a PostgreSQL database and migrates all relational tables
into MongoDB Atlas collections, and optionally migrates files into MongoDB GridFS.

Usage:
    python migrate_postgres_to_mongodb.py [--dry-run] [--skip-storage]

Requirements:
    pip install -r migration_requirements.txt
"""

import os
import sys
import uuid
import json
import logging
import argparse
from datetime import datetime, date, time
from typing import Dict, Any, List, Optional

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

import pymongo
from pymongo import MongoClient, UpdateOne
import gridfs

# Logging Configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("migration")

# Table-to-Collection mapping
TABLE_COLLECTION_MAPPING = {
    "users": "users",
    "refresh_tokens": "refresh_tokens",
    "login_audits": "login_audits",
    "projects": "projects",
    "datasets": "datasets",
    "dataset_statistics": "dataset_statistics",
    "feature_metadata": "feature_metadata",
    "dataset_preprocessing": "dataset_preprocessing",
    "preprocessing_artifacts": "preprocessing_artifacts",
    "training_experiments": "training_experiments",
    "training_sessions": "training_sessions",
    "trained_models": "trained_models",
    "model_metrics": "model_metrics",
    "evaluation_reports": "evaluation_reports",
    "hyperparameter_sets": "hyperparameter_sets",
    "prediction_runs": "prediction_runs",
    "monitoring_alerts": "monitoring_alerts",
    "alert_rules": "alert_rules",
    "drift_snapshots": "drift_snapshots",
    "external_telemetry_logs": "external_telemetry_logs",
    "monitoring_health_logs": "monitoring_health_logs",
    "model_deployments": "model_deployments",
    "deployment_policies": "deployment_policies",
    "deployment_environments": "deployment_environments",
    "deployment_versions": "deployment_versions",
    "deployment_approvals": "deployment_approvals",
    "deployment_health_logs": "deployment_health_logs",
    "deployment_events": "deployment_events",
    "deployment_event_checkpoints": "deployment_event_checkpoints",
    "deployment_freeze_windows": "deployment_freeze_windows",
    "deployment_settings": "deployment_settings",
    "deployment_environment_variables": "deployment_environment_variables",
    "deployment_job_locks": "deployment_job_locks",
    "deployment_replay_metrics": "deployment_replay_metrics",
    "deployment_approval_policies": "deployment_approval_policies",
}


def sanitize_value(val: Any) -> Any:
    """Convert PostgreSQL/Python types into MongoDB-friendly BSON types."""
    if val is None:
        return None
    if isinstance(val, uuid.UUID):
        return val
    if isinstance(val, (datetime, date)):
        if isinstance(val, date) and not isinstance(val, datetime):
            return datetime.combine(val, time.min)
        return val
    if isinstance(val, time):
        return val.isoformat()
    if isinstance(val, (dict, list)):
        return val
    if isinstance(val, str):
        # Attempt to detect UUID strings
        try:
            return uuid.UUID(val)
        except (ValueError, TypeError):
            pass
        # Attempt to detect JSON strings
        if (val.startswith("{") and val.endswith("}")) or (val.startswith("[") and val.endswith("]")):
            try:
                return json.loads(val)
            except Exception:
                pass
        return val
    return val


def sanitize_document(row: Dict[str, Any]) -> Dict[str, Any]:
    """Transform a SQL row dictionary into a MongoDB document with `_id`."""
    doc = {}
    for key, value in row.items():
        doc[key] = sanitize_value(value)

    # Ensure `_id` is populated
    if "id" in doc and doc["id"] is not None:
        doc["_id"] = doc["id"]
    elif "_id" not in doc:
        doc["_id"] = uuid.uuid4()
        doc["id"] = doc["_id"]

    return doc


def migrate_database(sql_engine, mongo_db, dry_run: bool = False) -> Dict[str, int]:
    """Extract rows from SQL and upsert them into MongoDB collections."""
    from sqlalchemy import text, inspect
    inspector = inspect(sql_engine)
    existing_tables = set(inspector.get_table_names())
    summary = {}

    with sql_engine.connect() as conn:
        for table_name, collection_name in TABLE_COLLECTION_MAPPING.items():
            if table_name not in existing_tables:
                logger.info("Table '%s' not found in PostgreSQL database. Skipping.", table_name)
                continue

            logger.info("Migrating table '%s' -> collection '%s'...", table_name, collection_name)
            result = conn.execute(text(f"SELECT * FROM {table_name}"))
            rows = result.mappings().all()

            if not rows:
                logger.info("Table '%s' is empty (0 rows).", table_name)
                summary[table_name] = 0
                continue

            documents = [sanitize_document(dict(row)) for row in rows]
            logger.info("Extracted %d rows from '%s'.", len(documents), table_name)

            if dry_run:
                logger.info("[DRY RUN] Would upsert %d documents to '%s'.", len(documents), collection_name)
                summary[table_name] = len(documents)
                continue

            collection = mongo_db[collection_name]
            operations = [
                UpdateOne({"_id": doc["_id"]}, {"$set": doc}, upsert=True)
                for doc in documents
            ]
            res = collection.bulk_write(operations, ordered=False)
            logger.info(
                "Table '%s': %d upserted/modified in '%s'.",
                table_name,
                res.upserted_count + res.modified_count + res.matched_count,
                collection_name,
            )
            summary[table_name] = len(documents)

    return summary


def migrate_local_files_to_gridfs(local_storage_dir: str, mongo_db, dry_run: bool = False) -> Dict[str, int]:
    """Migrate files from a local directory into MongoDB GridFS."""
    summary = {}
    fs = gridfs.GridFS(mongo_db)

    if not os.path.isdir(local_storage_dir):
        logger.info("Local storage directory '%s' not found. Skipping file migration.", local_storage_dir)
        return summary

    migrated_count = 0
    for root, _, files in os.walk(local_storage_dir):
        for file_name in files:
            if file_name.startswith("."):
                continue
            full_path = os.path.join(root, file_name)
            relative_path = os.path.relpath(full_path, local_storage_dir).replace("\\", "/")

            logger.info("Migrating file '%s' to GridFS...", relative_path)
            if dry_run:
                migrated_count += 1
                continue

            try:
                with open(full_path, "rb") as f:
                    data = f.read()

                existing = fs.find_one({"filename": relative_path})
                if existing:
                    fs.delete(existing._id)

                fs.put(
                    data,
                    filename=relative_path,
                    metadata={"migrated_at": datetime.utcnow()},
                )
                migrated_count += 1
            except Exception as e:
                logger.error("Failed to migrate file '%s': %s", relative_path, e)

    summary["local_files"] = migrated_count
    logger.info("Local storage: %d files migrated to GridFS.", migrated_count)
    return summary


def main():
    parser = argparse.ArgumentParser(description="Migrate PostgreSQL to MongoDB Atlas")
    parser.add_argument("--dry-run", action="store_true", help="Inspect and simulate migration without writing")
    parser.add_argument("--skip-storage", action="store_true", help="Skip migrating local storage files to GridFS")
    parser.add_argument("--storage-dir", default="tmp/uploads", help="Local directory of files to migrate to GridFS")
    args = parser.parse_args()

    postgres_url = os.getenv("DATABASE_URL")
    if not postgres_url:
        logger.error("ERROR: DATABASE_URL environment variable is not set.")
        sys.exit(1)

    # Standardize postgres dialect for SQLAlchemy
    if postgres_url.startswith("postgresql+asyncpg://"):
        postgres_url = postgres_url.replace("postgresql+asyncpg://", "postgresql://")

    mongo_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    mongo_db_name = os.getenv("MONGODB_DATABASE", "opticrop_db")

    logger.info("==================================================")
    logger.info("OptiCrop AI Migration: PostgreSQL -> MongoDB Atlas")
    logger.info("PostgreSQL URL: %s", postgres_url.split("@")[-1] if "@" in postgres_url else postgres_url)
    logger.info("MongoDB URL:    %s", mongo_url.split("@")[-1] if "@" in mongo_url else mongo_url)
    logger.info("Target DB Name: %s", mongo_db_name)
    logger.info("Dry Run Mode:   %s", args.dry_run)
    logger.info("==================================================")

    # Connect to MongoDB
    mongo_client = MongoClient(mongo_url)
    mongo_db = mongo_client[mongo_db_name]

    # Connect to PostgreSQL
    from sqlalchemy import create_engine
    sql_engine = create_engine(postgres_url)

    # Migrate Database
    db_summary = migrate_database(sql_engine, mongo_db, dry_run=args.dry_run)

    # Migrate Storage if requested
    storage_summary = {}
    if not args.skip_storage:
        storage_summary = migrate_local_files_to_gridfs(args.storage_dir, mongo_db, dry_run=args.dry_run)

    # Final Summary Report
    logger.info("==================================================")
    logger.info("MIGRATION COMPLETED SUCCESSFULLY")
    logger.info("Table Migration Counts:")
    for tbl, count in db_summary.items():
        logger.info("  - %-32s : %d", tbl, count)
    if storage_summary:
        logger.info("Storage Migration Counts:")
        for bkt, count in storage_summary.items():
            logger.info("  - %-32s : %d", bkt, count)
    logger.info("==================================================")


if __name__ == "__main__":
    main()
