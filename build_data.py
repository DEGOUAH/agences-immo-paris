import re, json, os

BASE = "/tmp/agences_paris"

def parse_text_file(path):
    with open(path, encoding="utf-8") as f:
        content = f.read()
    blocks = [b.strip() for b in content.strip().split("\n\n") if b.strip()]
    entries = []
    for b in blocks:
        lines = [l for l in b.split("\n") if l.strip() != ""]
        # expected: name, rating(reviews), type · address, hours · phone (phone may be missing)
        if len(lines) < 3:
            continue
        name = lines[0]
        rating_line = lines[1] if len(lines) > 1 else ""
        type_addr = lines[2] if len(lines) > 2 else ""
        hours_phone = lines[3] if len(lines) > 3 else ""

        m = re.match(r"([\d.]+)\(([\d,]+)\)", rating_line)
        rating = m.group(1) if m else ""
        reviews = m.group(2).replace(",", "") if m else ""

        if "·" in type_addr:
            parts = [p.strip() for p in type_addr.split("·")]
            biz_type = parts[0]
            address = parts[-1]
        else:
            biz_type = ""
            address = type_addr

        # phone: last token matching phone pattern
        phone_match = re.search(r"(0\d(?:[\s.]?\d{2}){4})", hours_phone)
        phone = phone_match.group(1) if phone_match else ""

        entries.append({
            "name": name,
            "rating": rating,
            "reviews": reviews,
            "type": biz_type,
            "address": address,
            "phone": phone,
        })
    return entries

def parse_web_file(path):
    urls = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            if "|" not in line:
                continue
            name, url = line.split("|", 1)
            urls.append(url.strip())
    return urls

all_data = []
for arr in range(1, 21):
    text_path = os.path.join(BASE, f"arr{arr:02d}_text.txt")
    web_path = os.path.join(BASE, f"arr{arr:02d}_web.txt")
    entries = parse_text_file(text_path)
    urls = parse_web_file(web_path)
    if len(urls) != len(entries):
        print(f"WARNING arr{arr:02d}: {len(entries)} entries vs {len(urls)} urls")
    for i, e in enumerate(entries):
        url = urls[i] if i < len(urls) else ""
        is_real_url = url.startswith("http")
        maps_query = f"{e['name']} {e['address']} Paris {arr}"
        maps_link = "https://www.google.com/maps/search/" + maps_query.replace(" ", "+").replace("&", "and")
        all_data.append({
            "arr": arr,
            "name": e["name"],
            "rating": e["rating"],
            "reviews": e["reviews"],
            "type": e["type"],
            "address": e["address"],
            "phone": e["phone"],
            "website": url if is_real_url else "",
            "maps": maps_link,
        })

print(f"Total entries: {len(all_data)}")
by_arr = {}
for d in all_data:
    by_arr.setdefault(d["arr"], 0)
    by_arr[d["arr"]] += 1
for a in sorted(by_arr):
    print(f"Arr {a}: {by_arr[a]}")

with open(os.path.join(BASE, "agences.json"), "w", encoding="utf-8") as f:
    json.dump(all_data, f, ensure_ascii=False, indent=2)

print("Saved to agences.json")
