import requests
import xml.etree.ElementTree as ET
from email.utils import format_datetime
from datetime import datetime
import subprocess

OUTFILE='docs/staalhard.rss'

ORG_ID = "c292b3ac-094e-4616-a956-a99800ed54e9"
PLAYLIST_ID = "956c60cc-9967-4621-9df9-ac2900f96ed2"

API_URL = f"https://omny.fm/api/orgs/{ORG_ID}/playlists/{PLAYLIST_ID}/clips"


def fetch_clips(limit=100):
    params = {
        "per_page": limit
    }

    r = requests.get(API_URL, params=params)
    r.raise_for_status()
    data = r.json()

    return data.get("Clips", [])


def iso_to_rfc2822(date_str):
    dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
    return format_datetime(dt)


def build_rss(clips):
    rss = ET.Element("rss", {
        "version": "2.0",
        "xmlns:itunes": "http://www.itunes.com/dtds/podcast-1.0.dtd"
    })

    channel = ET.SubElement(rss, "channel")

    # Channel metadata
    ET.SubElement(channel, "title").text = "Staalhard"
    ET.SubElement(channel, "link").text = "https://www.willy.radio/programmas/staalhard"
    ET.SubElement(channel, "description").text = "Staalhard episodes"
    ET.SubElement(channel, "language").text = "nl-be"

    # Channel image (use first episode image)
    if clips:
        image_url = clips[0]["ImageUrl"].split("?")[0]

        image = ET.SubElement(channel, "image")
        ET.SubElement(image, "url").text = image_url
        ET.SubElement(image, "title").text = "Staalhard"
        ET.SubElement(image, "link").text = "https://www.willy.radio/programmas/staalhard"

        # iTunes-specific image
        itunes_image = ET.SubElement(channel, "itunes:image")
        itunes_image.set("href", image_url)

    for clip in clips:
        item = ET.SubElement(channel, "item")

        title = clip["Title"]
        audio_url = clip["AudioUrl"].split("?")[0]
        pub_date = iso_to_rfc2822(clip["PublishedUtc"])
        guid = clip["Id"]
        image_url = clip["ImageUrl"].split("?")[0]

        ET.SubElement(item, "title").text = title
        ET.SubElement(item, "guid").text = guid
        ET.SubElement(item, "pubDate").text = pub_date
        ET.SubElement(item, "link").text = clip["PublishedUrl"]

        enclosure = ET.SubElement(item, "enclosure")
        enclosure.set("url", audio_url)
        enclosure.set("type", "audio/mpeg")

        # Episode image (important for Apple Podcasts)
        itunes_image = ET.SubElement(item, "itunes:image")
        itunes_image.set("href", image_url)

        if clip.get("Description"):
            ET.SubElement(item, "description").text = clip["Description"]

    return rss


def save_rss(tree, filename=OUTFILE):
    ET.indent(tree, space="  ", level=0)
    tree.write(filename, encoding="utf-8", xml_declaration=True)



if __name__ == "__main__":
    clips = fetch_clips(100)
    rss = build_rss(clips)

    tree = ET.ElementTree(rss)
    save_rss(tree)

    print(f"RSS feed created with {len(clips)} episodes.")
