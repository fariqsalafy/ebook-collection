import gdown
import json
import re

folder_id = '1_fFMqj47iydyqS6JlqzaekL_a8rD9D-S'

files = gdown.download_folder(
    id=folder_id,
    quiet=True,
    skip_download=True
)

print(f"Total files: {len(files)}")

books = []
for f in files:
    name = f.path
    ext = name.split('.')[-1].lower() if '.' in name else ''
    
    # View link
    view_url = f"https://drive.google.com/file/d/{f.id}/view"
    
    # Determine category from filename
    name_lower = name.lower()
    
    categories = []
    
    # Cooking / Resep
    if any(kw in name_lower for kw in ['resep', 'masakan', 'makanan', 'kue', 'cake', 
        'cooking', 'baking', 'frozen food', 'dapur', 'masak', 'menu', 'goreng',
        'tumisan', 'chinese food', 'ayam pop', 'sambal', 'saus', 'kukus',
        'snack', 'dessert', 'cookies', 'kopi', 'diet']):
        categories.append('Memasak & Resep')
    
    # Parenting / Anak / Bayi
    if any(kw in name_lower for kw in ['parenting', 'mpasi', 'bayi', 'batita', 'balita',
        'anak', 'menyusui', 'asi', 'hamil', 'melahirkan', 'montessori', 'baby',
        'gentle birth', 'mother', 'mommy', 'buku pintar', 'panduan merawat']):
        categories.append('Parenting & Anak')
    
    # Bisnis / Marketing / Keuangan
    if any(kw in name_lower for kw in ['bisnis', 'bisnis', 'marketing', 'keuangan', 'jualan',
        'uang', 'kaya', 'closing', 'mlm', 'shopee', 'money', 'magnet rezeki',
        'investing', 'rich dad', 'bisnis', 'bisnis', 'profit']):
        categories.append('Bisnis & Keuangan')
    
    # Psikologi / Self-Help
    if any(kw in name_lower for kw in ['psikologi', 'psikotes', 'psikotest', 'berpikir',
        'mindset', 'habbit', 'habit', 'atomic habits', 'mind', 'self',
        'depresi', 'cemasan', 'healing', 'emotional', 'berpikir', 'bodo amat',
        'filosofi', 'stoic', 'mindset therapy', 'berdamai', 'berani',
        'kebahagiaan', 'bahagia', 'gak sendiri', 'keren']):
        categories.append('Psikologi & Self-Help')
    
    # Islam / Spiritual
    if any(kw in name_lower for kw in ['islam', 'allah', 'rasulullah', 'nabi', 'qur\'an',
        'quran', 'zikir', 'doa', 'ibadah', 'sirah', 'islamic', 'secrets of divine',
        'aqidah', 'akhlak', 'tahajud', 'duha', 'berkah', 'syukur',
        'kitab', 'firasat', 'vibrasi', 'ulumul']):
        categories.append('Islam & Spiritual')
    
    # Psikotes / CPNS / Sekolah
    if any(kw in name_lower for kw in ['psikotes', 'cpns', 'bumn', 'toefl', 'ielts',
        'psikotest', 'grammar', 'bahasa inggris', 'vocabulary', 'psikologi',
        'tes', 'tpa']):
        categories.append('Psikotes & Bahasa')
    
    # Novel / Fiksi
    if any(kw in name_lower for kw in ['novel', 'fiksi', 'cerita', 'funiculi',
        'toko kelontong', 'namiya', 'midnight library', 'harry potter',
        'pangeran cilik', 'alchemis', 'sang alkemis', 'gadis kretek',
        'laut bercerita', 'cantik itu luka', 'it ends with us',
        'summer in seoul', 'dunia sophie', 'sekolah kebaikan', 'hujan']):
        categories.append('Novel & Fiksi')
    
    # Sekolah / Pendidikan
    if any(kw in name_lower for kw in ['-bg-', '-bs-', 'kelas ', 'ppip_kelas',
        'pendidikan', 'informatika', 'ipa-bg', 'ipa-bs', 'ips-bg', 'ips-bs',
        'bahasa indonesia', 'belajar men', 'makhfudzot', 'guru']):
        categories.append('Pendidikan & Sekolah')
    
    # Menjahit
    if any(kw in name_lower for kw in ['menjahit', 'pola busana', 'tailoring',
        'busana', 'pola', 'soekarno']):
        categories.append('Menjahit & Busana')
    
    # Pengembangan Diri
    if any(kw in name_lower for kw in ['mindset', 'atomic', 'habit', 'power of',
        'psychology of money', 'thinking', 'how to', 'seni', 'bicara',
        'rahasia', 'inspirasi', 'motivasi', 'chicken soup', 'berpikir',
        'leadership', 'kepemimpinan', 'public speaking', 'komunikasi',
        'rahasia', 'sukses', 'kekuatan', 'berubah', 'mulai']):
        categories.append('Pengembangan Diri')
    
    # Kesehatan
    if any(kw in name_lower for kw in ['kesehatan', 'diet', 'sehat', 'fitness',
        'skincare', 'kurus', 'langsing', 'gemuk', 'kanker']):
        categories.append('Kesehatan & Kecantikan')
    
    # If no category matched, put in Umum
    if not categories:
        categories.append('Umum')
    
    # Remove duplicates while preserving order
    seen = set()
    categories_unique = []
    for c in categories:
        if c not in seen:
            seen.add(c)
            categories_unique.append(c)
    
    book = {
        "id": f.id,
        "name": name,
        "ext": ext,
        "url": view_url,
        "categories": categories_unique
    }
    books.append(book)

# Sort by name
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
