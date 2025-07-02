import os
import subprocess
import datetime
import logging
from celery import shared_task
from google.cloud import storage
from django.conf import settings

logger = logging.getLogger(__name__)

@shared_task
def backup_mssql_to_gcs():
    """
    Celery task to perform MSSQL database backup and upload to Google Cloud Storage.
    """
    logger.info("Starting MSSQL database backup and GCS upload task...")

    db_settings = settings.DATABASES['default']
    db_name = db_settings['NAME']
    db_host = db_settings['HOST']
    db_user = db_settings['USER']
    db_password = db_settings['PASSWORD']

    # Define local backup directory and filename
    # Ensure this directory exists and is writable by the user running Celery worker
    local_backup_dir = "/tmp/mssql_backups" # Using /tmp for temporary storage
    os.makedirs(local_backup_dir, exist_ok=True)

    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    backup_filename = f"{db_name}_backup_{timestamp}.bak"
    local_backup_path = os.path.join(local_backup_dir, backup_filename)

    gcs_bucket_name = "your-gcs-bucket-name" # TODO: Replace with your actual GCS bucket name
    gcs_destination_blob_name = f"database_backups/{backup_filename}"

    try:
        # Step 1: Perform MSSQL backup using sqlcmd
        logger.info(f"Performing MSSQL backup to {local_backup_path}...")
        
        # Construct the sqlcmd command
        # For production, consider using a dedicated SQL user with minimal permissions for backup.
        # Also, ensure the MSSQL server has write access to the local_backup_dir if it's a shared path.
        # If sqlcmd is not available or not writing to the Celery worker's local filesystem,
        # you'd need an intermediate step (e.g., MSSQL writes to a shared network drive, then Celery worker picks it up).
        
        # For better security, use environment variables for credentials or a config management system.
        # For this example, I'm using the settings.DATABASES values.
        sql_command = f"""
        DECLARE @BackupFileName NVARCHAR(255);
        DECLARE @BackupPath NVARCHAR(255);
        SET @BackupPath = N'{local_backup_dir}/';
        SET @BackupFileName = @BackupPath + N'{backup_filename}';

        BACKUP DATABASE [{db_name}]
        TO DISK = @BackupFileName
        WITH NOFORMAT, NOINIT, NAME = N'{db_name}-Full Database Backup', SKIP, NOREWIND, NOUNLOAD, STATS = 10;
        """
        
        cmd = [
            "sqlcmd",
            "-S", f"{db_host}",
            "-U", f"{db_user}",
            "-P", f"{db_password}",
            "-Q", sql_command.replace('\n', ' ').strip() # Remove newlines and strip for -Q
        ]
        
        # Execute the command
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        logger.info(f"sqlcmd stdout: {result.stdout}")
        if result.stderr:
            logger.warning(f"sqlcmd stderr: {result.stderr}")

        logger.info(f"MSSQL backup created at {local_backup_path}")

        # Step 2: Upload to Google Cloud Storage
        logger.info(f"Uploading {local_backup_path} to GCS bucket {gcs_bucket_name} as {gcs_destination_blob_name}...")
        client = storage.Client()
        bucket = client.bucket(gcs_bucket_name)
        blob = bucket.blob(gcs_destination_blob_name)
        blob.upload_from_filename(local_backup_path)
        logger.info("Backup uploaded to GCS successfully.")

        # Step 3: Clean up local backup file
        logger.info(f"Deleting local backup file: {local_backup_path}")
        os.remove(local_backup_path)
        logger.info("Local backup file deleted.")

        # Step 4: (Optional) Clean up old backups in GCS (e.g., older than 30 days)
        retention_days_gcs = 30
        logger.info(f"Cleaning up GCS backups older than {retention_days_gcs} days in {gcs_bucket_name}/database_backups/...")
        
        blobs = client.list_blobs(gcs_bucket_name, prefix="database_backups/")
        now = datetime.datetime.now(datetime.timezone.utc) # Use timezone-aware datetime
        
        for blob in blobs:
            if blob.name.endswith('.bak'):
                # blob.time_created is timezone-aware
                age = now - blob.time_created
                if age.days > retention_days_gcs:
                    logger.info(f"Deleting old GCS backup: {blob.name} (created {blob.time_created})")
                    blob.delete()
        logger.info("GCS cleanup complete.")

    except subprocess.CalledProcessError as e:
        logger.error(f"Error during MSSQL backup (sqlcmd failed): {e}")
        logger.error(f"sqlcmd stdout: {e.stdout}")
        logger.error(f"sqlcmd stderr: {e.stderr}")
        raise # Re-raise to mark task as failed
    except Exception as e:
        logger.error(f"An error occurred during backup or upload: {e}", exc_info=True)
        raise # Re-raise to mark task as failed
