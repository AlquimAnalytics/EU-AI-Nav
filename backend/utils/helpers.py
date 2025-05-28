import os, shutil, logging

def archive_file(path, filename):
    """
    Moves processed files to the archive folder.
    """
    archive_dir = os.path.join(path, 'archive')
    file_path = os.path.join(path, filename)
    archive_file_path = os.path.join(archive_dir, filename)
    if not os.path.exists(archive_dir):
        os.makedirs(archive_dir)
        logging.info(f"Created archive directory: {archive_dir}")

    shutil.move(file_path, archive_file_path)
    logging.info(f"Moved {file_path} to archive at {archive_file_path}")

    return

def setup_logging(log_file):
    """
    Configures logging to log messages to a file.
    """
    logging.basicConfig(
        filename=log_file,
        filemode='a',
        format='%(asctime)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )
    logging.info("Logging setup complete.")
