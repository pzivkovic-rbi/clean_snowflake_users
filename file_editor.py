import re
import os

def remove_users_from_files(usernames, files, user_email_map):
    remove_from_users_tf(files["users_tf"], usernames)
    remove_from_users_sql(files["users_sql"], usernames, user_email_map)
    remove_from_grants_tf(files["grants_tf"], usernames)
    remove_from_masking_policies_tf(files["masking_policies_tf"], usernames)
    print("All user references removed from files.")

def remove_from_users_tf(path, usernames):
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # Remove from lists and resource blocks
    new_lines = []
    skip_block = False
    block_username = None
    for line in lines:
        # Remove from lists (snowflake_user.<username>, with or without comma)
        if any(re.search(rf"snowflake_user\.{re.escape(u)}\b", line) for u in usernames):
            continue
        # Remove resource blocks for these users
        m = re.match(r'resource\s+"snowflake_user"\s+"([a-zA-Z0-9_]+)"', line)
        if m and m.group(1) in usernames:
            skip_block = True
            block_username = m.group(1)
            continue
        if skip_block:
            # End of block is a line with just "}"
            if line.strip() == "}":
                skip_block = False
                block_username = None
            continue
        new_lines.append(line)

    with open(path, "w", encoding="utf-8") as f:
        f.writelines(new_lines)
    print(f"  - users.tf: removed {len(usernames)} users")

def remove_from_users_sql(path, usernames, user_email_map):
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    emails = set(user_email_map[u].upper() for u in usernames if u in user_email_map)
    new_lines = []
    for line in lines:
        # Remove lines with ('EMAIL', ...) for these users
        if any(email in line.upper() for email in emails):
            continue
        new_lines.append(line)

    with open(path, "w", encoding="utf-8") as f:
        f.writelines(new_lines)
    print(f"  - users.sql: removed {len(emails)} users")

def remove_from_grants_tf(path, usernames):
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    new_lines = []
    for line in lines:
        # Remove any line referencing snowflake_user.<username> (with or without .name)
        if any(re.search(rf"snowflake_user\.{re.escape(u)}(\.name)?\b", line) for u in usernames):
            continue
        new_lines.append(line)

    with open(path, "w", encoding="utf-8") as f:
        f.writelines(new_lines)
    print(f"  - grants.tf: removed references to {len(usernames)} users")

def remove_from_masking_policies_tf(path, usernames):
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    new_lines = []
    for line in lines:
        # Remove lines with (snowflake_user.<username>.name)
        if any(re.search(rf"\(snowflake_user\.{re.escape(u)}\.name\)", line) for u in usernames):
            continue
        new_lines.append(line)

    with open(path, "w", encoding="utf-8") as f:
        f.writelines(new_lines)
    print(f"  - masking_policies.tf: removed references to {len(usernames)} users")
