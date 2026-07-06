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


def extract_author(name):
    """Ekstrak penulis dari filename. Return (title_cleaned, author)"""
    title = name.rsplit('.', 1)[0]
    author = None
    
    # " - Author Name" (hindari eBookWave dll)
    m = re.search(r'\s+[-–]\s+([A-Z][a-zà-ü]+(?:\s+[A-Z][a-zà-ü]*)*)\s*$', title)
    if m:
        cand = m.group(1).strip()
        if cand.lower() not in ('ebookwave', 'brr', 'mb', 'o', 'id', 'eng', 'bm'):
            author = cand
            title = title[:m.start()]
    
    # "(Author Name)" di akhir
    if not author:
        m = re.search(r'\s*\(([A-Z][A-Za-zà-ü\s.]+)\)\s*$', title)
        if m:
            cand = m.group(1).strip()
            # Filter kode pendek atau yang jelas bukan nama
            if len(cand) > 4 and not re.match(r'^[A-Z\s]+$', cand):
                author = cand
                title = title[:m.start()]
    
    # "by Author Name" di akhir
    if not author:
        m = re.search(r'\s+by\s+(.+)$', title)
        if m:
            author = m.group(1).strip()
            title = title[:m.start()]
    
    # " - Pengarang" atau "oleh" pattern
    if not author:
        m = re.search(r'\s+oleh\s+(.+)$', title, re.IGNORECASE)
        if m:
            author = m.group(1).strip()
            title = title[:m.start()]
    
    return title.strip(), author


def gen_desc(cats, title):
    """Generate short description based on categories"""
    desc_map = {
        'Memasak & Resep': 'Buku ini berisi berbagai resep dan panduan memasak.',
        'Parenting & Anak': 'Panduan parenting, tumbuh kembang, dan perawatan anak.',
        'Bisnis & Keuangan': 'Wawasan seputar bisnis, marketing, dan keuangan pribadi.',
        'Psikologi & Self-Help': 'Buku pengembangan diri, psikologi, dan kesehatan mental.',
        'Islam & Spiritual': 'Buku keislaman, spiritualitas, dan penguatan iman.',
        'Psikotes & Bahasa': 'Buku latihan psikotes, CPNS, TOEFL, dan pembelajaran bahasa.',
        'Novel & Fiksi': 'Karya fiksi dan novel dari berbagai genre.',
        'Pendidikan & Sekolah': 'Buku pelajaran, kurikulum, dan referensi pendidikan.',
        'Menjahit & Busana': 'Panduan menjahit, pola busana, dan desain pakaian.',
        'Pengembangan Diri': 'Buku motivasi, keterampilan diri, dan pengembangan potensi.',
        'Kesehatan & Kecantikan': 'Tips kesehatan, kecantikan, diet, dan gaya hidup sehat.',
    }
    for cat in cats:
        if cat in desc_map:
            return desc_map[cat]
    return f'Buku dengan kategori {", ".join(cats)}.'

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
    
    # Extract author BEFORE cleaning title
    pre_name, author = extract_author(name)
    
    # Clean title (dari versi yang sudah dihilangkan penulisnya)
    display_name = clean_title(pre_name)
    if len(display_name) < 3:
        display_name = clean_title(name)
    
    # Categories
    categories = determine_categories(name_lower)
    
    # Description
    desc = gen_desc(categories, display_name)
    
    books.append({
        "id": f.id,
        "name": display_name,
        "author": author or "",
        "desc": desc,
        "file": name,
        "ext": ext,
        "thumb": thumb,
        "categories": categories
    })

# ─── Deduplicate ───
seen = {}
for b in books:
    key = re.sub(r'[^a-z0-9]', '', b['name'].lower())
    if key not in seen:
        seen[key] = b
        continue
    # Duplicate — pick the better one
    cur = seen[key]
    cur_bad = 0
    new_bad = 0
    for s in [(b['file'], b), (cur['file'], cur)]:
        f = s[0].lower()
        bad = 0
        if '(1).pdf' in f: bad += 2
        if 'ebookwave' in f: bad += 1
        if '[brr]' in f or '[mb]' in f or '[o]' in f: bad += 1
        if s[1] is b: new_bad = bad
        else: cur_bad = bad
    if new_bad < cur_bad:
        seen[key] = b
books = list(seen.values())

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
