<p align="center"><img width="1868" height="560" alt="Image" src="https://github.com/user-attachments/assets/a6bc6480-d0bd-4cab-bd0b-72e03e2b4580" /></p>
<div align="center"><a href="https://discord.gg/wsFFExCWFu"><img src="https://img.shields.io/discord/1073012182264066099" alt="Discord"></a></div>

## GBA Background Studio

**GBA Background Studio** adalah aplikasi desktop untuk membuat dan mengedit **latar belakang Game Boy Advance (GBA)**. Aplikasi ini memungkinkan konversi gambar menjadi tileset dan tilemap yang kompatibel dengan GBA, mengedit tile dan palet secara visual, serta mengekspor aset yang siap digunakan dalam proyek GBA Anda.

> ⚠️ Aplikasi ini dirancang untuk pengembang, ROM hacker, dan pixel artist yang membutuhkan kontrol presisi atas latar belakang GBA.

---

## 🌐 Terjemahan

README ini tersedia dalam bahasa-bahasa berikut:

<p align="center">
  <a href="README.md">English</a> | <a href="README.spa.md">Español</a> | <a href="README.brp.md">Português (BR)</a> | <a href="README.fra.md">Français</a> | <a href="README.deu.md">Deutsch</a> | <a href="README.ita.md">Italiano</a> | <a href="README.por.md">Português</a> | <a href="README.nld.md">Nederlands</a> | <a href="README.pol.md">Polski</a><br>
  <a href="README.tur.md">Türkçe</a> | <a href="README.vie.md">Tiếng Việt</a> | <a href="README.ind.md">Bahasa Indonesia</a> | <a href="README.hin.md">हिन्दी</a> | <a href="README.rus.md">Русский</a> | <a href="README.jap.md">日本語</a> | <a href="README.zhs.md">简体中文</a> | <a href="README.zht.md">繁體中文</a> | <a href="README.kor.md">한국어</a>
</p>

---

## ✨ Fitur

- **Konversi Gambar ke GBA**
  - Mengonversi gambar standar menjadi tileset dan tilemap yang kompatibel dengan GBA.
  - Mengonfigurasi ukuran output dan kedalaman warna (4bpp dan 8bpp).
  - Pratinjau hasil sebelum mengekspor.

- **Pengeditan Tileset**
  - Pemilihan dan pengeditan tile secara visual.
  - Alat gambar interaktif pada kisi tilemap.
  - Tingkat zoom dari 100% hingga 800% untuk pengeditan piksel per piksel.

- **Pengeditan Palet**
  - Mengedit hingga 256 warna per palet.
  - Menyinkronkan perubahan palet dengan pratinjau dan tile.
  - Mengatur ulang, mengganti, atau menyesuaikan warna individual.

- **Tab Pratinjau**
  - Memvisualisasikan tampilan latar belakang akhir pada layar mirip GBA.
  - Memvalidasi konfigurasi tile dan palet dengan cepat.

- **Riwayat Batalkan/Ulangi**
  - Pelacakan riwayat pengeditan secara lengkap.
  - Operasi batalkan dan ulangi dengan buffer riwayat yang luas.

- **Antarmuka dan bilah status yang dapat dikonfigurasi**
  - Bilah status terperinci dengan pemilihan tile, koordinat tilemap, ID palet, status balik, dan tingkat zoom.
  - Bilah alat kontekstual per tab (pratinjau, tile, palet).

- **Dukungan multibahasa**
  - Sistem terjemahan internal (Translator) dengan pemilihan bahasa melalui pengaturan.
  - Dirancang untuk mendukung beberapa bahasa dalam antarmuka.

---

## 🖼️ Tangkapan Layar

<p align="center"><img width="896" height="590" alt="Image" src="https://github.com/user-attachments/assets/e4c7b9f7-59dd-4640-8ce7-b5ec8331cdbd" /></p>

<p align="center"><img width="849" height="676" alt="Image" src="https://github.com/user-attachments/assets/83460fa2-048d-4a87-8349-b6cb2b4bc708" /></p>

<p align="center"><img width="849" height="676" alt="Image" src="https://github.com/user-attachments/assets/ae55d367-37fd-4417-9c22-e44c8404c578" /></p>

<p align="center"><img width="849" height="676" alt="Image" src="https://github.com/user-attachments/assets/033fb7c5-ccac-4384-8530-9bba4b0fd71f" /></p>

---

## 🏗️ Deskripsi Arsitektur

