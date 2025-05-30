import os
import sys
import yaml

from load_employee_data import fetch_employee_list, normalize_name
from parse_users import parse_users_tf, get_machine_users
from file_editor import remove_users_from_files
from utils import prompt_user_review, load_yaml

def main():
    # Load config
    config_path = os.path.join(os.path.dirname(__file__), "config.yaml")
    config = load_yaml(config_path)

    # Fetch employee list from S3
    print("Fetching current employee list from S3...")
    employee_emails, employee_full_names = fetch_employee_list(config["s3"]["bucket"], config["s3"]["key"])

    # Parse users.tf to get all human users and mapping
    print("Parsing users.tf...")
    users_tf_path = config["files"]["users_tf"]
    all_users, user_info_map = parse_users_tf(users_tf_path)
    machine_users = get_machine_users(users_tf_path)
    excluded_users = set(config.get("exclude_users", [])) | set(machine_users)
    exclude_emails = set(e.upper() for e in config.get("exclude_emails", []))

    # Identify users to remove (not in employee list by email or full name, and not excluded)
    removal_candidates = []
    for u in all_users:
        email, norm_full_name = user_info_map[u]
        email_upper = email.upper() if email else ""
        email_match = email_upper in employee_emails if email else False
        name_match = norm_full_name in employee_full_names if norm_full_name else False
        if (
            not email_match
            and not name_match
            and u not in excluded_users
            and email_upper not in exclude_emails
        ):
            removal_candidates.append(u)

    # Show hardcoded excluded machine users and which are found in users.tf
    print("\nThe following machine users are hardcoded to be excluded from removal (exclude_users):")
    for username in config.get("exclude_users", []):
        if username in all_users:
            print(f"  - {username} (found in users.tf)")
        else:
            print(f"  - {username} (not found in users.tf)")

    # Show hardcoded excluded emails and which users they protect
    print("\nThe following user emails are hardcoded to be excluded from removal (exclude_emails):")
    for email in exclude_emails:
        # Find usernames in users.tf with this email
        protected_usernames = [u for u in all_users if user_info_map[u][0].upper() == email]
        if protected_usernames:
            for uname in protected_usernames:
                print(f"  - {email} (protects username: {uname})")
        else:
            print(f"  - {email} (not found in users.tf)")

    if not removal_candidates:
        print("\nNo users found for removal.")
        return

    # Output candidate list for review
    print("\nFinal candidate users for removal (excluding all above):")
    for u in removal_candidates:
        email, norm_full_name = user_info_map[u]
        print(f"  - {u} (email: {email}, name: {norm_full_name})")

    # Allow user to review/edit the list
    # For prompt_user_review, pass a mapping of username to email for backward compatibility
    user_email_map = {u: user_info_map[u][0] for u in all_users}
    approved_users = prompt_user_review(removal_candidates, user_email_map)

    if not approved_users:
        print("No users selected for removal. Exiting.")
        return

    # Remove users from all files
    print("\nRemoving users from files...")
    remove_users_from_files(approved_users, config["files"], user_email_map)

    print("\nCleanup complete. Please review the changes and commit as needed.")

if __name__ == "__main__":
    main()
