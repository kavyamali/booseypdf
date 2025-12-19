import os
import sys
import re
import requests
import img2pdf
import argparse
from tqdm import tqdm
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs

def sanitize_filename(name):
    name=re.sub(r'[<>:"/\\|?*]','',name)
    return name.replace(' ','_')

def get_resolution_choice():
    print("\nSelect Quality:")
    print("1. Low (_1)")
    print("2. Standard (_2)")
    print("3. High (_3)")
    print("4. Max (_4)")
    choice=input("Choose (1-4) [default is 3]: ").strip()
    return{'1':'_1','2':'_2','3':'_3','4':'_4'}.get(choice,'_3')

def get_page_range(detected_end=None):
    print("\nPage Range:")
    start=input("Start Page [default is 1]: ").strip()
    start=int(start) if start.isdigit() else 1
    default_end=detected_end if detected_end else "Manual Input"
    end=input(f"End Page [detected: {default_end}]: ").strip()
    if not end and detected_end:end=detected_end
    elif not end and not detected_end:
        print("Error: You must specify an end page.");sys.exit(1)
    return start,int(end)

def parse_local_html(file_path):
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' not found.")
        print("Did you save the webpage as '*filename*.html'?")
        return None,None,None,None
    print(f"Parsing: {file_path}")
    with open(file_path,"rb") as f:
        raw=f.read()
    try:
        html=raw.decode("utf-8")
    except UnicodeDecodeError:
        html=raw.decode("latin-1",errors="replace")
    soup=BeautifulSoup(html,'html.parser')
    try:
        raw_title=soup.find("h1",class_="page-header__title").text.strip()
        raw_composer=soup.find("div",class_="page-header__composer").text.strip()
        suggested_name=f"{sanitize_filename(raw_composer)}-{sanitize_filename(raw_title)}.pdf"
    except AttributeError:
        suggested_name="Score.pdf"
    embed_link=soup.find("a",class_="fbp-embed")
    if not embed_link:
        match=re.search(r"uid=([a-f0-9\-]+)&asset=([a-zA-Z0-9_]+)",html)
        if match:return match.group(1),match.group(2),None,suggested_name
        return None,None,None,None
    params=parse_qs(urlparse(embed_link.get('href')).query)
    uid=params.get('uid',[None])[0]
    asset=params.get('asset',[None])[0]
    pages=params.get('pages',[None])[0]
    return uid,asset,int(pages) if pages else None,suggested_name

def download_and_stitch(asset_id,token,start,end,resolution,output_file):
    base_url=f"https://scoreserver.boosey.com/api/image/get/{asset_id}"
    headers={"Referer":"https://boosey.com/","User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    temp_dir="downloads_temp";os.makedirs(temp_dir,exist_ok=True)
    images=[]
    print(f"\nDownloading Pages {start} to {end} (Quality: {resolution})")
    for i in tqdm(range(start,end+1)):
        page=f"{i:04d}"
        filename=os.path.join(temp_dir,f"page_{page}.jpg")
        url=f"{base_url}/page{page}{resolution}.jpg?uni={token}"
        try:
            r=requests.get(url,headers=headers,stream=True)
            if r.status_code==404 and resolution!="_2":
                r=requests.get(url.replace(resolution,"_2"),headers=headers,stream=True)
            if r.status_code==200:
                with open(filename,'wb') as f:
                    for c in r.iter_content(1024):f.write(c)
                images.append(filename)
            elif r.status_code==403:
                print("\nError: The token in source.html has expired.")
                print("Refresh the page in your browser and re-save the html.")
                break
        except Exception:pass
    if images:
        print(f"Building PDF: '{output_file}'...")
        images.sort()
        try:
            with open(output_file,"wb") as f:f.write(img2pdf.convert(images))
            print(f"Success! Saved to: {output_file}")
            for img in images:os.remove(img)
            os.rmdir(temp_dir)
        except Exception as e:print(f"PDF Error: {e}")
    else:print("No images downloaded.")

if __name__=="__main__":
    p=argparse.ArgumentParser(description="Boosey Local Parser")
    p.add_argument("file",nargs="?",default="source.html")
    p.add_argument("--end",type=int)
    p.add_argument("--res")
    p.add_argument("--out")
    a=p.parse_args()
    uid,asset,pages,name=parse_local_html(a.file)
    if not uid or not asset:
        print("Failed to extract data.")
        print("Ensure you are logged in when you save the page!")
        sys.exit(1)
    print("\nScore Found!")
    print(f"    Asset ID: {asset[:10]}...")
    print(f"    Pages:    {pages}")
    print(f"    Title:    {name}")
    filename=a.out if a.out else name
    resolution=a.res if a.res else get_resolution_choice()
    start,end=(1,a.end) if a.end else get_page_range(pages)
    download_and_stitch(asset,uid,start,end,resolution,filename)
