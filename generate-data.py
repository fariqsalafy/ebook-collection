import gdown
import json
import re

folder_id = '1_fFMqj47iydyqS6JlqzaekL_a8rD9D-S'

files = gdown.download_folder(
    id=folder_id,
    quiet=True,
    skip_download=True
)

def clean_title(name):
    """ Bersihkan judul dari nomor urut, [kode], ebookwave, dll """
    # Hapus ekstensi
    title = name.rsplit('.', 1)[0]

    # Hapus pola "(1)" di akhir judul
    title = re.sub(r'\s*\(\d+\)\s*$', '', title)

    # Hapus " - eBookWave" di akhir
    title = re.sub(r'\s*[-–]\s*eBookWave$', '', title, flags=re.IGNORECASE)

    # Hapus "_Watermarked" dkk
    title = re.sub(r'_Watermarked', '', title, flags=re.IGNORECASE)
    title = re.sub(r'\s*z-lib\.org\s*\(SFILE\.MOBI\)', '', title, flags=re.IGNORECASE)
    title = re.sub(r'\s*\(SFILE\.MOBI\)', '', title, flags=re.IGNORECASE)

    # Bersihkan prefix "#N [KODE] ", "NNN. [KODE] ", "(kata) NNN. Judul"
    # Urutan penting: pola spesifik dulu baru generik
    
    # "#N [ID] Judul" atau "#N Judul"
    title = re.sub(r'^#[0-9]+\s*(\[.*?\]\s*)?', '', title)
    
    # "NNN. b.indo Judul" atau "NNN. b. indo Judul" (handle dulu sebelum NNN. saja)
    title = re.sub(r'^[0-9]+\.\s*b\.?\s*indo\s+', '', title, flags=re.IGNORECASE)
    
    # "NNN. [KODE] Judul"
    title = re.sub(r'^[0-9]+\.\s*\[.*?\]\s*', '', title)
    
    # "NNN. Judul" (angka saja diikuti titik)
    title = re.sub(r'^[0-9]+\.\s+', '', title)
    
    # "(kata) Judul" di awal
    title = re.sub(r'^\(.*?\)\s+', '', title)

    # "[KODE] Judul" di awal
    title = re.sub(r'^\[.*?\]\s+', '', title)

    # Hapus "by Author" di akhir
    title = re.sub(r'\s+by\s+[A-Z][^,]+$', '', title, flags=re.IGNORECASE)
    title = re.sub(r'\s+-\s+[A-Z][a-z]+\s+[A-Z][a-z]+$', '', title)  # - Dale Carnegie etc

    # Hapus " (Bahasa)" di akhir
    title = re.sub(r'\s*\(Bahasa\)\s*$', '', title)
    title = re.sub(r'\s*\(Indonesian Edition\)\s*$', '', title, flags=re.IGNORECASE)
    title = re.sub(r'\s*\(BM\)\s*$', '', title)

    # Hapus [BRR], [MB], [O] dll di awal  
    title = re.sub(r'^\[[A-Z]+[a-z]*\]\s*', '', title)

    # Hapus "B ind " di awal
    title = re.sub(r'^B\s+ind\s+', '', title, flags=re.IGNORECASE)

    # Hapus "Bahasa-Indonesia-" prefix dari buku sekolah
    title = re.sub(r'^(Bahasa-Indonesia|IPA|IPS|Informatika|Islam)-', r'\1 ', title)

    # Title case (kapitalisasi judul)
    # Skip untuk buku yang jelas punya judul resmi dengan huruf kapital

    # Bersihkan spasi berlebih
    title = re.sub(r'\s+', ' ', title).strip()
    title = re.sub(r'\s+\.$', '', title)  # trailing dot
    title = title.strip('-– ').strip()

    # Jika judul jadi terlalu pendek, gunakan nama file asli tanpa ekstensi
    if len(title) < 3:
        title = name.rsplit('.', 1)[0]

    return title


