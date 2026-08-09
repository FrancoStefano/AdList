# !/usr/bin/python3
# -*- coding:utf-8-*-
import os
import collections


def build_output_lines(target_file):
    # 1. Read and Deduplicate
    with open(target_file, 'r', encoding='utf-8') as f:
        # Using a set to immediately remove exact line duplicates
        # Skip comment lines (!) and section headers (#)
        raw_lines = set(line.strip() for line in f if line.strip()
                        and not line.strip().startswith('!')
                        and not line.strip().startswith('#'))

    grouped_domains = collections.defaultdict(list)
    seen_normalized = set()

    # 2. Logic for grouping and deduplication (after ABP standardization)
    for domain in raw_lines:
        # Split off trailing commentary (e.g. "iconfactory.net ### TapestryAds"):
        # a '#' preceded by whitespace is a human comment, not part of the domain.
        commentary = ""
        hash_idx = domain.find('#')
        if hash_idx > 0 and domain[hash_idx - 1] == ' ':
            domain, commentary = domain[:hash_idx].rstrip(), domain[hash_idx:]

        # Normalize single | prefix to || (invalid ABP format)
        if domain.startswith("|") and not domain.startswith("||") and not domain.startswith("@@"):
            domain = "|" + domain

        # Standardize format: ensure it has || and ^ unless it already starts with || or @@
        if not domain.startswith("||") and not domain.startswith("@@"):
            domain = f"||{domain}"
        if "^" not in domain:
            domain = f"{domain}^"

        if commentary:
            domain = f"{domain} {commentary}"

        # Deduplicate after standardization so 'extend.tv' and '||extend.tv^' are treated as the same
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

    # 3. Format the output
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
            output_lines.append(d)

        output_lines.append("")  # Empty line between groups

    return output_lines, len(seen_normalized)


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

    output_lines, count = build_output_lines(target_file)
    content = "\n".join(output_lines)

    # 2. Save to ABPcleanedList.txt
    #with open("ABPcleanedList.txt", "w", encoding='utf-8') as f:
    #    f.write(content)
    #print(f"Success! Processed {count} unique entries into 'ABPcleanedList.txt'.")

    # 3. Also update ABPList (no extension) if it exists in the same folder
    abplist_path = os.path.join(current_dir, "ABPList")
    if os.path.exists(abplist_path):
        with open(abplist_path, "w", encoding='utf-8') as f:
            f.write(content)
        print(f"Also updated 'ABPList'.")
    else:
        print("Note: 'ABPList' not found in the current directory, skipping.")


if __name__ == "__main__":
    process_abp_list()