###
### publish or update articles on yuque.com
###
### must-have file: .yuque_api_key
### only one line in this file:
### <app_id>=<personal access token>
### 
import requests
import argparse
import json
import os

class MarkdownDoc(object):
  slug_id_cache = dict()

  def __init__(self):
    self.id = None
    self.title = ""
    self.slug = ""
    self.content = "" 
    self.tags = []


def with_open(filename):
  doc = MarkdownDoc()
  # remove ".md" extension
  doc.title = filename[:-3]
  doc.slug = doc.title.replace(" ", "-")

  with open(filename) as f:
    """ 需要忽略 FRONT MATTER """
    front_matter_start = False
    front_matter_end = False
    non_empty_line_start = False
    for line in f:
      # ignore '---' start line
      if not front_matter_start and line.startswith("---"):
        front_matter_start = True
        continue
    
      # ignore '---' end line
      if not front_matter_end and line.startswith("---"):
        front_matter_end = True
        continue
    
      # ignore lines between
      if front_matter_start and not front_matter_end:
        if line.startswith("title"):
          doc.title = line.split(":")[1].strip()
        if line.startswith("tags"):
          doc.tags = [tag.strip() for tag in line.split(":")[1].strip().split(",")]
        continue
    
      # ignore first empty lines
      if not non_empty_line_start and len(line.strip()) > 0:
        non_empty_line_start = True
    
      if non_empty_line_start:
        doc.content += line
  
  # append the new line to the end of file
  if doc.content[-1] != "\n":
    doc.content += "\n"
  return doc

def yuque_create_or_update_doc(doc):
  global APP_ID
  global API_KEY

  api_service = "https://www.yuque.com/api/v2"
  op_url = f"{api_service}/repos/winterloo/db/docs"
  if doc.id:
    op_url += f"/{doc.id}"

  headers = {
    "Content-Type": "application/json",
    "User-Agent": APP_ID,
    "X-Auth-Token": API_KEY
  }

  payload = {
    "title": doc.title,
    "slug": doc.slug,
    "format": "markdown",
    "body": doc.content
  }

  if doc.id:
    r_response = requests.put(op_url, json=payload, headers=headers)
  else:
    r_response = requests.post(op_url, json=payload, headers=headers)

  if r_response.status_code != 200:
    print(r_response.content.decode())
    return

  jresp = json.loads(r_response.content.decode())
  doc_id = jresp["data"]["id"]
  doc_slug = jresp["data"]["slug"]
  doc_title = jresp["data"]["title"]
  doc_book_id = jresp["data"]["book_id"]

  op = "update" if doc.id else "create"
  print(f"""!!!----{op} doc {r_response.status_code}----!!!
doc id: {doc_id}
slug: {doc_slug}
title: {doc_title}
book_id: {doc_book_id}
""")

  if not doc.id:
    MarkdownDoc.slug_id_cache[doc_slug] = doc_id

def load_doc_id_cache():
  try:
    with open(".yuque_doc") as f:
      for line in f:
        if line.startswith("#"):
          continue
        slug, doc_id = line.strip().split(":")
        MarkdownDoc.slug_id_cache[slug.strip()] = doc_id.strip()
  except FileNotFoundError:
    pass

def save_doc_id_cache():
  with open(".yuque_doc", "w") as f:
    for slug, doc_id in MarkdownDoc.slug_id_cache.items():
      f.write(f"{slug}: {doc_id}\n")

def try_set_doc_id(doc):
  doc_id = MarkdownDoc.slug_id_cache.get(doc.slug)
  if doc_id:
    doc.id = doc_id

def load_api_key():
  with open(".yuque_api_key") as f:
    app_id, api_key = f.readline().strip().split("=")
    return (app_id, api_key)

APP_ID = None
API_KEY = None

def main():
  global APP_ID
  global API_KEY

  load_doc_id_cache()
  APP_ID, API_KEY = load_api_key()

  # list files in current directory
  filenames = os.listdir()
  for filename in filenames:
    if not filename.endswith(".md"):
      continue
    doc = with_open(filename)
    try_set_doc_id(doc)
    print(f"doc \"{filename}\"")
    yuque_create_or_update_doc(doc)

  save_doc_id_cache()
  
  
if __name__ == '__main__':
  main()
