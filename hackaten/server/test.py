from fuzzywuzzy import fuzz

def is_similar(group_name, existing_names, threshold=70):
    for existing_name in existing_names:
        similarity = fuzz.ratio(group_name.lower(), existing_name.lower())
        if similarity >= threshold:
            return False
    return True

# Example usage:
existing_group_names = ['demiurges', 'team', "idk"]
new_group_name = 'creator'

if is_similar(new_group_name, existing_group_names, threshold=50):
    print(f"Adding '{new_group_name}' to the list.")
    existing_group_names.append(new_group_name)
else:
    print(f"'{new_group_name}' is too similar to an existing group name and won't be added.")
