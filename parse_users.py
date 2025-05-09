import re

def normalize_name(name):
    return " ".join(name.lower().split())

def parse_users_tf(path):
    """
    Parse users.tf to extract all human user usernames and a mapping to their emails and normalized full names.
    Returns (list_of_usernames, {username: (email, normalized_full_name)})
    """
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # Find all snowflake_user.<username> in human user lists (ignore machine users)
    user_lists = re.findall(r'all_human_[a-z_]+_users\s*=\s*\[(.*?)\]', content, re.DOTALL)
    usernames = set()
    for user_list in user_lists:
        lines = user_list.splitlines()
        for line in lines:
            if "# Machine Users" in line:
                break
            m = re.search(r'snowflake_user\.([a-zA-Z0-9_]+)', line)
            if m:
                usernames.add(m.group(1))

    # Map username to (email, normalized_full_name) by parsing resource blocks
    user_info_map = {}
    for m in re.finditer(
        r'resource\s+"snowflake_user"\s+"([a-zA-Z0-9_]+)"\s*{([^}]*)}',
        content,
        re.DOTALL,
    ):
        username, block = m.group(1), m.group(2)
        # Extract email
        email_match = re.search(r'name\s*=\s*"([^"]+)"', block)
        email = email_match.group(1) if email_match else ""
        # Extract first_name and last_name
        first_name = ""
        last_name = ""
        display_name = ""
        fn_match = re.search(r'first_name\s*=\s*"([^"]+)"', block)
        ln_match = re.search(r'last_name\s*=\s*"([^"]+)"', block)
        dn_match = re.search(r'display_name\s*=\s*"([^"]+)"', block)
        if fn_match:
            first_name = fn_match.group(1)
        if ln_match:
            last_name = ln_match.group(1)
        if dn_match:
            display_name = dn_match.group(1)
        # Prefer first_name + last_name, else display_name
        if first_name and last_name:
            full_name = f"{first_name} {last_name}"
        elif display_name:
            full_name = display_name
        else:
            full_name = ""
        normalized_full_name = normalize_name(full_name)
        user_info_map[username] = (email, normalized_full_name)

    # Only keep usernames that have info mapping
    usernames = [u for u in usernames if u in user_info_map]
    return usernames, user_info_map

def get_machine_users(path):
    """
    Parse users.tf to extract usernames of machine users (from comments and resource blocks).
    Returns a set of usernames.
    """
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    machine_users = set()
    # Find all snowflake_user.<username> after '# Machine Users' in any list
    for user_list in re.findall(r'=\s*\[(.*?)\]', content, re.DOTALL):
        lines = user_list.splitlines()
        in_machine = False
        for line in lines:
            if "# Machine Users" in line:
                in_machine = True
                continue
            if in_machine:
                m = re.search(r'snowflake_user\.([a-zA-Z0-9_]+)', line)
                if m:
                    machine_users.add(m.group(1))
    # Also add all usernames from the dedicated machine user resource blocks at the end
    for m in re.finditer(
        r'resource\s+"snowflake_user"\s+"([a-zA-Z0-9_]+)"\s*{[^}]*?# Machine users',
        content,
        re.DOTALL | re.IGNORECASE,
    ):
        machine_users.add(m.group(1))
    return machine_users