GBA Background Studio dibangun dengan **Python** dan **PySide6**, mengikuti desain antarmuka modular:

- **Jendela utama (`GBABackgroundStudio`)**
  - Mengelola status aplikasi (BPP saat ini, tingkat zoom, pemilihan tile dan palet).
  - Menampung tab utama dan bilah status kustom.
  - Memuat dan menerapkan konfigurasi (termasuk sesi output terakhir).

- **Tab**
  - `PreviewTab` – Pratinjau latar belakang bergaya GBA.
  - `EditTilesTab` – Alat pengeditan tile dan tilemap.
  - `EditPalettesTab` – Editor palet dan alat manipulasi warna.

- **Komponen dan utilitas antarmuka**
  - `MenuBar` – Operasi file (buka gambar, ekspor file, keluar) dan tindakan editor.
  - `CustomGraphicsView` – `QGraphicsView` yang diperluas dengan interaksi berbasis tile.
  - `TilemapUtils` – Logika bersama untuk interaksi dan pemilihan tilemap.
  - `HistoryManager` – Manajemen batalkan/ulangi untuk operasi editor.
  - `HoverManager`, `GridManager` – Bantuan visual untuk efek hover dan overlay kisi.
  - `Translator`, `ConfigManager` – Lokalisasi dan konfigurasi persisten.

---

## 📦 Instalasi

### Persyaratan
- **Python** (Direkomendasikan 3.12+)
- **Pip** (Pengelola paket Python)
- **Dukungan Sistem Operasi untuk PySide6:**
  - **Windows:** Windows 10 (Versi 1809) atau yang lebih baru.
  - **macOS:** macOS 11 (Big Sur) atau yang lebih baru.
  - **Linux:** Distribusi modern dengan glibc 2.28 atau yang lebih baru.

### Dependensi
Dependensi utama meliputi:
- `PySide6` (Qt untuk Python) - *Catatan: Membutuhkan versi OS yang disebutkan di atas.*
- `Pillow` (PIL) untuk pemrosesan gambar.

Anda dapat menginstal dependensi menggunakan:
```bash
pip install -r requirements.txt
```

---

### 🏛️ Dukungan OS Legacy (Windows 7 / 8 / 8.1)
Jika Anda menggunakan versi Windows lama yang tidak mendukung **PySide6** (framework GUI), Anda tetap bisa menggunakan mesin konversi melalui **Wizard Baris Perintah Multibahasa** kami.

Anda dapat menginstal dependensi legacy menggunakan:
```bash
pip install -r requirements-legacy.txt
```

Ini memungkinkan Anda untuk mengonversi gambar ke aset GBA tanpa antarmuka grafis, menggunakan asisten langkah-demi-langkah dalam bahasa lokal Anda.

1. Buka direktori utama proyek.
2. Jalankan file **`GBA_Studio_Wizard.bat`**.
3. Pilih bahasa Anda (mendukung 18 bahasa).
4. Ikuti instruksi untuk menyeret gambar dan mengonfigurasi output GBA.

---

## 🚀 Memulai

1. **Klon repositori**

   ```bash
   git clone https://github.com/CompuMaxx/gba-background-studio.git
   cd gba-background-studio
   ```

2. **Buat dan aktifkan lingkungan virtual** (opsional tetapi direkomendasikan)

   ```bash
   python -m venv .venv
   source .venv/bin/activate   # Di Windows: .venv\Scripts\activate
   ```

3. **Instal dependensi**

   ```bash
   pip install -r requirements.txt
   ```

4. **Jalankan aplikasi**

   ```bash
   python main.py
   ```

---

## 🧭 Penggunaan Dasar

1. **Membuka Gambar**
   - Pergi ke **Berkas → Buka Gambar** atau tekan `Ctrl+O`.
   - Pilih gambar yang ingin Anda konversi menjadi latar belakang GBA.

2. **Mengonfigurasi Konversi**
   - Pilih **Mode BG** (**Mode Teks** atau **Rotasi/Skala**).
   - Pilih palet atau Tilemap yang akan digunakan (hanya untuk **Mode Teks 4bpp**).
   - Tetapkan warna yang akan digunakan sebagai transparan.
   - Sesuaikan ukuran output dan parameter lain yang diperlukan.
   - Klik **Konversi** dan aplikasi akan menangani sisanya.

