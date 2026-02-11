# import os
# import collections
#
#
# def process_abp_list():
#     # 1. Look for .txt files in the current directory
#     current_dir = os.getcwd()
#     txt_files = [f for f in os.listdir(current_dir)
#                  if f.endswith('.txt') and f != "ABPcleanedList.txt"]
#
#     target_file = ""
#
#     if txt_files:
#         target_file = txt_files[0]
#         print(f"Found file: {target_file}. Processing...")
#     else:
#         target_file = input("No .txt files found. Please enter the full path to your file: ").strip()
#
#     if not os.path.exists(target_file):
#         print("Error: File not found.")
#         return
#
#     # 2. Read the file
#     with open(target_file, 'r', encoding='utf-8') as f:
#         lines = f.readlines()
#
#     # 3. Logic for grouping and sorting
#     grouped_domains = collections.defaultdict(list)
#
#     for line in lines:
#         domain = line.strip()
#         if not domain:
#             continue
#
#         # Determine sorting key (ignoring www. and case)
#         sort_key = domain.lower()
#         if sort_key.startswith("www."):
#             sort_key = sort_key[4:]
#         elif sort_key.startswith("||"):  # Handle existing ABP markers
#             sort_key = sort_key[2:]
#
#         if not sort_key:
#             continue
#
#         first_letter = sort_key[0].upper()
#         grouped_domains[first_letter].append(domain)
#
#     # 4. Format the output
#     sorted_keys = sorted(grouped_domains.keys())
#     output_lines = []
#
#     for key in sorted_keys:
#         output_lines.append(f"#[{key}]")
#
#         # Sort domains within the group (ignoring 'www.')
#         current_group = sorted(
#             grouped_domains[key],
#             key=lambda x: x.lower()[4:] if x.lower().startswith("www.") else x.lower()
#         )
#
#         for d in current_group:
#             # Preserve existing formatting if it already looks like an ABP rule
#             if d.startswith("||"):
#                 output_lines.append(d)
#             else:
#                 output_lines.append(f"||{d}^")
#
#         output_lines.append("")  # Empty line between groups
#
#     # 5. Write to the new file
#     with open("ABPcleanedList.txt", "w", encoding='utf-8') as f:
#         f.write("\n".join(output_lines))
#
#     print("Success! Created 'ABPcleanedList.txt'.")
#
#
# if __name__ == "__main__":
#     process_abp_list()


import os
import collections


def process_abp_list():
    # 1. File Discovery
    current_dir = os.getcwd()
    txt_files = [f for f in os.listdir(current_dir)
                 if f.endswith('.txt') and f != "ABPcleanedList.txt"]

    target_file = ""
    if txt_files:
        target_file = txt_files[0]
        print(f"Found file: {target_file}. Processing...")
    else:
        target_file = input("No .txt files found. Please enter the full path to your file: ").strip()

    if not os.path.exists(target_file):
        print("Error: File not found.")
        return

    # 2. Read and Deduplicate
    with open(target_file, 'r', encoding='utf-8') as f:
        # Using a set to immediately remove exact line duplicates
        raw_lines = set(line.strip() for line in f if line.strip())

    grouped_domains = collections.defaultdict(list)
    seen_normalized = set()

    # 3. Logic for grouping and secondary deduplication
    for domain in raw_lines:
        # Create a "normalized" version to check for duplicates like 'example.com' vs 'Example.com'
        norm = domain.lower()
        if norm in seen_normalized:
            continue
        seen_normalized.add(norm)

        # Determine sorting key (ignoring www. and ABP markers)
        sort_key = norm
        if sort_key.startswith("||"):
            sort_key = sort_key[2:]
        if sort_key.startswith("www."):
            sort_key = sort_key[4:]

        if not sort_key:
            continue

        first_letter = sort_key[0].upper()
        grouped_domains[first_letter].append(domain)

    # 4. Format the output
    sorted_keys = sorted(grouped_domains.keys())
    output_lines = []

    for key in sorted_keys:
        output_lines.append(f"#[{key}]")

        # Sort domains within the group (ignoring 'www.' prefix and '||' markers)
        def get_sort_val(x):
            val = x.lower()
            if val.startswith("||"): val = val[2:]
            if val.startswith("www."): val = val[4:]
            return val

        current_group = sorted(grouped_domains[key], key=get_sort_val)

        for d in current_group:
            # Standardize format: ensure it has || and ^ unless it already has complex rules
            if not d.startswith("||"):
                d = f"||{d}"
            if "^" not in d:
                d = f"{d}^"
            output_lines.append(d)

        output_lines.append("")  # Empty line between groups

    # 5. Save output
    with open("ABPcleanedList.txt", "w", encoding='utf-8') as f:
        f.write("\n".join(output_lines))

    print(f"Success! Processed {len(seen_normalized)} unique entries into 'ABPcleanedList.txt'.")


if __name__ == "__main__":
    process_abp_list()