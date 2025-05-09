# Snowflake User Cleanup Script

This script helps automate the cleanup of old Snowflake user accounts by comparing users defined in your Terraform repo with a list of currently employed users from an S3 CSV export.

## Features

- Loads the current employee list from a CSV in S3 (using boto3).
- Parses users from `users.tf`, excluding machine users.
- Compares repo users to the employee list and identifies candidates for removal.
- Outputs a candidate list for manual review/editing.
- On confirmation, removes all references to the selected users from:
  - `users.tf`
  - `users.sql`
  - `grants.tf`
  - `masking_policies.tf`
- Modular, robust, and easily extensible for future checks (e.g., inactivity).

## Project Structure

```
clean_snowflake_users/
├── main.py
├── config.yaml
├── load_employee_data.py
├── parse_users.py
├── file_editor.py
├── utils.py
├── requirements.txt
└── README.md
```

## Configuration

Edit `config.yaml` to specify:

- S3 bucket/key for the employee CSV
- Paths to the relevant repo files
- List of excluded (machine) users

Example:
```yaml
s3:
  bucket: rbi-data-workday-exports
  key: org-report.csv

files:
  users_tf: rbi-snowflake/.snowflake/modules/account/users.tf
  users_sql: rbi-snowflake/.snowflake/modules/snowflake_cost/sql/dim/users.sql
  grants_tf: rbi-snowflake/.snowflake/modules/account/grants.tf
  masking_policies_tf: rbi-snowflake/.snowflake/modules/account/masking_policies.tf

exclude_users:
  - keboola_bk
  - keboola_fhs
  - keboola_plk
  - keboola_th
```

## Usage

1. **Install dependencies**  
   ```
   pip install -r requirements.txt
   ```

2. **Configure AWS credentials**  
   Ensure your terminal has access to AWS credentials for S3 access (via environment variables, `~/.aws/credentials`, or similar).

3. **Run the script**  
   ```
   python main.py
   ```

4. **Review the candidate list**  
   - The script will write a file `removal_candidates.txt` with the list of users to be removed.
   - Edit this file to remove any users you do **not** want to delete.
   - Save and close the file, then press Enter in the terminal to continue.

5. **Review changes**  
   - The script will update all relevant files in-place.
   - Review the changes with `git diff`, then commit and push as needed.

## Extending

- To add new checks (e.g., inactivity), extend `parse_users.py` or add new modules.
- To support new file types, add logic to `file_editor.py`.

## Notes

- No git/PR automation is included; use your normal git workflow to review and submit changes.
- The script is robust to comments and formatting, but always review changes before committing.