3. **Ubah Tile**
   - Beralih ke tab **Ubah Tile**.
   - Gunakan tampilan tilemap untuk menggambar dan memodifikasi tile individual.
   - Pilih area lengkap untuk menyalin, memotong, menempel, atau memutar kelompok tile.
   - Sinkronkan perubahan secara real-time untuk melihat hasil instan.
   - Sesuaikan tingkat **Zoom** untuk presisi sempurna.
   - Optimalkan atau Deoptimalkan Tile untuk menghemat ruang atau memastikan kompatibilitas perangkat keras.
   - Konversi aset antara format **4bpp** dan **8bpp**.
   - Beralih antara **Mode Teks** dan **Rotasi/Skala** dengan mulus.

4. **Ubah Palet**
   - Pergi ke tab **Ubah Palet**.
   - Modifikasi warna dalam kisi palet dan sesuaikan dengan editor warna.
   - Pilih area tertentu atau semua tile yang termasuk dalam palet untuk menggantinya atau menukarnya dengan yang lain.

5. **Pratinjau Latar Belakang**
   - Beralih ke tab **Pratinjau** untuk representasi setia tentang tampilan di GBA nyata.
   - Verifikasi bahwa konfigurasi tile dan palet Anda bekerja dengan sempurna bersama.

6. **Ekspor Aset**
   - Pergi ke **Berkas → Ekspor Berkas** atau tekan `Ctrl+E`.
   - Ekspor tileset, tilemap, dan palet dalam format yang siap diintegrasikan ke dalam rantai alat pengembangan GBA Anda.
   - Ekspor aset individual secara terpisah dari menu masing-masing jika diperlukan.

---

## 🔄 Batalkan/Ulangi

Aplikasi melacak tindakan pengeditan Anda menggunakan **manajer riwayat**:

- **Batalkan** – mengembalikan operasi terakhir.
- **Ulangi** – menerapkan kembali operasi yang dibatalkan.

Sistem riwayat mempertahankan buffer status terkini, termasuk pengeditan tile, perubahan palet, dan operasi tilemap.

---

## ⚙️ Konfigurasi dan Lokalisasi

### Konfigurasi

Aplikasi menggunakan manajer konfigurasi untuk menyimpan pengaturan seperti:

- Bahasa terakhir yang digunakan
- Tingkat zoom terakhir yang digunakan
- Apakah akan memuat output terakhir saat memulai
- Preferensi antarmuka dan editor lainnya

Konfigurasi dimuat saat memulai dan diterapkan ke antarmuka dan menu.

### Lokalisasi

Komponen `Translator` mengelola teks antarmuka:

- Bahasa default dikonfigurasi melalui pengaturan.
- File terjemahan dapat ditambahkan atau diedit untuk mendukung lebih banyak bahasa.
- Teks antarmuka (menu, dialog, label) melewati penerjemah.

---

## 🤝 Berkontribusi

Kontribusi sangat disambut! Jika Anda ingin membantu:

1. Fork repositori ini.
2. Buat branch fitur:
   ```bash
   git checkout -b feature/fitur-baru-saya
   ```
3. Commit perubahan Anda:
   ```bash
   git commit -am "Menambahkan fitur baru saya"
   ```
4. Push branch:
   ```bash
   git push origin feature/fitur-baru-saya
   ```
5. Buka Pull Request yang menjelaskan perubahan Anda.

Harap jaga konsistensi kode Anda dengan gaya yang ada dan sertakan pengujian jika memungkinkan.

---

## 📄 Lisensi

Proyek ini dilisensikan di bawah **GNU General Public License v3.0 (GPL-3.0)**.  
Lihat file [LICENSE](LICENSE) untuk detail lebih lanjut.

---

## 🙏 Ucapan Terima Kasih

- Terima kasih kepada komunitas homebrew dan ROM hacking GBA atas dokumentasi dan alat mereka.
- Terinspirasi oleh editor pixel art klasik dan utilitas pengembangan GBA.

---

## 📩 Kontak dan Dukungan

<p align="left">
  <a href="https://discord.gg/wsFFExCWFu">
    <img src="https://img.shields.io/badge/Discord-5865F2?style=for-the-badge&logo=discord&logoColor=white" alt="Discord Server" /><img src="https://img.shields.io/badge/CompuMax_Dev's-gray?style=for-the-badge" alt="Join our Discord" />
  </a>
</p>

Jika Anda merasa alat ini berguna dan ingin mendukung pengembangannya, pertimbangkan untuk mentraktir saya kopi!

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/compumax)

---
