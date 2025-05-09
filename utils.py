import yaml
import os

def load_yaml(path):
    with open(path, "r") as f:
        return yaml.safe_load(f)

def prompt_user_review(removal_candidates, user_email_map):
    """
    Write the candidate list to a file for manual review/editing.
    User can remove any lines they don't want to delete.
    """
    review_file = "removal_candidates.txt"
    with open(review_file, "w") as f:
        f.write("# Edit this file to remove any users you do NOT want to delete.\n")
        f.write("# Only lines not starting with '#' will be processed.\n")
        for u in removal_candidates:
            f.write(f"{u}  # {user_email_map[u]}\n")

    print(f"\nReview the candidate list in '{review_file}'.")
    print("Remove any users you do NOT want to delete, then save and close the file.")
    input("Press Enter when you are done reviewing the file...")

    # Read back the approved list
    approved_users = []
    with open(review_file, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            # Only take the username (before any comment)
            username = line.split("#")[0].strip()
            if username:
                approved_users.append(username)
    return approved_users