def determine_categories(name_lower):
    cats = []
    
    if any(kw in name_lower for kw in ['resep', 'masakan', 'makanan', 'kue', 'cake', 
        'cooking', 'baking', 'frozen food', 'dapur', 'masak', 'menu', 'goreng',
        'tumisan', 'chinese food', 'ayam pop', 'sambal', 'saus', 'kukus',
        'snack', 'dessert', 'kopi', 'diet', 'frozen']):
        cats.append('Memasak & Resep')

    if any(kw in name_lower for kw in ['parenting', 'mpasi', 'bayi', 'batita', 'balita',
        'menyusui', 'asi', 'hamil', 'melahirkan', 'montessori', 'baby',
        'gentle birth', 'mommy', 'panduan merawat']):
        cats.append('Parenting & Anak')

    if any(kw in name_lower for kw in ['bisnis', 'marketing', 'keuangan', 'jualan',
        'uang', 'kaya', 'closing', 'mlm', 'shopee', 'money', 'magnet rezeki',
        'investing', 'rich dad', 'profit', 'saham', 'bisnis']):
        cats.append('Bisnis & Keuangan')

    if any(kw in name_lower for kw in ['psikologi', 'psikotes', 'berpikir',
        'mindset', 'habit', 'atomic habits', 'self', 'depresi', 'cemasan',
        'healing', 'emotional', 'bodo amat', 'filosofi', 'stoic',
        'berdamai', 'berani', 'kebahagiaan', 'bahagia', 'mindset therapy']):
        cats.append('Psikologi & Self-Help')

    if any(kw in name_lower for kw in ['islam', 'allah', 'rasulullah', 'nabi', 'qur\'an',
        'quran', 'zikir', 'doa', 'ibadah', 'sirah', 'islamic', 'secrets of divine',
        'aqidah', 'akhlak', 'tahajud', 'duha', 'syukur', 'kitab', 'firasat',
        'vibrasi', 'ulumul', 'berkah']):
        cats.append('Islam & Spiritual')

    if any(kw in name_lower for kw in ['psikotes', 'cpns', 'bumn', 'toefl', 'ielts',
        'grammar', 'bahasa inggris', 'vocabulary', 'tes', 'tpa']):
        cats.append('Psikotes & Bahasa')

    if any(kw in name_lower for kw in ['novel', 'fiksi', 'funiculi', 'toko kelontong',
        'namiya', 'midnight library', 'harry potter', 'pangeran cilik',
        'alchemis', 'sang alkemis', 'gadis kretek', 'laut bercerita',
        'cantik itu luka', 'it ends with us', 'summer in seoul',
        'dunia sophie', 'sekolah kebaikan']):
        cats.append('Novel & Fiksi')

    if any(kw in name_lower for kw in ['-bg-', '-bs-', 'kelas ', 'ppip_kelas',
        'pendidikan', 'informatika', 'ipa-bg', 'ipa-bs', 'ips-bg', 'ips-bs',
        'bahasa indonesia', 'makhfudzot']):
        cats.append('Pendidikan & Sekolah')

    if any(kw in name_lower for kw in ['menjahit', 'pola busana', 'tailoring',
        'busana', 'pola', 'soekarno']):
        cats.append('Menjahit & Busana')

    if any(kw in name_lower for kw in ['seni', 'how to', 'public speaking', 'komunikasi',
        'rahasia', 'sukses', 'kekuatan', 'leadership', 'pemimpin']):
        cats.append('Pengembangan Diri')

    if any(kw in name_lower for kw in ['sehat', 'fitness', 'skincare', 'kurus',
        'langsing', 'kanker', 'diet']):
        cats.append('Kesehatan & Kecantikan')

    if not cats:
        cats.append('Umum')

    return list(dict.fromkeys(cats))  # unique, preserve order


print(f"Total files: {len(files)}")

books = []
for f in files:
    name = f.path
    ext = name.split('.')[-1].lower() if '.' in name else 'pdf'
    name_lower = name.lower()
    
    # Thumbnail
    thumb = f"https://drive.google.com/thumbnail?id={f.id}&sz=w400"
    
    # Clean title
    display_name = clean_title(name)
    
    # Categories
    categories = determine_categories(name_lower)
    
    books.append({
        "id": f.id,
        "name": display_name,
        "file": name,
        "ext": ext,
        "url": f"https://drive.google.com/file/d/{f.id}/view",
        "thumb": thumb,
        "categories": categories
    })

books.sort(key=lambda x: x['name'].lower())

output = {
    "folder_name": "E Book SovianaCSP",
    "folder_url": "https://drive.google.com/drive/folders/1_fFMqj47iydyqS6JlqzaekL_a8rD9D-S",
    "total": len(books),
    "books": books
}

with open('books.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"Written {len(books)} books to books.json")

# Count by category
cat_count = {}
for b in books:
    for c in b['categories']:
        cat_count[c] = cat_count.get(c, 0) + 1
print("\nCategory counts:")
for c, n in sorted(cat_count.items(), key=lambda x: -x[1]):
    print(f"  {c}: {n}")

# Sample titles to verify cleaning
print("\n=== SAMPLE TITLES (before → after) ===")
samples = [
    "#1 [ID] Belajar Menjahit untuk Pemula 1.pdf",
    "( workbook toefl) Check Your English Vocabulary for TOEFL by Rawdon Wyatt.pdf",
    "112. b.indo The things you can see only when you slow down (Bahasa).pdf",
    "433. [ID] Mindset - Mengubah Pola Berpikir Untuk Perubahan Besar Dalam Hidup Anda By Carol S Dweck.pdf",
    "[ID] Atomic Habits – James Clear.pdf",
    "800. [ID] Atomic Habits – James Clear.pdf",
    "Cantik itu luka (Eka Kurniawan).pdf",
    "Funiculi Funicula 2 - eBookWave.pdf",
    "Bahasa-Indonesia-BG-KLS-VII.pdf",
    "Buku Penuntun Membuat Pola Busana Tingkat Mahir - Soekarno.pdf",
]
for s in samples:
    print(f"  BEFORE: {s}")
    print(f"  AFTER:  {clean_title(s)}")
    print()
