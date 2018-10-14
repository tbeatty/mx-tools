"""
This script uploads a file and metadata collected from pdf document info
and command line options to Google Cloud Storage.

Example:

    python upload_pdf.py document.pdf \
      --dest-path gs://mx-docs \
      --user-id 1 \
      --tags tag1 tag2
"""

import argparse
import os
import re

from google.cloud import storage
from PyPDF2 import PdfFileReader


def get_doc_info(filename):
    with open(filename, 'rb') as f:
        reader = PdfFileReader(f)
        return reader.getDocumentInfo()


def build_metadata(filename, user_id, tags):
    doc_info = get_doc_info(filename)
    return {'user_id': user_id, 'title': doc_info.title, 'tags': ','.join(tags)}


def upload_pdf(filename, dest_path, user_id, tags=None):
    metadata = build_metadata(filename, user_id, tags)
    match = re.match(r'gs://(.*?)(?:$|/)(.*)', dest_path)
    bucket_name, blob_name = match.groups()
    basename = os.path.basename(filename)
    blob_name = '{}/{}'.format(blob_name, basename) if blob_name else basename
    print('Uploading {} to {}'.format(
        filename,
        'gs://{}/{}'.format(bucket_name, blob_name)))
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(blob_name)
    blob.metadata = metadata
    blob.upload_from_filename(filename)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('filename')
    parser.add_argument(
        '--dest-path',
        required=True,
        help='Path in GCS to write the file')
    parser.add_argument(
        '--user-id',
        type=int,
        help="User id to add to the file's GCS metadata")
    parser.add_argument(
        '--tags',
        nargs='+',
        help="Tags to add to the file's GCS metadata")
    args = parser.parse_args()
    upload_pdf(
        args.filename,
        args.dest_path,
        args.user_id,
        args.tags)


if __name__ == '__main__':
    main()
