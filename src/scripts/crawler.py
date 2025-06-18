import json
import requests
from bs4 import BeautifulSoup
import os
from urllib.parse import urljoin
import re


def crawl_person(url, career, save_dir="images"):
  external_id = url.split('/')[-1]

  sub_folders = [name.split('_')[0] for name in os.listdir(save_dir) if os.path.isdir(os.path.join(save_dir, name))]
  if external_id in sub_folders:
      print(f"Skipping crawl for {url} as data already exists.")
      return


  headers = {
      "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
                    " AppleWebKit/537.36 (KHTML, like Gecko)"
                    " Chrome/114.0 Safari/537.36"
  }
  resp = requests.get(url, headers=headers)
  resp.raise_for_status()
  
  soup = BeautifulSoup(resp.content, "html.parser")



  save_dir = os.path.join(save_dir, external_id + '_' + info['name'].replace(' ', '_'))
  # tạo thư mục lưu ảnh nếu chưa có
  os.makedirs(save_dir, exist_ok=True)
  
  # ---- 1. Crawl thông tin cơ bản ----
  info = {}
  # Ví dụ: tên, ngày sinh, nơi sinh - tùy theo cấu trúc page cụ thể
  # Cập nhật đúng selector theo HTML trang
  info_section = soup.find('div', {'class': 'motangan'})
  if (info_section is None):
      print("Khong tim thay thong tin " + url)
      return
      
  try:
    info['name'] = info_section.find('h2').text
  except Exception as e:
    info['name'] = None

  try:
    info['address'] = info_section.find('p', title=True).text.split(': ')[1]
  except Exception as e:
    info['address'] = None
  
  try:
    info['birthdate'] = info_section.find('a', href=True).text + info_section.find('a', href=True).next_sibling.strip().split(' ')[0]
  except Exception as e:
    info['birthdate'] = None
  
  try:
    info['facebook'] = info_section.find('a', href=True, class_='fbl')['href']
  except Exception as e:
    info['facebook'] = None
  
  try:
    info['email'] = info_section.find('b', string=re.compile(r'Email:')).next_sibling.text
  except Exception as e:
    info['email'] = None
  
  try:
    info['phone_number'] = info_section.find('b', string=re.compile(r'Số điện thoại: ')).next_sibling.text
  except Exception as e:
    info['phone_number'] = None
  info['ref'] = url
  info['career'] = career


  # lưu thông tin vào file info.json trong folder
  with open(os.path.join(save_dir, 'info.json'), 'w', encoding='utf-8') as f:
    json.dump(info, f, ensure_ascii=False, indent=4)

  # ---- 2. Crawl hình ảnh chính ----
  images = []
  # Ví dụ: ảnh đại diện, ảnh nổi bật
  images = soup.find_all('img', {'src': re.compile(r'/images/nnt/')})
  images = list(map(lambda x: 'https://nguoinoitieng.tv' + x['src'], images))
  images = list(dict.fromkeys(images))
  
  # ---- 3. Tải ảnh về local ----
  for idx, img_url in enumerate(images):
      local_path = os.path.join(save_dir, str(idx) + '.jpg')
      try:
          img_resp = requests.get(img_url, headers=headers, stream=True)
          img_resp.raise_for_status()
          with open(local_path, "wb") as f:
              for chunk in img_resp.iter_content(1024):
                  f.write(chunk)
          print(f"Saved image: {local_path}")
      except Exception as e:
          print(f"Failed to download {img_url}: {e}")
  
  # ---- 4. In hoặc trả dữ liệu ----
  print("\n--- Thông tin cơ bản ---")
  for k, v in info.items():
      print(f"{k}: {v}")
  print("\n--- Danh sách ảnh đã tải ---")
  for p in os.listdir(save_dir):
      print(f"- {p}")
  
  # Trả về cấu trúc nếu cần dùng ở nơi khác
  return info, images

def crawl_page(url, page = 1):
  print(f"Crawling page {page} of {url}")
  headers = {
      "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
                    " AppleWebKit/537.36 (KHTML, like Gecko)"
                    " Chrome/114.0 Safari/537.36"
  }

  page_url = url + f"/page{page}"
  resp = requests.get(page_url, headers=headers)
  resp.raise_for_status()

  soup = BeautifulSoup(resp.content, "html.parser")
  
  people_section = soup.find('div', {'class': 'list-ngaymai'})
  people = people_section.find_all('a', href=True)

  people = list(map(lambda x: urljoin(url, x['href']), people))
  people = [person for person in people if 'nghe-nghiep' in person]
  people = list(dict.fromkeys(people))

  return people

def crawl_all():
    base_url = "https://nguoinoitieng.tv/nghe-nghiep/"

    careers = {
        "dien-vien": 105,
        "nguoi-mau": {"from": 119, "to": 193},
        "hot-girl": 84,
        "ca-si": {"from": 38, "to": 188},
    }

    for career, page_count in careers.items():
        page_count_from = 1
        page_count_to = page_count
        if isinstance(page_count, dict) and 'from' in page_count and 'to' in page_count:
            page_count_from = page_count['from']
            page_count_to = page_count['to']
        for page in range(page_count_from, page_count_to + 1):
            people = crawl_page(base_url + career, page)
            for person in people:
                crawl_person(person,career, "images" )

def crawl_best():
    base_url = "https://nguoinoitieng.tv/nghe-nghiep/"

    careers = {
        "dien-vien": 20,
        "nguoi-mau": 20,
        "hot-girl": 20,
        "ca-si": 20,
    }

    best_people_folder: list = []
    exists_folder: list = os.listdir("images")

    for career, page_count in careers.items():
        page_count_from = 1
        page_count_to = page_count
        if isinstance(page_count, dict) and 'from' in page_count and 'to' in page_count:
            page_count_from = page_count['from']
            page_count_to = page_count['to']
        for page in range(page_count_from, page_count_to + 1):
            people = crawl_page(base_url + career, page)
            for person in people:
                external_id = person.split('/')[-1]
                best_people_folder.append(next((folder for folder in exists_folder if folder.split('_')[0] == external_id), None))


    # Save the best_people_folder list as a JSON file
    with open('best_people_folder.json', 'w', encoding='utf-8') as f:
        json.dump(best_people_folder, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
  # crawl_best()
  print(len(os.listdir("images")))