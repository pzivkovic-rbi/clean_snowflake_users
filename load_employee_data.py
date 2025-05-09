import boto3
import csv
import io
import os

def normalize_name(name):
    """Lowercase, strip, and collapse whitespace for robust name comparison."""
    return " ".join(name.lower().split())

def fetch_employee_list(bucket, key):
    """
    Download the employee CSV from S3 and return:
      - a set of user emails (uppercased)
      - a set of normalized full names (from Full_Name column)
    Includes both Employees and Contingent Workers (contractors).
    """
    s3 = boto3.client("s3")
    obj = s3.get_object(Bucket=bucket, Key=key)
    body = obj["Body"].read().decode("utf-8")
    reader = csv.DictReader(io.StringIO(body))
    emails = set()
    full_names = set()
    email_col = "Email"
    name_col = "Full_Name"
    for row in reader:
        email = row.get(email_col, "").strip().upper()
        if email:
            emails.add(email)
        full_name = row.get(name_col, "").strip()
        if full_name:
            full_names.add(normalize_name(full_name))
    return emails, full_names
